from epub_chapter_splitter import EpubChapterSplitter
from epub_converter import EpubConverter
from epub_image_extractor import EpubImageExtractor
from epub_text_extractor import EpubTextExtractor

__all__ = [
    "EpubChapterSplitter",
    "EpubConverter",
    "EpubImageExtractor",
    "EpubTextExtractor",
    "read_epub",
]


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
    epub_converter = EpubConverter(file_path, metadata)
    return epub_converter.split_chapters()
