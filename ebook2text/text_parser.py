from pathlib import Path
from typing import Generator

from ebook2text.chapter_check import is_chapter
from ebook2text.text_utilities import clean_text, desmarten_text


class TextParser:
    def __init__(self, file_path: Path):
        self.file_path: Path = file_path
        self.chapter_separator: str = "***"

    def read_line(self) -> Generator[str, None, None]:
        with self.file_path.open("r", encoding="utf-8") as f:
            yield from f

    def parse_file(self) -> Generator[str, None, None]:
        """
        Parses the book lines, replacing chapter headers with asterisks and
        applying text standardization.

        Yields a line-by-line of the processed book content as a string.
        """
        for line in self.read_line():
            parsed_line = (
                self.chapter_separator
                if is_chapter(line)
                else desmarten_text(line)
            )

            yield clean_text(parsed_line)

    def write_text(self, content: str, file_path: Path) -> None:
        """
        Write the parsed text to a file.

        Args:
            text (str): The parsed text to be written to the file.
        """
        with file_path.open("a", encoding="utf-8") as f:
            f.write(content + "\n")

    def return_string(self, generator: Generator[str, None, None]) -> str:
        """Return the parsed text as a string."""
        return "\n".join(generator)
