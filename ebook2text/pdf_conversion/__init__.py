from pathlib import Path
from typing import Generator

from ebook2text.pdf_conversion.pdf_converter import PDFConverter
from ebook2text.pdf_conversion.pdf_image_extractor import PDFImageExtractor
from ebook2text.pdf_conversion.pdf_text_extractor import PDFTextExtractor

__all__ = [
    "PDFConverter",
    "PDFImageExtractor",
    "PDFTextExtractor",
    "convert_pdf",
    "initialize_pdf_converter",
]


def initialize_pdf_converter(file_path: Path, metadata: dict):
    image_extractor = PDFImageExtractor(file_path)
    text_extractor = PDFTextExtractor(image_extractor)
    return PDFConverter(file_path, metadata, text_extractor)


def convert_pdf(file_path: Path, metadata: dict) -> Generator[str, None, None]:
    """
    A convenience function that reads a PDF file and splits its content into
    chapters based on chapter boundaries.
    This function initializes a PDFConverter object with the provided file
    path and metadata. It then calls the 'split_chapters' method of the
    PDFConverter instance to extract text from the PDF, identify chapter
    boundaries, and split the content into chapters. The resulting text,
    representing the split chapters, is returned as a single string.
    Args:
        file_path (str): The path to the PDF file to be read.
        metadata (dict): A dictionary containing metadata such as title and
            author information.

    Returns:
        str: The content of the PDF file split into chapters based on chapter
            boundaries.
    """
    pdf_converter = initialize_pdf_converter(file_path, metadata)

    yield from pdf_converter.parse_file()
