import ebooklib
from ebooklib import epub
from ebooklib.epub import EpubBook
from bs4 import BeautifulSoup

from .abstract_book import BookConversion
from .chapter_check import is_chapter, is_not_chapter, NOT_CHAPTER
from .ocr import encode_image, run_ocr


class EpubConversion(BookConversion):
    """
    EpubConversion class for converting EPUB files to text and splitting
    chapters.

    This class extends the BookConversion abstract class and provides methods
    for reading EPUB files,extracting text from elements, extracting images,
    processing chapter text, and splitting chapters.

    Args:
        file_path (str): The path to the PDF file to be read.
        metadata (dict): A dictionary containing metadata such as title and
            author information.

    Attributes:
        MAX_LINES_TO_CHECK (int): Maximum number of lines to check for chapter
            identification.

    Methods:
        extract_text: Extract text from an element, using OCR for images.
        split_chapters: Split the EPUB file into chapters and return the
            cleaned text.
    """
    def _read_file(self, file_path: str) -> EpubBook:
        """Reads Epub file using Ebooklib package"""
        return epub.read_epub(file_path, options={"ignore_ncx": True})

    def extract_text(self, element) -> str:
        """
        Extract text from an element, using OCR for images.

        Args:
            element: The element from which text needs to be extracted.

        Returns:
            str: The extracted text from the element.
        """
        if element.name == "img":
            base64_images = self._extract_images(element)
            text = run_ocr(base64_images)
        else:
            text = element.get_text().strip().lower()
        return text

    def _extract_images(self, element) -> list:
        """
        Extracts images from the EPUB file.

        Args:
            element: The element containing the image data.

        Returns:
            list: A list of encoded image data.
        """
        image_data = self.book.read_item(element["src"])
        return [encode_image(image_data)]
    
    def _process_chapter_text(self, item) -> str:
        """
        Extracts text from a chapter item.
        
            Args:
                item: ebooklib item representing a chapter.
            Returns string containing the text of the chapter.
        """
        TEXT_ELEMENTS = ["p", "img", "h1", "h2", "h3", "h4", "h5", "h6"]
        soup = BeautifulSoup(item.content, "html.parser")
        elements = soup.find_all(TEXT_ELEMENTS)

        for i, element in enumerate(elements[:self.MAX_LINES_TO_CHECK]):
            text = self.extract_text(element)
            if any(word in NOT_CHAPTER for word in text.split()):
                return ""
            elif is_chapter(text):
                starting_line = i + 1
                return ("\n".join(
                    tag.get_text().strip()
                    for tag in elements[starting_line:]
                    if tag != "img"
                ))
        return ""
        
    def split_chapters(self) -> str:
        """
        Split the EPUB file into chapters and return the cleaned text.

        Returns:
            str: The cleaned text of the chapters separated by '***'.
        """
        chapter: list = []
        for item in self.book.get_items():
            if (
                item.get_type() == ebooklib.ITEM_DOCUMENT
                and not is_not_chapter(item.file_name.lower(), self.metadata)
            ):
                chapter_text = self._process_chapter_text(item)
                if chapter_text:
                    chapter.append(self.clean_text(chapter_text))
        return "\n***\n".join(chapter)


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
    epub_converter = EpubConversion(file_path, metadata)
    return epub_converter.split_chapters()