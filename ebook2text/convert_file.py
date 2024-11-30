from pathlib import Path
from typing import Union

from ebook2text.abstract_book import BookConversion
from ebook2text.docx_conversion import _initialize_docx_converter
from ebook2text.epub_conversion import _initialize_epub_converter
from ebook2text.pdf_conversion import _initialize_pdf_converter
from ebook2text.text_parser import TextParser


def _initialize_converter(
    file_path: Path, metadata: dict, extension: str
) -> Union[BookConversion, TextParser]:
    if extension == ".epub":
        return _initialize_epub_converter(file_path, metadata)
    elif extension == ".pdf":
        return _initialize_pdf_converter(file_path, metadata)
    elif extension == ".docx":
        return _initialize_docx_converter(file_path, metadata)
    elif extension in {"txt", "text"}:
        return TextParser(file_path)
    raise ValueError(f"Unsupported file type: {extension}")


def _parse_file_path(file_path: Path) -> Path:
    folder = file_path.parent
    book_name = (
        file_path.stem.replace(" ", "_").replace("-", "_").replace(".", "_")
    )
    almost_path = folder / book_name
    return almost_path.with_suffix(".txt")


def convert_file(
    file_path: Path,
    metadata: dict,
    *,
    save_file: bool = True,
    save_path: Union[Path, None] = None,
) -> Union[str, None]:
    """
    Converts a book to a text file with 3 asterisks for chapter breaks
    Args:
        book_name: Name of the book.
        folder_name: Name of the folder containing the book.
    """
    extension = file_path.suffix.lower()
    converter = _initialize_converter(file_path, metadata, extension)
    for content in converter.parse_file():
        if save_file:
            path = save_path or _parse_file_path(file_path)
            converter.write_text(content, path)
            string_output = None
        else:
            string_output = converter.return_string(content)
    return string_output
