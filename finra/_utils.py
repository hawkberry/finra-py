from datetime import date, datetime, timezone
from typing import Any, Callable

__all__ = [
    "date_isoformat",
    "datetime_isoformat_ms",
    "datetime_naive",
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
    
    return {
        k[1:]: build_json_object(v)
        for k, v in vars(obj).items()
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

