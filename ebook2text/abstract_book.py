from abc import ABC, abstractmethod
from typing import Union

from .text_conversion import desmarten_text


class BookConversion(ABC):
    def __init__(self, file_path: str, metadata: dict):
        self.file_path: str = file_path
        self.metadata: dict = metadata
        self.book = self._read_file(file_path)
        self.MAX_LINES_TO_CHECK: int = 3

        self._parsed_book: Union[str, None] = None

    def clean_text(self, text: str) -> str:
        """
        Removes smart punctuation from text
        """
        return desmarten_text(text)

    def split_chapters(self) -> str:
        """
        Splits the parsed book content into chapters, handling page breaks and
        chapter starts, and compiles the final structured text of the book.

        Returns:
            str: The structured text of the entire book with chapters
                separated.
        """
        if self._parsed_book is None:
            self._split_book()
        return self._parsed_book

    @abstractmethod
    def _read_file(file_path: str):
        raise NotImplementedError("Must be implemented in child class")

    @abstractmethod
    def _extract_images(self, text_obj) -> list:
        raise NotImplementedError("Must be implemented in child class")

    @abstractmethod
    def extract_text(self, text_obj) -> str:
        raise NotImplementedError("Must be implemented in child class")

    @abstractmethod
    def _split_book(self) -> str:
        raise NotImplementedError("Must be implemented in child class")
