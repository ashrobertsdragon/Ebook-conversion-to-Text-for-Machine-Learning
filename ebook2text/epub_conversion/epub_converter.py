from typing import List

from ebook2text._types import EpubBook, Tag
from ebook2text.abstract_book import BookConversion
from ebook2text.ebooklib import epub
from ebook2text.epub_conversion import (
    EpubChapterSplitter,
    EpubImageExtractor,
    EpubTextExtractor,
)


class EpubConverter(BookConversion):
    """
    Converts EPUB files to text and splits chapters.

    This class extends the BookConversion abstract class and provides methods
    for reading EPUB files,extracting text from elements, extracting images,
    processing chapter text, and splitting chapters.

    Args:
        file_path (str): The path to the EPUB file to be read.
        metadata (dict): A dictionary containing metadata such as title and
            author information.
    """

    def _read_file(self, file_path: str) -> EpubBook:
        """Reads Epub file using Ebooklib package"""
        return epub.read_epub(file_path, options={"ignore_ncx": True})

    def extract_images(self, element: Tag) -> List[str]:
        """Delegates to EpubImageExtractor to extract images."""
        image_extractor = EpubImageExtractor(self.book)
        return image_extractor.extract_images(element)

    def extract_text(self, element: Tag) -> str:
        """Delegates to EpubTextExtractor to extract text."""
        text_extractor = EpubTextExtractor(self)
        return text_extractor.extract_text(element)

    def split_chapters(self) -> str:
        """
        Splits the EPUB file into chapters.
        """
        splitter = EpubChapterSplitter(self.book, self.metadata, self)
        return splitter.split_chapters()
