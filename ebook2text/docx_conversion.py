import base64
import logging
from typing import Tuple

import docx
from docx import Document
from docx.text.paragraph import Paragraph

from .abstract_book import BookConversion
from .chapter_check import is_chapter, is_not_chapter
from .namespaces import docx_ns_map
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
        """
        Calls the __init__ method of the parent BookConversion class which
        calls assigns the return of the _read_file method to self.book. Then
        extracts the paragraph objects from the book and puts them in the
        paragraphs list before initializing the non_chapter flag and
        pages_list
        """
        super().__init__(file_path, metadata)
        self.paragraphs: list = self.extract_paragraphs()

        self.non_chapter: bool = False
        self.pages_list: list = []

    def _read_file(self, file_path: str) -> Document:
        """
        Reads a Word document from the specified file path and returns a
        Document object representing the parsed content.
        """
        return docx.Document(file_path)

    def extract_paragraphs(self) -> list:
        """
        Extracts paragraphs from the Word document.

        Returns:
            list: A list of paragraph objects extracted from the document.
        """
        return self.book.paragraphs

    def _contains_page_break(self, paragraph: Paragraph) -> bool:
        """
        Checks if a given paragraph contains a page break.
        Args:
            paragraph: The Paragraph object containing the text and formatting
        Returns:
            bool: True if the paragraph contains a page break, False otherwise
        """
        p_element = paragraph._element
        if p_element.pPr is not None:
            if p_element.pPr.pageBreakBefore is not None:
                # Explicit check required by python-dox library to avoid
                # FutureWarning warning
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
        image_blobs: list = self._extract_image_blobs(paragraph)
        base64_images: list = self._build_base64_images_list(image_blobs)
        return base64_images

    def _extract_image_blobs(self, paragraph: Paragraph) -> list:
        """
        Extracts image blobs from a paragraph in a Word document and returns a
        list of these blobs.

        Args:
            paragraph (Paragraph): The paragraph object from a Word document
                containing runs with potential images.

        Returns:
            list: A list of image blobs extracted from the paragraph.
        """
        namespace: dict = docx_ns_map
        image_blobs: list = []

        blips = paragraph._element.findall(".//a:blip", namespaces=namespace)
        for blip in blips:
            try:
                rId = blip.attrib[f"{{{namespace['r']}}}embed"]
                image_part = paragraph.part.related_parts[rId]
                image_blobs.append(image_part.blob)
            except Exception as e:
                logging.exception("Could not extract images %s", str(e))
        return image_blobs

    def _build_base64_images_list(self, image_blobs: list) -> list:
        """
        Extracts and converts images found in a Word document's paragraph into
        base64-encoded strings.

        Args:
            image_blobs (list): A list of image blobs extracted from the
                paragraph.

        Returns:
            list: A list of base64-encoded strings representing the images.
        """
        base64_images = [
            base64.b64encode(image).decode("utf-8") for image in image_blobs
        ]
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
        self, paragraph_text: str, current_para_index: int
    ) -> Tuple[str, int]:
        """
        Process a paragraph's text to determine if it starts a new chapter and
        format it accordingly.

        Args:
            paragraph_text (str): The text of the paragraph to be processed.
            current_para_index (int): The index of the paragraph
                within the current chapter.

        Returns:
            Tuple[str, int]: A tuple containing the processed text and the
                updated index of the paragraph within its chapter.
        """
        CHAPTER_SEPARATOR = "***"

        if self._is_start_of_chapter(paragraph_text, current_para_index):
            current_para_index = 0
            processed_text = CHAPTER_SEPARATOR if self.pages_list else ""
            self.non_chapter = False
        elif self._is_non_chapter(paragraph_text, current_para_index):
            processed_text = ""
            self.non_chapter = True
        elif self.non_chapter:
            processed_text = ""
        else:
            processed_text = self.clean_text(paragraph_text)
        return processed_text, current_para_index

    def _add_page(self, current_page: list) -> None:
        """
        Adds the current page content to the `self.pages` list after filtering
        out empty pages.

        Args:
            current_page (list): The list of content for the current page.

        Effects:
            Modifies the `self.pages` list by appending the non-empty page
            content.
        """
        filtered_page = list(filter(None, current_page))
        if filtered_page:
            self.pages_list.extend(filtered_page)

    def _split_book(self) -> str:
        """
        Process paragraphs to organize them into pages and chapters, handling
        page breaks and chapter starts, and compile the final structured text
        of the book.

        Returns:
            str: The structured text of the entire book.
        """
        current_page: list = []
        current_para_index: int = 0

        for paragraph in self.paragraphs:
            paragraph_text = self.extract_text(paragraph)
            current_para_index += 1

            if self._contains_page_break(paragraph):
                self._add_page(current_page)
                current_page = []
                current_para_index = 0

            if paragraph_text:
                (processed_text, current_para_index) = self._process_text(
                    paragraph_text, current_para_index
                )
                current_page.append(processed_text)

        if current_page:
            self._add_page(current_page)
        self._parsed_book = "\n".join(self.pages_list)


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
