from pathlib import Path
from typing import Generator

from bs4 import BeautifulSoup

import ebook2text.ebooklib as ebooklib
from ebook2text import logger
from ebook2text._types import EpubBook, EpubItem, ResultSet, Tag
from ebook2text.chapter_check import NOT_CHAPTER, is_chapter, is_not_chapter
from ebook2text.ebooklib import epub
from ebook2text.ebooklib.epub import EpubException
from ebook2text.epub_conversion.epub_text_extractor import EpubTextExtractor
from ebook2text.text_utilities import desmarten_text


class EpubConverter:
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

    def __init__(
        self,
        file_path: Path,
        metadata: dict,
        text_extractor: EpubTextExtractor,
    ) -> None:
        self.epub_book: EpubBook = self._read_file(file_path)
        self.metadata = metadata
        self.text_extractor = text_extractor
        self.chapter_separator = "\n***\n"
        self.max_lines_to_check = 6

    def _read_file(self, file_path: Path) -> EpubBook:
        """Reads Epub file using Ebooklib package"""
        try:
            return epub.read_epub(file_path, options={"ignore_ncx": True})
        except EpubException as e:
            logger.error(f"Error reading EPUB file: {e}")
            raise

    def _get_items(self) -> Generator[EpubItem, None, None]:
        """Yields items in the Epub file."""
        yield from self.epub_book.get_items()

    def _process_chapter_text(self, item: EpubItem) -> str:
        """
        Extracts text from a chapter item.

        Args:
            item: ebooklib item representing a chapter.

        Returns:
            str: String containing the text of the chapter.
        """
        TEXT_ELEMENTS = ["p", "img", "h1", "h2", "h3", "h4", "h5", "h6"]
        soup = BeautifulSoup(item.content, "html.parser")
        elements: ResultSet[Tag] = soup.find_all(TEXT_ELEMENTS)

        for i, element in enumerate(elements[: self.max_lines_to_check]):
            text = self.text_extractor.extract_text(element, self.epub_book)
            if any(word in NOT_CHAPTER for word in text.split()):
                return ""
            elif is_chapter(text):
                starting_line = i + 1
                return "\n".join(
                    tag.get_text().strip()
                    for tag in elements[starting_line:]
                    if tag != "img"
                )
        return ""

    def clean_text(self, text: str) -> str:
        """
        Removes smart punctuation from text
        """
        return desmarten_text(text)

    def parse_file(self) -> Generator[str, None, None]:
        """
        Split the EPUB file into chapters and return the cleaned text.

        Returns:
            str: The cleaned text of the chapters separated by '***'.
        """
        for item in self._get_items():
            if (
                item.get_type() == ebooklib.ITEM_DOCUMENT
                and not is_not_chapter(item.file_name.lower(), self.metadata)
            ):
                if chapter_text := self._process_chapter_text(item):
                    yield self.clean_text(chapter_text)

    def write_text(self, content: str, file_path: Path) -> None:
        """
        Write the parsed text to a file.

        Args:
            text (str): The parsed text to be written to the file.
        """
        with file_path.open("a", encoding="utf-8") as f:
            f.write(self.chapter_separator + content)

    def return_string(self, generator: Generator[str, None, None]) -> str:
        """Return the parsed text as a string."""
        return f"{self.chapter_separator}".join(generator)
