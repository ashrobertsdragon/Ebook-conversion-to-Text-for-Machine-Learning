from ebook2text._types import Tag
from ebook2text.abstract_book import ImageExtraction
from ebook2text.ocr import encode_image_file


class EpubImageExtractor(ImageExtraction):
    """
    Extracts images from an EPUB file.
    """

    def extract_images(self, element: Tag) -> list:
        """
        Extracts images from the EPUB file.

        Args:
            element: The element containing the image data.

        Returns:
            list: A list of encoded image data.
        """
        if element.name != "img":
            raise ValueError("Element is not an image")
        return [encode_image_file(element.string)]
