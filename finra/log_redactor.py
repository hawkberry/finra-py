import json
import re
from collections import defaultdict
from logging import LogRecord, FileHandler, StreamHandler
from typing import Any, Callable, Optional

from httpx import Response, codes


__all__ = [
    "RedactFileHandler",
    "RedactStreamHandler",
    "register_redactions",
    "register_redactions_from_response",
    ]


# Class for building a global singleton for redacting secrets in logs
class _LogRedactor:
    """
    Collects strings that should not be emitted and replaces them with safe
    placeholders
    """
    
    def __init__(self):
        self.label_counts = defaultdict(int)
        self.__redacted_strings = {} # {string-to-redact: (label, count)}
        
    def register(self, s: Any, label: str) -> None:
        """
        Registers a string that should not be logged and its replacement label
        
        :param s:
        :param label:
        """
        if s is None: # ignore nulls
            return
        
        if not isinstance(s, str):
            s = f"{s}" # convert literals to strings
        elif not s.strip(): # ignore empty strings, all spaces
            return
        
        if s not in self.__redacted_strings:
            self.label_counts[label] += 1
            self.__redacted_strings[s] = (label, self.label_counts[label])
        
    # Regex substitution callback
    def __repl(self, m: re.Match) -> str:
        label, count = self.__redacted_strings[m.group(0)]
        return (
            f"<REDACTED {label}-{count}>"
            if self.label_counts[label] > 1
            else f"<REDACTED {label}>"
            )
    
    def redact(self, msg: str) -> str:
        """
        Scans the string for secret strings and returns a sanitized version
        with the secrets replaced with placeholders
        
        :param msg:
        """
        alts = "|".join([
            re.escape(t)
            for t in sorted(self.__redacted_strings, key=len, reverse=True)
            ]) # check longest strings first to avoid partial matches
        pattern = (
            rf'(?:(?<=[\{{\[:, "])(?:{alts})(?=[\}}\], "]))'
            rf"|(?:\A(?:{alts}))"
            rf"|(?:(?:{alts})\Z)"
            )
        try:
            return re.sub(pattern, self.__repl, msg)
        except KeyError:
            return msg


# Global singleton for redacting secrets in debug logs
_LOG_REDACTOR = _LogRedactor()


def _register_redactions(
    obj: Any,
    key_path: Optional[list[str]],
    bad_patterns: list[str],
    whitelist: list[str]
    ) -> None:
    if obj is None: # JSON nulls are not redacted
        return
    
    if key_path is None:
        key_path = []
    
    if isinstance(obj, list):
        for i, v in enumerate(obj):
            key_path.append(str(i))
            _register_redactions(v, key_path, bad_patterns, whitelist)
            key_path.pop()
        
    elif isinstance(obj, dict):
        key = obj["fieldName"] if "fieldName" in obj else None # Filter support
        for k, v in obj.items():
            if key is None:
                key_path.append(k)
            else: # redact Filter values using Filter field names
                key_path.append(key if k in ("fieldValue", "values") else k)
            _register_redactions(v, key_path, bad_patterns, whitelist)
            key_path.pop()
    elif key_path: # use last non-numeric key as name
        
        for k in reversed(key_path): # pragma: no cover
            try:
                int(k)
            except ValueError:
                break
        
        if k not in whitelist: # whitelist is case-sensitive
            last_key = k.casefold() # bad patterns is case-insensitive
            if any([bad in last_key for bad in bad_patterns]):
                _LOG_REDACTOR.register(obj, "-".join(key_path))


# Bad word stubs in lowercase, redact if they are part of any key
_BAD_PATTERNS = [
    "key",
    "secret",
    "token",
    "crd",
    "ssn",
    "dob",
    "dateofbirth",
    "identifier",
    "addressline",
    "firstname",
    "lastname",
    "middlename",
    "suffixname",
    "initiatorName",
    "occurrencenumber",
    "confirmationnumber",
    "docketnumber",
    "instanceNumber",
    "userid",
    "resultLink",
    ]


# Whitelisted terms in lowercase, to never redact
_WHITELIST = [
    "token_type",
    "tierIdentifier",
    "issueSymbolIdentifier",
    "securitiesInformationProcessorSymbolIdentifier",
    ]


def register_redactions(
    obj: Any,
    key_path: Optional[list[str]]=None,
    bad_patterns: Optional[list[str]]=None,
    whitelist: Optional[list[str]]=None
    ) -> None:
    """
    Recursively iterates through the leaf elements of JSON  and registers
    elements for redaction with keys matching a bad pattern blacklist. Any key
    containing an element of ``bad_patterns`` will be redacted, unless it is
    specified exactly in ``whitelist``. Pattern matching is case-insensitive.
    
    :param obj: JSON object with values to redact, or a string to redact
    :param key_path: The redaction label. Must provide if redacting a string.
    :param bad_patterns: Redact values for all keys containing these word
        stubs (case-insensitive)
    :param whitelist: Never redact values for these full words (case-sensitive)
    """
    if bad_patterns is None:
        _bad_patterns = _BAD_PATTERNS
    else:
        _bad_patterns = [k.casefold() for k in bad_patterns] # case-insensitive
    if whitelist is None:
        _whitelist = _WHITELIST
    else:
        _whitelist = whitelist # case-sensitive
    _register_redactions(obj, key_path, _bad_patterns, _whitelist)


def _register_redactions_from_response(
    response: Response,
    register_redactions: Callable
    ) -> None:
    if response.status_code == codes.OK:
        try:
            register_redactions(response.json())
        except json.decoder.JSONDecodeError:
            pass            


def register_redactions_from_response(response: Response) -> None:
    """
    Convenience method that calls :func:`register_redactions` on an
    ``httpx.Response`` object if the response is successful. To register a
    response object for redaction it must have an ``application/json`` content
    type. If the response object has a ``text/plain`` content type, secrets in
    the response will **NOT** be redacted.
    
    :param response:
    """
    _register_redactions_from_response(response, register_redactions)


def _emit(handler: FileHandler | StreamHandler, record: LogRecord):
    if handler.stream is None: # pragma: no cover
        raise ValueError("Logging handler stream is None")
    
    try:
        msg = _LOG_REDACTOR.redact(handler.format(record))
        handler.acquire()
        try:
            handler.stream.write(msg + handler.terminator)
            handler.flush()
        finally:
            handler.release()
    except (BrokenPipeError, OSError, ValueError, TypeError):
        handler.handleError(record)


class RedactFileHandler(FileHandler):
    """FileHandler subclass that redacts secrets"""
    
    def emit(self, record: LogRecord) -> None:
        _emit(self, record)


class RedactStreamHandler(StreamHandler):
    """StreamHandler subclass that redacts secrets"""
    
    def emit(self, record: LogRecord) -> None:
        _emit(self, record)

