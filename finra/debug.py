import atexit
import logging
import sys
from importlib import metadata
from pathlib import Path
from typing import Iterable, Optional, TextIO

from . import auth
from . import base_client
from .log_redactor import RedactFileHandler, RedactStreamHandler


__all__ = ["enable_bug_report_logging"]


def get_logger() -> logging.Logger:
    """Logger for :mod:`debug` module"""
    return logging.getLogger(__name__)


# Internal version used in testing
def _enable_bug_report_logging(
    filename: Optional[str | Path]=None,
    stream: Optional[TextIO]=sys.stderr,
    loggers: Optional[Iterable[logging.Logger]]=None
    ) -> tuple[Optional[RedactFileHandler], Optional[RedactStreamHandler]]:
    formatter = logging.Formatter(
        "[%(levelname)s:%(filename)s:%(lineno)s:%(funcName)s] %(message)s"
        )
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
    return fh, sh


def enable_bug_report_logging(
    filename: Optional[str | Path]=None,
    stream: Optional[TextIO]=sys.stderr
    ) -> None:
    """
    Enable bug report logging for the FINRA API client.
    
    This will collect all logs related to the client, and redact common secrets
    before writing them. By default a handler is included that writes to
    ``sys.stderr``. To disable this behavior, set ``stream=None``.
    
    :param filename: log file name to open using :py:class:`RedactFileHandler
        <finra.log_redactor.RedactFileHandler>`
    :param stream: open file stream passed to :py:class:`RedactStreamHandler
        <finra.log_redactor.RedactStreamHandler>`
    
    .. note::
        **IMPORTANT!** Log redaction is only a best effort, and is not
        guaranteed to be perfect. Never share your logs without verifying that
        all secret information is properly redacted. The bug report utility
        should not be used in production code. All logged output is recorded,
        which creates a performance penalty. To terminate bug report logging,
        and flush the handlers, just exit the program.
    """
    if filename is None and stream is None:
        raise ValueError(
            "Must set filename or stream to enable bug report logging"
            )
    
    fh, sh = _enable_bug_report_logging(filename, stream)
    
    # Cleanup: flush and close the handlers
    def cleanup(handler): # pragma: no cover
        try:
            handler.flush()
            handler.close()
        except Exception: # ignore cleanup failures
            pass
    
    if fh is not None:
        atexit.register(lambda: cleanup(fh))
    if sh is not None: # note: this does not close the underlying stream
        atexit.register(lambda: cleanup(sh))
    
    get_logger().debug(
        "FINRA API Client version %s", metadata.version("finra-py")
        )

