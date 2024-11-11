from ebook2text.text_conversion import (
    clean_chapter_breaks,
    clean_text,
    desmarten_text,
    parse_text_file,
    remove_leading_chapter_breaks,
    remove_whitespace,
)


class TestDesmartenText:
    def test_desmarten_text_basic(self):
        text = "Hello ‘world’! “This” is a test."
        expected = "Hello 'world'! \"This\" is a test."
        assert desmarten_text(text) == expected

    def test_desmarten_text_all_chars(self):
        text = (
            "‘quoted’ “double quoted” – en dash — em dash … ellipsis • bullet"
        )
        expected = "'quoted' \"double quoted\" - en dash - em dash ... ellipsis * bullet"
        assert desmarten_text(text) == expected

    def test_desmarten_text_no_smart_punctuation(self):
        text = "This is a regular sentence."
        assert desmarten_text(text) == text  # No change expected


class TestCleanChapterBreaks:
    CHAPTER_BREAK = "***\n"

    def test_clean_chapter_breaks_two(self):
        text = f"Some text.{self.CHAPTER_BREAK}{self.CHAPTER_BREAK}Some text."
        expected = f"Some text.{self.CHAPTER_BREAK}Some text."
        assert clean_chapter_breaks(text) == expected

    def test_clean_chapter_breaks_multiple(self):
        text = f"Some text.{self.CHAPTER_BREAK}{self.CHAPTER_BREAK}{self.CHAPTER_BREAK}Some text."
        expected = f"Some text.{self.CHAPTER_BREAK}Some text."
        assert clean_chapter_breaks(text) == expected

    def test_clean_chapter_breaks_no_change(self):
        text = f"Some text.{self.CHAPTER_BREAK}Some text."
        assert clean_chapter_breaks(text) == text


class TestRemoveLeadingChapterBreaks:
    CHAPTER_BREAK = "***\n"

    def test_remove_leading_chapter_breaks(self):
        text = f"{self.CHAPTER_BREAK}Some text."
        expected = "Some text."
        assert remove_leading_chapter_breaks(text) == expected

    def test_remove_leading_chapter_breaks_no_change(self):
        text = "Some text."
        assert remove_leading_chapter_breaks(text) == text


class TestCleanText:
    CHAPTER_BREAK = "***\n"

    def test_clean_text_multiple_chapter_breaks_with_whitespace(self):
        text = (
            f"Some text.{self.CHAPTER_BREAK}\n{self.CHAPTER_BREAK}Some text."
        )
        expected = f"Some text.{self.CHAPTER_BREAK}Some text."
        assert clean_text(text) == expected

    def test_clean_text_multiple_leading_chapter_breaks(self):
        text = f"{self.CHAPTER_BREAK}{self.CHAPTER_BREAK}Some text."
        expected = "Some text."
        assert clean_text(text) == expected

    def test_leaves_expected_chapter_breaks(self):
        text = f"Some text.{self.CHAPTER_BREAK}{self.CHAPTER_BREAK}Some text.{self.CHAPTER_BREAK}Some text."
        expected = f"Some text.{self.CHAPTER_BREAK}Some text.{self.CHAPTER_BREAK}Some text."
        assert clean_text(text) == expected

    def test_clean_text_no_extra_whitespace(self):
        text = "This is a normal sentence."
        assert clean_text(text) == text

    def test_clean_text_empty(self):
        assert clean_text("") == ""


class TestRemoveWhitespace:
    CHAPTER_BREAK = "***\n"

    def test_remove_whitespace_basic(self):
        text = "  This  is   a  test.  "
        expected = "This is a test."
        assert remove_whitespace(text) == expected

    def test_remove_whitespace_chapter_breaks(self):
        text = f"String 1.{self.CHAPTER_BREAK}\nString 2."
        expected = f"String 1.{self.CHAPTER_BREAK}String 2."
        assert remove_whitespace(text) == expected

    def test_remove_whitespace_no_extra_whitespace(self):
        text = "This is a normal sentence."
        assert remove_whitespace(text) == text


class TestParseTextFile:
    CHAPTER_BREAK = "***\n"

    def test_parse_text_file_with_chapters(self):
        book_content = (
            "Chapter 1\n"
            "Some text.\n"
            "Chapter 2\n"
            "More ‘text’.\n"  # Includes smart punctuation
        )

        expected = f"{self.CHAPTER_BREAK}Some text.\n{self.CHAPTER_BREAK}More 'text'.\n"

        assert parse_text_file(book_content) == expected

    def test_parse_text_file_no_chapters(self):
        book_content = (
            "Some text.\n" "More ‘text’.\n"  # Includes smart punctuation
        )
        expected = "Some text.\nMore 'text'.\n"
        assert parse_text_file(book_content) == expected

    def test_parse_text_file_empty(self):
        assert parse_text_file("") == ""

    def test_parse_text_file_with_roman_chapter(self):
        book_content = "I\nSome text."
        expected = f"{self.CHAPTER_BREAK}Some text."
        assert parse_text_file(book_content) == expected

    def test_parse_text_file_with_spelled_chapter(self):
        book_content = "One\nSome text."
        expected = f"{self.CHAPTER_BREAK}Some text."
        assert parse_text_file(book_content) == expected
