import logging
from collections.abc import Callable
from typing import Any


class LoggerProxy:
    def __init__(self):
        self._logger = None

    def set_logger(self, logger: Any) -> None:
        self._logger = logger

    def _add_basic_logger(self) -> None:
        logging.basicConfig()
        self._logger = logging.getLogger("supasaas")

    def __getattr__(self, name: str) -> Callable:
        if self._logger is None:
            self._add_basic_logger()
        return getattr(self._logger, name)


logger = LoggerProxy()


def set_logger(custom_logger: Any) -> None:
    """
    Set the logger for the entire library.

    Args:
        custom_logger: The logger object to be used throughout the library.
    """
    logger.set_logger(custom_logger)
