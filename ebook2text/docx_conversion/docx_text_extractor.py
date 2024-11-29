from ebook2text._types import Paragraph
from ebook2text.abstract_book import TextExtraction
from ebook2text.docx_conversion import DocxConverter
from ebook2text.ocr import run_ocr


class DocxTextExtractor(TextExtraction):
    """
    Class dedicated to extracting and processing text from docx Paragraphs.
    """

    def __init__(self, converter: DocxConverter):
        self.converter = converter

    def extract_text(self, paragraph: Paragraph) -> str:
        """
        Extracts the text content from the paragraph, performs OCR on any
        images present, and returns whichever is not empty.

        Args:
            paragraph: The Paragraph object containing the text and formatting.

        Returns:
            str: The extracted and processed text.
        """
        ocr_text = self._extract_image_text(paragraph)
        paragraph_text = paragraph.text.strip()
        return ocr_text or paragraph_text

    def _extract_image_text(self, paragraph: Paragraph) -> str:
        """
        Extracts text from images within the paragraph using OCR.
        """
        if base64_images := self.converter.extract_images(paragraph):
            return run_ocr(base64_images)
        return ""
