from ebook2text._types import Tag
from ebook2text.abstract_book import TextExtraction
from ebook2text.epub_conversion import EpubConverter
from ebook2text.ocr import run_ocr


class EpubTextExtractor(TextExtraction):
    """
    Extracts text from EPUB elements, handling image OCR.
    """

    def __init__(self, converter: EpubConverter):
        self.converter = converter

    def extract_text(self, element: Tag) -> str:
        """
        Extracts text from an element, using OCR for images.

        Args:
            element: The element from which text needs to be extracted.
            book (EpubBook): The EpubBook object for accessing image data.

        Returns:
            str: The extracted text from the element.
        """
        if element.name == "img":
            return self._extract_image_text(element)
        else:
            return self._extract_text(element)

    def _extract_image_text(self, element: Tag) -> str:
        base64_images: list = self.converter.extract_images(element)
        return run_ocr(base64_images)

    def _extract_text(self, element: Tag) -> str:
        return element.get_text().strip()
