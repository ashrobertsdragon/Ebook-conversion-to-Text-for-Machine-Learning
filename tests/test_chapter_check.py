import pytest

from ebook2text.chapter_check import (
    is_chapter,
    is_not_chapter,
    is_number,
    is_roman_numeral,
    is_spelled_out_number,
    roman_to_int,
    word_to_num,
)


class TestRomanToInt:
    def test_valid_roman_numerals(self):
        assert roman_to_int("I") == 1
        assert roman_to_int("IV") == 4
        assert roman_to_int("IX") == 9
        assert roman_to_int("X") == 10
        assert roman_to_int("XL") == 40
        assert roman_to_int("XC") == 90
        assert roman_to_int("C") == 100
        assert roman_to_int("CD") == 400
        assert roman_to_int("CM") == 900
        assert roman_to_int("M") == 1000
        assert roman_to_int("MCMXCIX") == 1999

    def test_invalid_roman_numerals(self):
        with pytest.raises(ValueError):
            roman_to_int("IIII")  # Too many consecutive I's
        with pytest.raises(ValueError):
            roman_to_int("VV")  # Duplicate V
        with pytest.raises(ValueError):
            roman_to_int("VX")  # Invalid subtraction
        with pytest.raises(ValueError):
            roman_to_int("IC")  # Invalid subtraction
        with pytest.raises(ValueError):
            roman_to_int("IM")  # Invalid subtraction
        with pytest.raises(ValueError):
            roman_to_int("A")  # Invalid character
        with pytest.raises(ValueError):
            roman_to_int("")  # Empty string

    def test_wrong_type(self):
        with pytest.raises(TypeError):
            roman_to_int(123)


class TestWordToNum:
    def test_valid_numbers(self):
        assert word_to_num("zero") == 0
        assert word_to_num("one") == 1
        assert word_to_num("twenty-one") == 21
        assert word_to_num("Thirty-Five") == 35  # Case-insensitive
        assert word_to_num("ninety-nine") == 99

    def test_invalid_numbers(self):
        with pytest.raises(ValueError):
            word_to_num("onehundred")
        with pytest.raises(ValueError):
            word_to_num("blah")
        with pytest.raises(ValueError):
            word_to_num("")

    def test_wrong_type(self):
        with pytest.raises(TypeError):
            word_to_num(123)


class TestIsSpelledOutNumber:
    def test_valid_spelled_out_numbers(self):
        assert is_spelled_out_number("one")
        assert is_spelled_out_number("twenty-five")

    def test_invalid_spelled_out_numbers(self):
        assert not is_spelled_out_number("onehundred")
        assert not is_spelled_out_number("blah")


class TestIsRomanNumeral:
    def test_valid_roman_numerals(self):
        assert is_roman_numeral("I")
        assert is_roman_numeral("XIV")

    def test_invalid_roman_numerals(self):
        assert not is_roman_numeral("IIII")
        assert not is_roman_numeral("blah")


class TestIsNumber:
    def test_digits(self):
        assert is_number("123")

    def test_roman_numerals(self):
        assert is_number("XIV")

    def test_spelled_out_numbers(self):
        assert is_number("twenty-five")

    def test_invalid_numbers(self):
        assert not is_number("blah")


class TestIsChapter:
    def test_chapter_prefix(self):
        assert is_chapter("Chapter 1")

    def test_roman_numeral(self):
        assert is_chapter("I")

    def test_spelled_out_number(self):
        assert is_chapter("one")

    def test_digit(self):
        assert is_chapter("1")

    def test_invalid_chapter(self):
        assert not is_chapter("Introduction")


class TestIsNotChapter:
    def test_title_match(self):
        assert is_not_chapter("My Awesome Book", {"title": "My Awesome Book"})

    def test_author_match(self):
        assert is_not_chapter("John Doe", {"author": "John Doe"})

    def test_not_chapter_word(self):
        assert is_not_chapter("Introduction", {})
        assert is_not_chapter("Appendix A", {})

    def test_no_match(self):
        assert not is_not_chapter("Chapter 1", {})
