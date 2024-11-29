from ebook2text.docx_conversion.docx_chapter_splitter import (
    DocxChapterSplitter,
)
from ebook2text.docx_conversion.docx_converter import DocxConverter
from ebook2text.docx_conversion.docx_image_extractor import DocxImageExtractor
from ebook2text.docx_conversion.docx_text_extractor import DocxTextExtractor

__all__ = [
    "DocxConverter",
    "DocxImageExtractor",
    "DocxTextExtractor",
    "DocxChapterSplitter",
    "read_docx",
]


def read_docx(file_path: str, metadata: dict) -> str:
    """
    Reads the contents of a DOCX file and returns the processed text.

    Args:
        file_path (str): The path to the DOCX file.
        metadata (dict): Metadata about the document.

    Returns:
        str: The processed text of the DOCX file formatted into chapters.
    """
    docx_converter = DocxConverter(file_path, metadata)
    return docx_converter.split_chapters()
