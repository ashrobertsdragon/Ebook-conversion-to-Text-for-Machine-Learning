from ._logger import logger, set_logger
from .convert_file import convert_file
from .file_handling import read_text_file, write_to_file
from .VERSION import __version__

__version__ = __version__
__all__ = [
    "convert_file",
    "read_text_file",
    "write_to_file",
    "logger",
    "set_logger",
]
