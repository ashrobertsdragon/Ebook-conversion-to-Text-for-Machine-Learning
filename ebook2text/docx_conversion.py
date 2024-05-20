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
        self.paragraphs = self.extract_paragraphs()

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
            if "<w:lastRenderedPageBreak/>" in run.element.xml or "<w:br " in run.element.xml:
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
        base64_images: list = []
        
        for run in paragraph.runs:
            for inline_shape in run.element.findall(
                ".//a:blip",
                namespaces=docx.oxml.ns.nsmap
            ):
                image_blip = inline_shape.get(
                    '{http://schemas.openxmlformats.org/drawingml/2006/main}embed'
                )
                image_part = self.doc.part.related_parts[image_blip]
                stream = BytesIO(image_part.blob)
                base64_images.append(
                    base64.b64encode(stream.read()).decode("utf-8")
                )
        
        return base64_images

    def extract_text(self, paragraph: Paragraph) -> str:
        """
        Extracts the text content from a paragraph in a Word document,
        performs optical character recognition (OCR) on any images present in
        the paragraph, and returns the recognized text
        """
        base64_images = self._extract_images(paragraph)
        ocr_text = run_ocr(base64_images)
        return ocr_text if ocr_text else paragraph.text.strip()

    def _is_start_of_chapter(self, text: str, index: int) -> bool:
        
        if index >= self.MAX_LINES_TO_CHECK:
            return False
        return (
            is_chapter(text)
            or not is_not_chapter(text, self.metadata)
        )
    
    def _process_text(self, paragraph_text: str, paragraph_index_of_chapter: int) -> Tuple[str, int]:
        """
        Process a paragraph's text to determine if it starts a new chapter and
        format it accordingly.

        Args:
            paragraph_text (str): The text of the paragraph to be processed.
            paragraph_index_of_chapter (int): The index of the paragraph
                within the current chapter.

        Returns:
            Tuple[str, int]: A tuple containing the processed text and the
                updated index of the paragraph within its chapter.
        """
        if self._is_start_of_chapter(
            paragraph_text,
            paragraph_index_of_chapter
        ):
            paragraph_index_of_chapter = 0
            processed_text = (
                "***" if self.pages
                else self.clean_text(paragraph_text)
            )
        else:
            processed_text = paragraph_text
        return processed_text, paragraph_index_of_chapter
    
    def split_chapters(self) -> str:
        """Splits the paragraph list into chapters."""
        self.pages: list = []
        current_page: list = []
        paragraph_index_of_chapter: int = 0

        for paragraph in self.paragraphs:
            paragraph_text = self.extract_text(paragraph)
            paragraph_index_of_chapter += 1

            if self._contains_page_break(paragraph):
                self.pages.append("\n".join(current_page))
                current_page = []
                paragraph_index_of_chapter = 0

            elif paragraph_text:
                processed_text, paragraph_index_of_chapter = self._process_text(paragraph_text, paragraph_index_of_chapter)
                current_page.append(processed_text)

        if current_page:
            self.pages.append("\n".join(current_page))
        return "\n".join(self.pages)
    
def read_docx(file_path: str, metadata: dict) -> str:
    """
    Reads the contents of a DOCX file, preprocesses it, and returns it as a string.
    
    Args:
        file_path (str): The path to the DOCX file.
        metadata (dict): Metadata about the document.
        
    Returns:
        str: The processed text of the DOCX file formatted into chapters.
    """
    docx_converter = DocxConverter(file_path, metadata)
    return docx_converter.split_chapters()