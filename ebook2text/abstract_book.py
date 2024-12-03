from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generator, Generic, List, TypeVar, Union

from ebook2text.text_utilities import desmarten_text

T = TypeVar("T")


class ImageExtraction(ABC, Generic[T]):
    @abstractmethod
    def extract_images(self, T) -> List[str]:
        raise NotImplementedError("Must be implemented in child class")


class TextExtraction(ABC, Generic[T]):
    def __init__(self, image_extractor: ImageExtraction):
        self.image_extractor = image_extractor

    @abstractmethod
    def extract_text(self, T) -> Union[str, List[str]]:
        raise NotImplementedError("Must be implemented in child class")

    @abstractmethod
    def _extract_image_text(self, T) -> str:
        raise NotImplementedError("Must be implemented in child class")


class BookConversion(ABC, Generic[T]):
    def __init__(
        self, file_path: Path, metadata: dict, text_extractor: TextExtraction
    ):
        self.file_path: Path = file_path
        self.metadata: dict = metadata
        self.text_extractor = text_extractor
        self._objects = self._read_file(file_path)
        self.MAX_LINES_TO_CHECK: int = 6
        self.CHAPTER_SEPARATOR: str = "***"

    @abstractmethod
    def _read_file(self, file_path: Path) -> Generator[T, None, None]:
        raise NotImplementedError("Must be implemented in child class")

    @abstractmethod
    def parse_file(self) -> Generator[str, None, None]:
        raise NotImplementedError("Must be implemented in child class")

    @abstractmethod
    def write_text(self, content: str, file_path: Path) -> None:
        raise NotImplementedError("Must be implemented in child class")

    @abstractmethod
    def return_string(self, generator: Generator[str, None, None]) -> str:
        raise NotImplementedError("Must be implemented in child class")

    def clean_text(self, text: str) -> str:
        """
        Removes smart punctuation from text
        """
        return desmarten_text(text)
