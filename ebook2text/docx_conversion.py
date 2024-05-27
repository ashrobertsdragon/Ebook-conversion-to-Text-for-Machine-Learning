import base64
from io import BytesIO
from typing import Tuple

import docx
from docx import Document
from docx.text.paragraph import Paragraph

from .abstract_book import BookConversion
from .chapter_check import is_chapter, is_not_chapter
from .ocr import run_ocr


class DocxConverter(BookConversion):
    """
    Class to convert a Word document to structured text, extract images,
    perform OCR, and split content into chapters.

    Attributes:
        file_path (str): The path to the Word document.
        metadata (dict): Metadata related to the document.
        doc (Document): The parsed Word document object.
        paragraphs (list): List of paragraphs objects extracted from the
            document.
        pages (list): List of parsed text pages.

    Methods:
        extract_paragraphs: Extracts paragraphs from the Word document.
        extract_paragraph_text: Extracts text content from a paragraph and
            performs OCR on images.
        clean_text: Cleans smart punctuation from the text.
        split_chapters: Splits the paragraphs into chapters.
    """

    def __init__(self, file_path: str, metadata: dict):
        super().__init__(file_path, metadata)
        self.paragraphs: list = self.extract_paragraphs()
        self.non_chapter: bool = False

    def _read_file(self, file_path: str) -> Document:
        return docx.Document(file_path)

    def extract_paragraphs(self) -> list:
        return self.book.paragraphs

    def _contains_page_break(self, paragraph: Paragraph) -> bool:
        """
        Checks if a given paragraph contains a page break.
        Args:
            paragraph: The Paragraph object containing the text and formatting
        Returns:
            bool: True if the paragraph contains a page break, False otherwise
        """
        for run in paragraph.runs:
            if (
                "<w:lastRenderedPageBreak/>" in run.element.xml
                or "<w:pageBreakBefore/>" in run.element.xml
                or "<w:br " in run.element.xml
            ):
                return True
        return False

    def _extract_images(self, paragraph: Paragraph) -> list:
        """
        Extracts and converts images found in a Word document's paragraph into
        base64-encoded strings.

        Args:
            paragraph: A paragraph object from a `.docx` file, which contains
                runs and potentially inline images.

        Returns:
            list: A list of base64-encoded strings, each representing an image
                extracted from the paragraph.
        """
        SCHEMA_STUB = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
        SCHEMA = f"'{SCHEMA_STUB}embed'"
        base64_images: list = []
        for run in paragraph.runs:
            for inline_shape in run.element.findall(
                ".//a:blip", namespaces=docx.oxml.ns.nsmap
            ):
                image_blip = inline_shape.get(SCHEMA)
                image_part = self.book.part.related_parts[image_blip]
                stream = BytesIO(image_part.blob)
                read_strm = stream.read()
                base64_encoding = base64.b64encode(read_strm).decode("utf-8")
                base64_images.append(base64_encoding)

        return base64_images

    def extract_text(self, paragraph: Paragraph) -> str:
        """
        Extracts the text content from a paragraph in a Word document,
        performs optical character recognition (OCR) on any images present in
        the paragraph, and returns the recognized text
        """
        ocr_text: str = ""
        base64_images: list = self._extract_images(paragraph)
        if base64_images:
            ocr_text = run_ocr(base64_images)
        paragraph_text: str = paragraph.text.strip()
        return ocr_text if ocr_text else paragraph_text

    def _check_index(self, index: int) -> bool:
        """
        Checks if the given index exceeds a predefined maximum limit for lines
        to check.

        Args:
            index (int): The index to be checked against the maximum limit.

        Returns:
            bool: True if the index is greater than or equal to the maximum
                limit, False otherwise.
        """
        return index >= self.MAX_LINES_TO_CHECK

    def _is_start_of_chapter(self, text: str, index: int) -> bool:
        """
        Checks if the given text marks the start of a new chapter based on
        specific criteria.

        Args:
            text (str): The text to be checked for chapter header indicators.
            index (int): The number of paragraphs since the last page break.

        Returns:
            bool: True if the text is considered the start of a chapter, False
                otherwise.
        """
        if self._check_index(index):
            return False
        return is_chapter(text)

    def _is_non_chapter(self, text: str, index: int) -> bool:
        """
        Checks if the given text is not a chapter based on specific criteria.

        Args:
            text (str): The text to be checked for being front or back matter.
            index (int): The paragraph index of the text within the chapter.

        Returns:
            bool: True if the text is not a chapter, False otherwise.
        """
        if self._check_index(index):
            return False
        return is_not_chapter(text, self.metadata)

    def _process_text(
        self, paragraph_text: str, current_chapter_index: int
    ) -> Tuple[str, int]:
        """
        Process a paragraph's text to determine if it starts a new chapter and
        format it accordingly.

        Args:
            paragraph_text (str): The text of the paragraph to be processed.
            current_chapter_index (int): The index of the paragraph
                within the current chapter.

        Returns:
            Tuple[str, int]: A tuple containing the processed text and the
                updated index of the paragraph within its chapter.
        """
        CHAPTER_SEPARATOR = "***"
        current_chapter_index += 1

        if self._is_non_chapter(paragraph_text, current_chapter_index):
            processed_text = ""
            self.non_chapter = True
        elif self._is_start_of_chapter(paragraph_text, current_chapter_index):
            current_chapter_index = 0
            processed_text = CHAPTER_SEPARATOR if self.pages else ""
            self.non_chapter = False
        elif self.non_chapter:
            processed_text = ""
        else:
            processed_text = self.clean_text(paragraph_text)

        return processed_text, current_chapter_index

    def split_chapters(self) -> str:
        """Splits the paragraph list into chapters."""
        self.pages: list = []
        current_page: list = []
        paragraph_chapter_index: int = 0

        for i, paragraph in enumerate(self.paragraphs):
            if i > 20:
                break
            paragraph_text = self.extract_text(paragraph)
            paragraph_chapter_index += 1

            if self._contains_page_break(paragraph):
                self.pages.append("\n".join(current_page))
                current_page = []
                paragraph_chapter_index = 0

            elif paragraph_text:
                (processed_text, paragraph_chapter_index) = self._process_text(
                    paragraph_text, paragraph_chapter_index
                )
                current_page.append(processed_text)

        if current_page:
            self.pages.append("\n".join(current_page))
        return "\n".join(self.pages)


def read_docx(file_path: str, metadata: dict) -> str:
    """
    Reads the contents of a DOCX file, preprocesses it, and returns it as a
    string.

    Args:
        file_path (str): The path to the DOCX file.
        metadata (dict): Metadata about the document.

    Returns:
        str: The processed text of the DOCX file formatted into chapters.
    """
    docx_converter = DocxConverter(file_path, metadata)
    return docx_converter.split_chapters()
