import re
from .chapter_check import is_chapter


def desmarten_text(book_content: str) -> str:
    """
    Replace smart punctuation in the given text with regular ASCII punctuation.
    Arguments:
        book_content (str): The input text containing smart punctuation.
    Returns str: The text with smart punctuation replaced by regular punctuation.
    """

    punctuation_map = str.maketrans({
        "‘": "'",
        "’": "'",
        "“": '"',
        "”": '"',
        "–": "-",
        "—": "-",
        "…": "...",
        "•": "*"
    })
    return book_content.translate(punctuation_map)

def remove_whitespace(full_text: str) -> str:
    full_text = re.sub(r"\s+", " ", full_text)
    if full_text.startswith("\n***\n"):
        full_text = full_text.lstrip("\n***\n")
    full_text = re.sub(r"\n***\n\n***\n", r"\n***\n", full_text)
    return full_text

def parse_text_file(book_content: str) -> str:
    """
    Parses the book content, replacing chapter headers with asterisks and applying text standardization.
    Args:
        book_content: The entire content of the book as a string.
    Returns the processed book content as a string.
    """
    book_lines = book_content.split("\n")
    parsed_lines = [
        "\n***\n" if is_chapter(line) else desmarten_text(line)
        for line in book_lines
    ]
    return "\n".join(parsed_lines)
