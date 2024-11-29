from ebook2text._types import EpubBook, EpubItem, Tag
from ebook2text.abstract_book import ImageExtraction
from ebook2text.ocr import encode_image_file


class EpubImageExtractor(ImageExtraction):
    """
    Extracts images from an EPUB file.
    """

    def __init__(self, book: EpubBook):
        self.book = book

    def extract_images(self, element: Tag) -> list:
        """
        Extracts images from the EPUB file.

        Args:
            element: The element containing the image data.

        Returns:
            list: A list of encoded image data.
        """
        image_data: EpubItem = self.book.get_item_with_href(element["src"])
        return [encode_image_file(image_data)]
