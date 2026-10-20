from datetime import date, datetime, timezone
from typing import Any, Callable

import httpx


__all__ = [
    "date_isoformat",
    "datetime_isoformat_ms",
    "datetime_naive",
    "validate_url",
    "build_json_object",
    "LazyLog",
    ]


##############################################################################
# TIME

def date_isoformat(dt: date | datetime) -> str:
    """
    Formats ``datetime`` or ``date`` objects as `YYYY-MM-DD` according to
    ISO 8601
    
    :param dt:
    """
    if isinstance(dt, datetime):
        return dt.date().isoformat()
    return dt.isoformat()


def datetime_isoformat_ms(dt: datetime, sep: str="T", suffix: str="") -> str:
    """
    Formats ``datetime`` or ``date`` objects as
    `yyyy-MM-dd'T'HH:mm:ss.SSS{suffix}` rounded down to the closest
    millisecond, according to a special variation of ISO 8601, with optional
    suffix for timezone. A suffix of 'Z' indicates 'UTC' timezone.
    
    :param dt:
    :param sep:
    :param suffix:
    """
    return dt.strftime(
        f"%Y-%m-%d{sep}%H:%M:%S.{dt.microsecond // 1000:03d}{suffix}"
        )


def datetime_naive(dt: date | datetime, tz=timezone.utc) -> datetime:
    """
    Return a naive ``datetime``. If given ``datetime`` is tz-aware, convert to
    the provided ``timezone``, which defaults to ``timezone.utc``.
    
    :param dt:
    """
    if isinstance(dt, datetime):
        if dt.tzinfo is not None: # convert datetime to tz, and remove tzinfo
            return dt.astimezone(tz).replace(tzinfo=None)
        return dt
    return datetime.combine(dt, datetime.min.time()) # date


##############################################################################
# SECURITY

def validate_url(
    url: str | httpx.URL,
    allowed_hosts: tuple[str, ...]
    ) -> httpx.URL:
    """
    Validate a URL before making an authenticated request.
    
    :param url:
    :param allowed_hosts:
    """
    parsed = httpx.URL(url)
    
    if parsed.scheme != "https":
        raise ValueError("URLs must use HTTPS")
    
    if parsed.username or parsed.password:
        raise ValueError("URLs must not contain embedded credentials")
    
    if parsed.host.lower() not in allowed_hosts:
        _allowed = ", ".join([f"'{host}'" for host in allowed_hosts])
        raise ValueError(f"URLs must use an approved host: {_allowed}")
    
    return parsed


##############################################################################
# JSON

def build_json_object(obj: object | Any) -> Any:
    """
    Convert python object to json object. Copy data structures, recursively
    applied to object attributes and values. Enums are not handled, and must be
    converted prior to calling.
    
    :param obj:
    """
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj # literals are passed through
    
    if isinstance(obj, dict): # dicts are processed recursively
        return {k: build_json_object(v) for k, v in obj.items()}
    
    if isinstance(obj, list): # lists are processed recursively
        return [build_json_object(v) for v in obj]
    
    try:
        _obj = vars(obj)
    except TypeError as exc:
        exc.args = (
            f"{exc}. The build method does not support type "
            f"'{obj.__class__.__module__}.{obj.__class__.__qualname__}'.",
            )
        raise
    
    return {
        k[1:]: build_json_object(v)
        for k, v in _obj.items()
        if k[0] == "_" and v is not None
        } # objects have underscore attributes iterated recursively if not None


##############################################################################
# LOGGING

class LazyLog:
    """
    Helper to defer evaluation of expensive variables in log messages.
    
    :param callback:
    """
    
    def __init__(self, callback: Callable):
        self.callback = callback
        
    def __str__(self) -> str:
        return self.callback()

