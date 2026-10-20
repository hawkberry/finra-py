import atexit
import logging
import sys
from importlib import metadata
from pathlib import Path
from typing import Iterable, Optional, TextIO

from . import auth
from . import base_client
from .log_redactor import _LOG_REDACTOR, RedactFileHandler, RedactStreamHandler


__all__ = [
    "get_logger",
    "enable_bug_report_logging",
    ]


##############################################################################
# LOGGING

def get_logger() -> logging.Logger:
    """Logger for :mod:`debug` module"""
    return logging.getLogger(__name__)


##############################################################################
# BUG REPORTING

_FMT = "[%(levelname)s:%(filename)s:%(lineno)s:%(funcName)s] %(message)s"

def _enable_bug_report_logging(
    filename: Optional[str | Path]=None,
    stream: Optional[TextIO]=sys.stderr,
    loggers: Optional[Iterable[logging.Logger]]=None
    ) -> tuple[Optional[RedactFileHandler], Optional[RedactStreamHandler]]:
    
    _LOG_REDACTOR.enabled = True # enable redaction registration
    
    formatter = logging.Formatter(_FMT)
    if filename is None: # add redacting file handler
        fh = None
    else:
        fh = RedactFileHandler(filename)
        fh.setFormatter(formatter)
    if stream is None: # add redacting stream handler
        sh = None
    else:
        sh = RedactStreamHandler(stream)
        sh.setFormatter(formatter)
    
    if loggers is None:
        loggers = (
            get_logger(),
            auth.get_logger(),
            base_client.get_logger(),
            )
    for logger in loggers:
        logger.setLevel(logging.DEBUG) # debug
        if fh is not None:
            logger.addHandler(fh)
        if sh is not None:
            logger.addHandler(sh)
    
    # Cleanup: flush and close the handlers
    def cleanup(handler): # pragma: no cover
        try:
            handler.flush()
            handler.close()
        except Exception: # ignore cleanup failures
            pass
    
    if fh is not None:
        atexit.register(lambda: cleanup(fh))
    if sh is not None: # NOTE: this does not close the underlying stream
        atexit.register(lambda: cleanup(sh))
    return fh, sh


def enable_bug_report_logging(
    filename: Optional[str | Path]=None,
    stream: Optional[TextIO]=sys.stderr
    ) -> None:
    """
    Enable detailed diagnostic logging for the FINRA client, authentication,
    and debug modules. The dedicated handlers apply best-effort redaction
    before writing the output. By default, logs are written to ``sys.stderr``.
    To suppress stderr output when writing to a file, set ``stream=None``. At
    least one output destination is required. For more information about debug
    logging see :ref:`debug`.
    
    :param filename: Log file name to open using :py:class:`RedactFileHandler
        <finra.log_redactor.RedactFileHandler>`
    :param stream: Open file stream passed to :py:class:`RedactStreamHandler
        <finra.log_redactor.RedactStreamHandler>`
    
    .. note::
        **IMPORTANT!** Log redaction is intended as a bug reporting utility and
        not for use in production code. It is not guaranteed to be perfect, and
        should be considered only best effort. Never share your logs without
        verifying that all secret information is properly redacted. All logged
        output is processed and recorded, which creates a performance penalty.
        To terminate bug report logging, exit the program.
    """
    if filename is None and stream is None:
        raise ValueError(
            "Must set filename or stream to enable bug report logging"
            )
    
    _enable_bug_report_logging(filename, stream)
    
    get_logger().debug(
        "FINRA API Client version %s", metadata.version("finra-py")
        )

