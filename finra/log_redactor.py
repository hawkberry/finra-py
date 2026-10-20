import json
import logging
import re
from collections import defaultdict
from logging import LogRecord, FileHandler, StreamHandler
from typing import Any, Iterable, Optional

from httpx import Response, codes


__all__ = [
    "register_redactions",
    "register_redactions_from_response",
    "RedactFileHandler",
    "RedactStreamHandler",
    ]


##############################################################################
# LOG REDACTOR

# Class for building a global singleton for redacting secrets in logs
class _LogRedactor:
    """
    Maintains values that must be removed from log output and substitutes
    redaction labels for them
    """
    
    def __init__(self):
        self.enabled = False
        self.label_counts = defaultdict(int)
        self.__redacted_strings = {} # {string-to-redact: (label, count)}
        
    def register(self, s: Any, label: str) -> None:
        """
        Adds a value to the redaction registry and associates it with the
        provided label
        
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
        Replaces registered values in the provided message string with their
        corresponding redaction labels
        
        :param msg:
        """
        if not self.__redacted_strings:
            return msg
        
        alts = "|".join([
            re.escape(t)
            for t in sorted(self.__redacted_strings, key=len, reverse=True)
            ]) # check longest strings first to avoid partial matches

####TODO: remove
##        pattern = (
##            rf'(?:(?<=[\{{\[:, "])(?:{alts})(?=[\}}\], "]))'
##            rf"|(?:\A(?:{alts}))"
##            rf"|(?:(?:{alts})\Z)"
##            )

##        try:
        
        return re.sub(rf"(?<!\w)(?:{alts})(?!\w)", self.__repl, msg)
        
##        except KeyError:
##            return msg


# Global singleton for redacting secrets in debug logs
_LOG_REDACTOR = _LogRedactor()


##############################################################################
# REGISTER REDACTIONS

# Bad word stubs to redact if they are case-insensitively part of any key
# Case-insensitive -> define stubs are in lowercase
_BAD_PATTERNS: tuple[str, ...] = (
    "key",
    "secret",
    "token",
    "CRD",
    "SSN",
    "DOB",
    "dateOfBirth",
    "identifier",
    "addressLine",
    "firstName",
    "lastName",
    "middleName",
    "suffixName",
    "initiatorName",
    "occurrenceNumber",
    "confirmationNumber",
    "docketNumber",
    "instanceNumber",
    "userID",
    "resultLink",
    )
_BAD_PATTERNS = tuple([k.casefold() for k in _BAD_PATTERNS])


# Whitelisted keys to never redact, case-sensitive
_WHITELIST = (
    "token_type",
    "tierIdentifier",
    "issueSymbolIdentifier",
    "securitiesInformationProcessorSymbolIdentifier",
    )


# Warn-on submission warning patterns for matching special values
_SSN = re.compile(
    r"(\d{3}(\s|\.|-|_)?\d{2}(\s|\.|-|_)?\d{4})"
    )

_SSN_AVOID_HYPHEN_NOTATION = re.compile(
    r"(\d{3}(\s|\.|_)?\d{2}(\s|\.|_)?\d{4})"
    )

_DATE_OF_BIRTH = re.compile(
    r"(((DOB)|(BIRTH ON)|(BIRTH IS)|(D\.O\.B\.?)|(BIRTH)|(DATE OF BIRTH))"
    r"\s*[:=,-]?\s*"
    r"(\(?(?:\d|\d{2})/(?:\d|\d{2})/(?:\d{4}|\d{2})\)?))"
    )

_ACCOUNT_NUMBER_AVOID_ZIP = re.compile(
    r"((#|A/C|ACCOUNT|ACCT|ANNUITY|CONTRACT|LIFE|LOAN #|LOAN NO.|"
    r"LOAN NUMBER|POLICIES|POLICY|VA)\D*"
    r"(?<![$])(?<![$]\s)(?<!POB)(?<!POB\s)"
    r"(?<!P\.O\.B\.)(?<!P\.O\.B\.\s)(?<!BOX)(?<!BOX\s)"
    r"(?<!I)(?<!I\s)\d{6,})"
    )

_CREDIT_CARD_NUMBER = re.compile(
    r"(((4|6)\d|(5(1|2|3|4|5)))\d{2}(\s|\.|-|_)"
    r"\d{4}(\s|\.|-|_)\d{4}(\s|\.|-|_)\d{4})"
    )

_CREDIT_CARD_NUMBER_AMEX = re.compile(
    r"((34|37)\d{2}(\s|\.|-|_)\d{6}(\s|\.|-|_)\d{5})"
    )

_HEALTH_INFO = re.compile(
    r"(\b(trauma|thyroid|thrombosis|syphilis|sinus|shingles|sepsis|sclera|"
    r"sarcoma|rhinitis|renal|pathology| pancreatic|pancreas|obesity|"
    r"neurone|myositis|meningitis|lyme|kidney|influenza|hypo|hypertension|"
    r"hyper| hepatitis|hemophilia|gitis|gastrointestinal|gallbladder|flu|"
    r"diagnos|congenital|chronic|bronchitis|brain| arthriti|"
    r"amyotrophic lateral|allergy|WILM|Tumor|Tuberculosis|Stroke|Seizure|"
    r"SWINE|SIDS|SCHIZOPHRENIA| SARS|Respiratory|Pulmonary|Pneumonia|"
    r"PTSD|PSORIASIS|PROSTATE|POX|PARKINSON|PALSY|PACEMAKER|OTOMY|OSTOMY|"
    r"OSTEOPOROSIS|OSCOPY|OPLASTY|Neuropathy|Muscular Dystrophy|"
    r"Multiple Sclerosis|MERS|MELANOMA|Lymphoma| Lymph node|Lupus|Liver|"
    r"Leukemia|LARYNX|JAUNDICE|INFLAMMATION|Hernia|Hemorrhage|HODGKIN|"
    r"HIV|HEART|H1N1| GOUT|GLAUCOMA|Fracture|Fibromyalgia|FEVER|"
    r"Epilepsy|Encephalitis|ENDO|ECTOMY|Diabetic|Diabetes|Depression|"
    r"Dementia|DYSFUNCTION|DOWN SYNDROME|DEGENERATION|Coronary|"
    r"Congenital|Cardio|Cardiac|CROHN|COVID|CORONA| COMA|COLORECTAL|"
    r"COLON|CATARACT|CANCER|Bulim(ia|i)|Bipolar|Bi-Polar|BREAST|"
    r"BLADDER|Autoimmune|Auti(sm|s)| Attention Deficit|"
    r"Atrial fibrillation|Asthma|Arthrit(is|i)|Appendix|Appendicitis|"
    r"Appendectomy|Anxiety| Anorex(ia|i)|Aneurysm|ATOSIS|ARRHYTHMIA|"
    r"APNEA|AORTA|ALZHEIMER|ADHD|AIDS|ALS)\b)"
    )

_WARN_ON_RE = (
    _SSN,
    _SSN_AVOID_HYPHEN_NOTATION,
    _DATE_OF_BIRTH,
    _ACCOUNT_NUMBER_AVOID_ZIP,
    _CREDIT_CARD_NUMBER,
    _CREDIT_CARD_NUMBER_AMEX,
    _HEALTH_INFO,
    )


# Redact entire text field if the value matches these case-sensitive patterns
_HEALTH_INFO_AVOID_REDACTED = re.compile(
    r"(\b(Disease|Infection|MENTAL|PSYCHIATRIC|SURGERY|Syndrome)\b)"
    )


# Warn-on submission warnings, case-insensitive field names
_WARN_ON: tuple[str, ...] = (
    "dateExplanation",
    "allegationAmountExplanation",
    "disclosureEventDetailText",
    "initiatorName",
    "customerResidenceStateDetailText",
    "employingFirmName",
    "commentText",
    "chargeText",
    "amendedChargeText",
    "sentenceDetailText",
    "pendingLimitationDetailText",
    "appealLimitationDetailText",
    "orderedSanctionTypeOtherText",
    "sanctionDurationExplanation",
    "sanctionRequalificationExplanation",
    "terminationAllegation",
    "appealDetailText",
    "compromiseCreditorTermsText",
    "otherBusinessText",
    "internalReviewU5DisclosureQuestionText",
    "dispositionDetailText",
    )
_WARN_ON = tuple([k.casefold() for k in _WARN_ON])


def _register_redactions(
    obj: Any,
    key_path: Optional[list[str]],
    bad_patterns: Iterable[str],
    whitelist: Iterable[str],
    warn_on: Optional[Iterable[str]]
    ) -> None:
    if obj is None: # JSON nulls are not redacted
        return
    
    if key_path is None:
        key_path = []
    
    if isinstance(obj, list):
        for i, v in enumerate(obj):
            key_path.append(str(i))
            _register_redactions(v, key_path, bad_patterns, whitelist, warn_on)
            key_path.pop()
        
    elif isinstance(obj, dict):
        key = obj["fieldName"] if "fieldName" in obj else None # Filter support
        for k, v in obj.items():
            if key is None:
                key_path.append(k)
            else: # redact Filter values using Filter field names
                key_path.append(key if k in ("fieldValue", "values") else k)
            _register_redactions(v, key_path, bad_patterns, whitelist, warn_on)
            key_path.pop()
        
    elif key_path: # use last non-numeric key as name
        for k in reversed(key_path): # pragma: no cover
            try:
                int(k)
            except ValueError:
                break
        
        if k not in whitelist: # whitelist is case-sensitive
            last_key = k.casefold()
            
            # Bad patterns is case-insensitive
            if any([bad in last_key for bad in bad_patterns]):
                _LOG_REDACTOR.register(obj, "-".join(key_path))
                
            # Warn-on free-text field names are case-insensitive
            # RE matching is case-sensitive
            elif (warn_on is not None
                and isinstance(obj, str)
                and last_key in warn_on):
                
                # Redact entire free-text field if value matches these patterns
                if _HEALTH_INFO_AVOID_REDACTED.search(obj):
                    _LOG_REDACTOR.register(obj, "-".join(key_path))
                    
                # Redact regex matches from free-text field
                else:
                    for p in _WARN_ON_RE:
                        for m in p.finditer(obj):
                            _LOG_REDACTOR.register(
                                m.group(0), "-".join(key_path)
                                )


def register_redactions(
    obj: Any,
    key_path: Optional[list[str]]=None,
    bad_patterns: Optional[Iterable[str]]=None,
    whitelist: Optional[Iterable[str]]=None
    ) -> None:
    """
    Recursively walk a JSON object, and registers leaf values for redaction if
    their corresponding keys match a string in ``bad_patterns``. Any key
    containing a string in ``bad_patterns`` will be matched, unless it is
    specified exactly in ``whitelist``. Bad pattern matching is
    case-insensitive.
    
    :param obj: JSON object with values to redact, or a string to redact
    :param key_path: The redaction label. Must provide if redacting a string.
    :param bad_patterns: Redact values for all keys containing these word
        stubs (case-insensitive). Default: ``_BAD_PATTERNS``.
    :param whitelist: Never redact values for these full words
        (case-sensitive). Default: ``_WHITELIST``.
    """
    if not _LOG_REDACTOR.enabled: # no ops exit for non-redaction debug logging
        return
    
    _bad_patterns: Iterable[str] # case-insensitive
    if bad_patterns is None:
        _bad_patterns = _BAD_PATTERNS
    else:
        _bad_patterns = [k.casefold() for k in bad_patterns]
    
    _whitelist: Iterable[str] # case-sensitive
    if whitelist is None:
        _whitelist = _WHITELIST
    else:
        _whitelist = whitelist
    
    _register_redactions(obj, key_path, _bad_patterns, _whitelist, None)


def register_redactions_from_response(response: Response) -> None:
    """
    Registers redactions from a successful ``httpx.Response`` object by
    inspecting ``response.json()``, regardless of the response content type,
    and passing it through :func:`register_redactions`. If the body cannot be
    decoded as JSON, no values are registered from that response and a warning
    is emitted.
    
    :param response:
    """
    if not _LOG_REDACTOR.enabled: # no ops exit for non-redaction debug logging
        return
    
    if response.status_code == codes.OK:
        try:
            _register_redactions(
                response.json(), None, _BAD_PATTERNS, _WHITELIST, _WARN_ON
                )
        except (json.decoder.JSONDecodeError, UnicodeDecodeError):
            logging.getLogger("finra.debug").warning(
                "Response.json() could not decode the content as JSON, so the "
                "response could not be registered for redaction. Review the "
                "log before sharing."
                )


##############################################################################
# LOGGING HANDLERS

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

