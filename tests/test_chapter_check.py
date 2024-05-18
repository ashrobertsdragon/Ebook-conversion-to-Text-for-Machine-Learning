import pytest
from ebook_conversion.chapter_check import roman_to_int, word_to_num, is_number, is_chapter, is_not_chapter, NOT_CHAPTER

IS_NOT_CHAPTER_TEST_METADATA = {
    "title": "Test Book",
    "author": "John Doe"
}

def test_roman_to_int_valid():
    assert roman_to_int('III') == 3
    assert roman_to_int('IV') == 4
    assert roman_to_int('IX') == 9
    assert roman_to_int('LVIII') == 58
    assert roman_to_int('MCMXCIV') == 1994
    assert roman_to_int('MMMCMXCIX') == 3999

def test_roman_to_int_invalid_strings():
    with pytest.raises(ValueError):
        roman_to_int('IIII')
    with pytest.raises(ValueError):
        roman_to_int('VX')
    with pytest.raises(ValueError):
        roman_to_int('A') 
    with pytest.raises(ValueError):
        roman_to_int('')
    with pytest.raises(ValueError):
        roman_to_int('MMMM')

def test_roman_to_int_invalid_types():
    with pytest.raises(ValueError):
        roman_to_int(123)
    with pytest.raises(ValueError):
        roman_to_int(['X', 'V']) 
    with pytest.raises(ValueError):
        roman_to_int(None)
    with pytest.raises(ValueError):
        roman_to_int(12.34)

def test_word_to_num_zero():
    assert word_to_num("zero") == 0

def test_word_to_num_single_digit():
    assert word_to_num("five") == 5
    assert word_to_num("NINE") == 9

def test_word_to_num_teen():
    assert word_to_num("eleven") == 11
    assert word_to_num("NINETEEN") == 19

def test_word_to_num_two_digit():
    assert word_to_num("twentythree") == 23
    assert word_to_num("FORTYFIVE") == 45

def test_word_to_num_two_words():
    assert word_to_num("sixtynine") == 69
    assert word_to_num("NINETYTWO") == 92

def test_word_to_num_invalid_input():
    with pytest.raises(ValueError):
        word_to_num("onehundred")

    with pytest.raises(ValueError):
        word_to_num("twenty-three")

    with pytest.raises(ValueError):
        word_to_num("abc")

def test_word_to_num_empty_input():
    with pytest.raises(ValueError):
        word_to_num("")

@pytest.mark.parametrize("input_str, expected_output", [
    ("42", True),
    ("XLII", True),
    ("forty-two", True),
    ("hello", False),
    ("", False)
])
def test_is_number(input_str, expected_output):
    assert is_number(input_str) == expected_output

@pytest.mark.parametrize("input_str, expected_output", [
    ("Chapter 1", True),
    ("chapter XII", True),
    ("twenty-three", True),
    ("23", True),
    ("Introduction", False),
    ("This is a paragraph", False),
    ("", False)
])
def test_is_chapter(input_str, expected_output):
    assert is_chapter(input_str) == expected_output

def test_is_chapter_case_insensitive():
    assert is_chapter("CHAPTER XIII") is True
    assert is_chapter("SEVENTYTWO") is True

def test_is_chapter_with_leading_spaces():
    assert is_chapter("   chapter XIV") is True
    assert is_chapter("    seventy-five") is True
    assert is_chapter("   This is not a chapter") is False

@pytest.mark.parametrize("paragraph, expected_output", [
    ("Preface", True),
    ("INTRODUCTION", True),
    ("acknowledgments", True),
    ("Dedication", True),
    ("Prologue", True),
    ("Test Book", True),
    ("John Doe", True),
    ("Chapter 1", False),
    ("This is a regular paragraph.", False)
])
def test_is_not_chapter(paragraph, expected_output):
    metadata = IS_NOT_CHAPTER_TEST_METADATA.copy()
    result = is_not_chapter(paragraph, metadata)
    assert result == expected_output

def test_is_not_chapter_no_metadata():
    metadata = {}
    paragraph = "Preface"
    result = is_not_chapter(paragraph, metadata)
    assert result is True

def test_is_not_chapter_case_insensitive():
    metadata = TEST_METADATA.copy()
    paragraph = "PROLOGUE"
    result = is_not_chapter(paragraph, metadata)
    assert result is True

def test_is_not_chapter_customized_words():
    not_chapter_words = NOT_CHAPTER.copy()
    not_chapter_words.append("appendix")
    metadata = TEST_METADATA.copy()
    paragraph = "Appendix A"
    result = is_not_chapter(paragraph, metadata, not_chapter_words=not_chapter_words)
    assert result is True

