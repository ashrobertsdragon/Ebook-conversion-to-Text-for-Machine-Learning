from pathlib import Path
from typing import Generator

from ebook2text.epub_conversion.epub_converter import EpubConverter
from ebook2text.epub_conversion.epub_image_extractor import EpubImageExtractor
from ebook2text.epub_conversion.epub_text_extractor import EpubTextExtractor

__all__ = [
    "EpubConverter",
    "EpubImageExtractor",
    "EpubTextExtractor",
    "convert_epub",
    "_initialize_epub_converter",
]


def _initialize_epub_converter(
    file_path: Path, metadata: dict
) -> EpubConverter:
    image_extractor = EpubImageExtractor()
    text_extractor = EpubTextExtractor(image_extractor)
    return EpubConverter(file_path, metadata, text_extractor)


def convert_epub(
    file_path: Path, metadata: dict
) -> Generator[str, None, None]:
    """
    Reads an EPUB file and splits it into chapters.

    Args:
        file_path (str): The path to the EPUB file to be read.
        metadata (dict): A dictionary containing metadata such as title and
            author information.

    Returns:
        str: The cleaned text of the chapters separated by '***'.
    """
    image_extractor = EpubImageExtractor()
    text_extractor = EpubTextExtractor(image_extractor)
    epub_converter = EpubConverter(file_path, metadata, text_extractor)
    yield from epub_converter.parse_file()
