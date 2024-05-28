import base64
from abc import ABC, abstractmethod
from typing import List

from ._types import SplitType
from .text_conversion import desmarten_text


class BookConversion(ABC):
    def __init__(self, file_path: str, metadata: dict):
        self.file_path: str = file_path
        self.metadata: dict = metadata
        self.book = self._read_file(file_path)

    @abstractmethod
    def _read_file(file_path: str):
        raise NotImplementedError("Must be implemented in child class")

    @abstractmethod
    def split_chapters(self) -> str:
        raise NotImplementedError("Must be implemented in child class")


class ImageExtraction(ABC):
    @abstractmethod
    def extract_images(self) -> List[str]:
        raise NotImplementedError("Must be implemented in child class")

    def _build_base64_images_list(self, image_streams: list) -> list:
        """
        Converts image blobs to base64-encoded strings.

        Args:
            image_blobs (list): A list of extracted image streams.

        Returns:
            list: A list of base64-encoded strings representing the images.
        """
        return [
            base64.b64encode(image).decode("utf-8") for image in image_streams
        ]


class TextExtraction(ABC):
    @abstractmethod
    def extract_text(self) -> str:
        raise NotImplementedError("Must be implemented in child class")

    @abstractmethod
    def _extract_image_text(self) -> str:
        raise NotImplementedError("Must be implemented in child class")


class ChapterSplit(ABC):
    @abstractmethod
    def __init__(self, text_obj: SplitType, metadata: dict, parent) -> None:
        self.text_obj = text_obj
        self.metadata = metadata
        self.parent = parent

        self.MAX_LINES_TO_CHECK: int = 3
        self.CHAPTER_SEPARATOR: str = "***"

    @abstractmethod
    def split_chapters(self) -> str:
        raise NotImplementedError("Must be implemented in child class")

    def clean_text(self, text: str) -> str:
        """
        Removes smart punctuation from text
        """
        return desmarten_text(text)
