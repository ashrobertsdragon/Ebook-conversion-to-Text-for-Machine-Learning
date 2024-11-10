import re

from .chapter_check import is_chapter


def desmarten_text(book_content: str) -> str:
    """
    Replace smart punctuation in the given text with regular ASCII
    punctuation.
    Args:
        book_content (str): The input text containing smart punctuation.
    Returns:
        (str) The text with smart punctuation replaced by regular punctuation.
    """

    punctuation_map = str.maketrans(
        {
            "‘": "'",
            "’": "'",
            "“": '"',
            "”": '"',
            "–": "-",
            "—": "-",
            "…": "...",
            "•": "*",
        }
    )
    return book_content.translate(punctuation_map)


def clean_chapter_breaks(full_text: str, chapter_break: str = "***\n") -> str:
    """
    Replace chapter breaks in the given text with a single chapter break.
    Args:
        full_text: The input text containing chapter breaks.
        chapter_break: The string representing a chapter break.
    Returns:
        The text with chapter breaks replaced by a single chapter break.
    """
    escaped_break = re.escape(chapter_break)
    return re.sub(f"(?:{escaped_break})+", chapter_break, full_text)


def remove_leading_chapter_breaks(
    full_text: str, chapter_break: str = "***\n"
) -> str:
    """
    Remove leading chapter breaks from the given text.
    Args:
        full_text: The input text containing leading chapter breaks.
    Returns:
        The text with leading chapter breaks removed.
    """
    return (
        full_text.removeprefix(chapter_break)
        if full_text.startswith(chapter_break)
        else full_text
    )


def remove_whitespace(full_text: str) -> str:
    """
    Remove extra whitespace from the given text.
    Args:
        full_text: The input text with extra whitespace.
    Returns:
        The text with extra whitespace removed.
    """
    return re.sub(r"(\s)+", r"\1", full_text.strip())


def clean_text(full_text: str) -> str:
    """
    Clean the given text by removing leading chapter breaks, chapter breaks,
    and extra whitespace.
    Args:
        full_text: The input text to be cleaned.
    Returns:
        The cleaned text.
    """
    return remove_leading_chapter_breaks(
        clean_chapter_breaks(remove_whitespace(full_text))
    )


def parse_text_file(book_content: str) -> str:
    """
    Parses the book content, replacing chapter headers with asterisks and
    applying text standardization.
    Args:
        book_content: The entire content of the book as a string.
    Returns the processed book content as a string.
    """
    book_lines = book_content.split("\n")
    parsed_lines = [
        "***" if is_chapter(line) else desmarten_text(line)
        for line in book_lines
    ]
    book_text = "\n".join(parsed_lines)
    return clean_text(book_text)
