from bs4 import BeautifulSoup

import ebook2text.ebooklib as ebooklib
from ebook2text._types import EpubBook, ResultSet, Tag
from ebook2text.abstract_book import ChapterSplit
from ebook2text.chapter_check import NOT_CHAPTER, is_chapter, is_not_chapter
from ebook2text.epub_conversion import EpubConverter


class EpubChapterSplitter(ChapterSplit[EpubBook]):
    """
    Splits an EPUB file into chapters.
    """

    def __init__(
        self, book: EpubBook, metadata: dict, converter: EpubConverter
    ) -> None:
        super().__init__(book, metadata, converter)
        self.book = self.text_obj

    def _process_chapter_text(self, item) -> str:
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

        for i, element in enumerate(elements[: self.MAX_LINES_TO_CHECK]):
            text = self.converter.extract_text(element)
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

    def split_chapters(self) -> str:
        """
        Split the EPUB file into chapters and return the cleaned text.

        Returns:
            str: The cleaned text of the chapters separated by '***'.
        """
        chapters: list = []
        join_char = f"\n{self.CHAPTER_SEPARATOR}\n"
        for item in self.book.get_items():
            if (
                item.get_type() == ebooklib.ITEM_DOCUMENT
                and not is_not_chapter(item.file_name.lower(), self.metadata)
            ):
                if chapter_text := self._process_chapter_text(item):
                    chapters.append(self.clean_text(chapter_text))
        return join_char.join(chapters)


def read_epub(file_path: str, metadata: dict) -> str:
    """
    Reads an EPUB file and splits it into chapters.

    Args:
        file_path (str): The path to the EPUB file to be read.
        metadata (dict): A dictionary containing metadata such as title and
            author information.

    Returns:
        str: The cleaned text of the chapters separated by '***'.
    """
    epub_converter = EpubConverter(file_path, metadata)
    return epub_converter.split_chapters()
