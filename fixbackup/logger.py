from argparse import ArgumentParser
from typing import ClassVar, Optional, Any
import sys
import os
import logging
from logging import (
    basicConfig,
    getLogger,
    setLoggerClass,
    DEBUG,
    INFO,
    WARNING,
    ERROR,
    CRITICAL,
    Logger,
)


DEBUG2 = DEBUG - 1
DEBUG3 = DEBUG - 2
DEBUG4 = DEBUG - 3
DEBUG5 = DEBUG - 4
TRACE = DEBUG - 5

getLogger().setLevel(ERROR)
getLogger("fix").setLevel(INFO)


def add_args(arg_parser: ArgumentParser) -> None:
    group = arg_parser.add_mutually_exclusive_group()
    group.add_argument(
        "--verbose",
        "-v",
        help="Verbose logging",
        dest="verbose",
        action="store_true",
        default=False,
    )
    group.add_argument(
        "--trace",
        help="Trage logging",
        dest="trace",
        action="store_true",
        default=False,
    )
    group.add_argument(
        "--quiet",
        help="Only log errors",
        dest="quiet",
        action="store_true",
        default=False,
    )


def setup_logger(
    proc: str,
    *,
    force: bool = True,
    verbose: bool = False,
    quiet: bool = False,
    level: Optional[str] = None,
    json_format: bool = True,
) -> None:
    # override log output via env var
    log_format = f"%(asctime)s|{proc}|%(levelname)5s|%(process)d|%(threadName)10s  %(message)s"
    basicConfig(format=log_format, datefmt="%y-%m-%d %H:%M:%S", force=force)
    argv = sys.argv[1:]
    if level:
        getLogger("fix").setLevel(level)
    elif "--trace" in argv or os.environ.get("FIX_TRACE", "false").lower() == "true":
        getLogger("fix").setLevel(TRACE)
    elif verbose or "-v" in argv or "--verbose" in argv or os.environ.get("FIX_VERBOSE", "false").lower() == "true":
        getLogger("fix").setLevel(DEBUG)
    elif quiet or "--quiet" in argv or os.environ.get("FIX_QUIET", "false").lower() == "true":
        getLogger().setLevel(WARNING)
        getLogger("fix").setLevel(CRITICAL)


# via https://stackoverflow.com/a/35804945/92184
def add_logging_level(level_name: str, level_num: int, method_name: Optional[str] = None) -> None:
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present

    Example
    -------
    >>> add_logging_level("TRACE", logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace("that worked")
    >>> logging.trace("so did this")
    >>> logging.TRACE
    5

    """
    if not method_name:
        method_name = level_name.lower()

    if hasattr(logging, level_name):
        raise AttributeError("{} already defined in logging module".format(level_name))
    if hasattr(logging, method_name):
        raise AttributeError("{} already defined in logging module".format(method_name))
    if hasattr(logging.getLoggerClass(), method_name):
        raise AttributeError("{} already defined in logger class".format(method_name))

    def log_for_level(self: logging.Logger, message: str, *args: Any, **kwargs: Any) -> None:
        if self.isEnabledFor(level_num):
            self._log(level_num, message, args, **kwargs)

    def log_to_root(message: str, *args: Any, **kwargs: Any) -> None:
        logging.log(level_num, message, *args, **kwargs)

    logging.addLevelName(level_num, level_name)
    setattr(logging, level_name, level_num)
    setattr(logging.getLoggerClass(), method_name, log_for_level)
    setattr(logging, method_name, log_to_root)


class FixLogger(Logger):
    def debug2(self, msg: str, *args: Any, **kwargs: Any) -> None: ...

    def debug3(self, msg: str, *args: Any, **kwargs: Any) -> None: ...

    def debug4(self, msg: str, *args: Any, **kwargs: Any) -> None: ...

    def debug5(self, msg: str, *args: Any, **kwargs: Any) -> None: ...

    def trace(self, msg: str, *args: Any, **kwargs: Any) -> None: ...


def get_fix_logger(name: Optional[str] = None) -> FixLogger:
    return getLogger(name)  # type: ignore


add_logging_level("DEBUG2", DEBUG2)
add_logging_level("DEBUG3", DEBUG3)
add_logging_level("DEBUG4", DEBUG4)
add_logging_level("DEBUG5", DEBUG5)
add_logging_level("TRACE", TRACE)

setLoggerClass(FixLogger)
setup_logger("fix", force=False)
log = get_fix_logger("fix")
