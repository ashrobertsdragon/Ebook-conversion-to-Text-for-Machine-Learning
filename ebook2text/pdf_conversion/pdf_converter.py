import re
from pathlib import Path
from typing import Generator, List

from pdfminer.high_level import extract_pages

from ebook2text import logger
from ebook2text._types import LTPage
from ebook2text.abstract_book import BookConversion, TextExtraction
from ebook2text.pdf_conversion._enums import LineAction, LineType
from ebook2text.pdf_conversion.pdf_line_logic import check_line, compare_lines


class PDFConverter(BookConversion):
    """
    PDFConverter class for converting PDF files to text and images.

    This class provides methods for extracting text and images from PDF files.
    It includes functions for processing PDF layout elements, extracting
    images in base64 format, running OCR on images, splitting text into
    paragraphs, and checking for chapter boundaries.

    Args:
        file_path (str): Path to the PDF file.
        metadata (dict): Dictionary with title and author name.
    """

    SENTENCE_PUNCTUATION: tuple = (".", "!", "?", '."', '!"', '?"')

    def __init__(
        self, file_path: Path, metadata: dict, text_extractor: TextExtraction
    ):
        super().__init__(file_path, metadata, text_extractor)
        self.pages = self._objects
        self.chapter_separator = f"{self.CHAPTER_SEPARATOR}\n"
        self._page: List[str] = []

    def _read_file(self, file_path: Path) -> Generator[LTPage, None, None]:
        """
        Read the PDF file using PDFMiner.Six extract_pages function.

        Args:
            file_path (str): Path to the PDF file.

        Returns:
            List[LTPage]: List of page objects.
        """
        try:
            yield from extract_pages(file_path, maxpages=25)
        except Exception as e:
            logger.error(f"Error reading PDF file: {e}")

    def ends_with_punctuation(self, text: str) -> bool:
        """Checks if text ends with sentence punctuation"""
        return text.rstrip().endswith(self.SENTENCE_PUNCTUATION)

    def is_title_page(self, page_lines: list[str]) -> bool:
        """
        Determines if the page is a title page by comparing the number of lines in
        the page to a threshold.
        """
        return len(page_lines) < self.MAX_LINES_TO_CHECK

    @staticmethod
    def split_line(line: str) -> list[str]:
        """Split the line at newline characters."""
        return line.split("\n")

    def add_line_to_page(self, line: str) -> None:
        self._page.append(line + "\n") if self.ends_with_punctuation(
            line
        ) else self._page.append(line)

    def _process_page_text(self, page_lines: list[str], metadata: dict) -> str:
        """
        Process the text of a page.

        Args:
            page_lines (list[str]): The lines of the page.
            metadata (dict): The metadata dictionary.

        Returns:
            str: The processed text of the page.
        """
        checked: int = 0
        index: int = 0
        previous_line_value: LineType = LineType.UNINITIALIZED
        last_action: LineAction = LineAction.UNINITIALIZED

        while index < len(page_lines):
            split_lines = self.split_line(page_lines[index])
            if len(split_lines) > 1:
                page_lines[index : index + 1] = split_lines

            line = page_lines[index].strip("\r\n").lstrip()
            index += 1
            if not line:
                continue

            if checked < self.MAX_LINES_TO_CHECK:
                checked += 1
                line_value: LineType = check_line(line, metadata)
                action = compare_lines(
                    previous_line=previous_line_value,
                    current_line=line_value,
                    last_action=last_action,
                )
                last_action = action
                previous_line_value = line_value

                if action == LineAction.RETURN_EMPTY:
                    return ""
                elif action in (LineAction.FIRST_LINE, LineAction.CONTINUE):
                    continue
                elif action == LineAction.ADD_SEPARATOR:
                    self._page.append(self.chapter_separator)
            self.add_line_to_page(line)
        # after all lines run through `split_line`
        return "" if self.is_title_page(page_lines) else "".join(self._page)

    @staticmethod
    def remove_extra_whitespace(text: str) -> str:
        text = re.sub(r"\n+", "\n", text)
        return re.sub(r"[ ]{2,}", " ", text)

    def parse_file(self) -> Generator[str, None, None]:
        for page in self.pages:
            page_text = self._process_page_text(
                self.text_extractor.extract_text(page), self.metadata
            )
            self._page = []
            yield self.remove_extra_whitespace(page_text)

    def _clean_output_before_write(self, output: str, file_path: Path) -> str:
        return (
            output
            if file_path.exists()
            else output.lstrip(self.chapter_separator)
        )

    def write_text(self, output: str, file_path: Path) -> None:
        """
        Write the parsed text to a file.

        Args:
            output (str): The parsed text to be written to the file.
            file_path (Path): The path to the output file.
        """
        with file_path.open("a", encoding="utf-8") as f:
            f.write(self._clean_output_before_write(output, file_path))

    def return_string(self, output: Generator[str, None, None]) -> str:
        """Return the parsed text as a string."""
        return "".join(output)
