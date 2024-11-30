import pytest

from ebook2text.text_parser import TextParser


@pytest.fixture
def text_parser():
    return TextParser()


class TestParseTextFile:
    CHAPTER_BREAK = "***\n"

    def test_parse_text_file_with_chapters(self, text_parser):
        book_content = (
            "Chapter 1\n"
            "Some text.\n"
            "Chapter 2\n"
            "More ‘text’.\n"  # Includes smart punctuation
        )

        expected = f"{self.CHAPTER_BREAK}Some text.\n{self.CHAPTER_BREAK}More 'text'.\n"

        assert text_parser.parse_file(book_content) == expected

    def test_parse_text_file_no_chapters(self, text_parser):
        book_content = (
            "Some text.\n" "More ‘text’.\n"  # Includes smart punctuation
        )
        expected = "Some text.\nMore 'text'.\n"
        assert text_parser.parse_file(book_content) == expected

    def test_parse_text_file_empty(self, text_parser):
        assert text_parser.parse_file("") == ""

    def test_parse_text_file_with_roman_chapter(self, text_parser):
        book_content = "I\nSome text."
        expected = f"{self.CHAPTER_BREAK}Some text."
        assert text_parser.parse_file(book_content) == expected

    def test_parse_text_file_with_spelled_chapter(self, text_parser):
        book_content = "One\nSome text."
        expected = f"{self.CHAPTER_BREAK}Some text."
        assert text_parser.parse_file(book_content) == expected
