from abc import ABC, abstractmethod

from .chapter_check import is_chapter, is_not_chapter
from .text_conversion import desmarten_text


class BookConversion(ABC):
    def __init__(self, file_path: str, metadata: dict):
        self.file_path: str = file_path
        self.metadata: dict = metadata
        self.book = self._read_file(file_path)
        self.MAX_LINES_TO_CHECK: int = 3
    
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
    def split_chapters(self) -> str:
        raise NotImplementedError("Must be implemented in child class")
    
    def clean_text(self, text: str) -> str:
        return desmarten_text(text)
    
    def _is_start_of_chapter(self, text: str, index: int) -> bool:
        
        if index >= self.MAX_LINES_TO_CHECK:
            return False
        return (
            is_chapter(text)
            or not is_not_chapter(text, self.metadata)
        )
