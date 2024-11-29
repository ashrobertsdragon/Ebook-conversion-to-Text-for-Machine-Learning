import base64
from typing import List

from ebook2text import logger
from ebook2text._namespaces import docx_ns_map
from ebook2text._types import Paragraph
from ebook2text.abstract_book import ImageExtraction


class DocxImageExtractor(ImageExtraction):
    """
    A class dedicated to extracting images from docx Paragraph objects.
    """

    def __init__(self):
        self.paragraph: Paragraph = None

    def extract_images(self, paragraph: Paragraph) -> List[str]:
        """
        Extracts and converts images found in the paragraph into
        base64-encoded strings.

        Returns:
            list: A list of base64-encoded strings, each representing an image
                extracted from the paragraph.
        """
        self.paragraph = paragraph
        image_blobs: list = self._extract_image_blobs()
        return self._build_base64_images_list(image_blobs)

    def _build_base64_images_list(self, image_streams: list) -> list:
        """
        Converts image blobs to base64-encoded strings.

        Args:
            image_blobs (list): A list of extracted image streams.

        Returns:
            list: A list of base64-encoded strings representing the images.
        """
        return [
            base64.b64encode(image).decode("utf-8") for image in image_streams
        ]

    def _extract_image_blobs(self) -> list:
        """
        Extracts image blobs from the paragraph.

        Returns:
            list: A list of image blobs extracted from the paragraph.
        """
        namespace: dict = docx_ns_map
        image_blobs: list = []

        blips = self.paragraph._p.findall(".//a:blip", namespaces=namespace)
        for blip in blips:
            try:
                rId = blip.attrib[f"{{{namespace['r']}}}embed"]
                image_part = self.paragraph.part.related_parts[rId]
                image_blobs.append(image_part.blob)
            except (KeyError, ValueError, AttributeError) as e:
                logger.exception(f"Corrupted image data: {str(e)}")
        return image_blobs
