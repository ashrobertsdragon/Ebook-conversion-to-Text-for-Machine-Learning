from ebook2text.chapter_check import is_chapter, is_not_chapter
from ebook2text.pdf_conversion._enums import LineAction, LineType


def is_header(line: str, metadata: dict[str, str]) -> bool:
    """
    Determines if the line is part of the page header by checking if it starts
    or ends with the title or author.
    """
    return (
        line.startswith(metadata["title"])
        or line.endswith(metadata["title"])
        or line.startswith(metadata["author"])
        or line.endswith(metadata["author"])
    )


def check_line(line: str, metadata: dict[str, str]) -> LineType:
    """
    Check if the line indicates something special should be done.

    This function calls is_header(), is_chapter(), and is_not_chapter() to
    determine if the line is a chapter marker, the marker of a page that is
    not a chapter - such as frontmatter or backmatter -, part of the page
    header, or a regular line.

    Args:
        line (str): The line to check.
        metadata (dict[str, str]): The metadata dictionary.
        header_detected (bool): Whether the header has already been detected.

    Returns:
        tuple[LineType, bool]: A tuple containing an enum of line type and a
            boolean indicating whether the header has been detected.
    """
    if is_header(line, metadata):
        return LineType.HEADER
    if is_chapter(line):
        return LineType.CHAPTER
    elif is_not_chapter(line, metadata):
        return LineType.NOT_CHAPTER
    return LineType.LINE


def compare_lines(
    *, previous_line: LineType, current_line: LineType, last_action: LineAction
) -> LineAction:
    """
    Compare two line types and determine what action should be taken.

    Args:
        previous_line (LineType): The previous line type.
        current_line (LineType): The current line type.
        last_action (LineAction): The last action taken.

    Returns:
        LineAction: An enum of the action to take.
    """
    if (
        last_action == LineAction.FIRST_LINE
        and previous_line == LineType.CHAPTER
        and current_line == LineType.LINE
    ):
        return LineAction.ADD_SEPARATOR

    # Use a dictionary matrix using tuples of previous and current line types
    comparisons: dict[tuple[LineType, LineType], LineAction] = {
        # first line of page, can't make decision, unless LINE
        (LineType.UNINITIALIZED, LineType.CHAPTER): LineAction.FIRST_LINE,
        (LineType.UNINITIALIZED, LineType.HEADER): LineAction.FIRST_LINE,
        (LineType.UNINITIALIZED, LineType.NOT_CHAPTER): LineAction.FIRST_LINE,
        (LineType.UNINITIALIZED, LineType.LINE): LineAction.ADD_LINE,
        # identify the header across two lines
        (LineType.HEADER, LineType.CHAPTER): LineAction.CONTINUE,
        (LineType.CHAPTER, LineType.HEADER): LineAction.CONTINUE,
        # Return empty string if not a chapter
        (LineType.NOT_CHAPTER, LineType.LINE): LineAction.RETURN_EMPTY,
        # NOT_CHAPTER can be on later line
        (LineType.LINE, LineType.NOT_CHAPTER): LineAction.RETURN_EMPTY,
        # NOT_CHAPTER misidentified as HEADER
        # Probably a Section marker followed by chapter marker
        (LineType.CHAPTER, LineType.CHAPTER): LineAction.ADD_SEPARATOR,
        # Catching actual chapter marker above
        (LineType.CHAPTER, LineType.LINE): LineAction.ADD_LINE,
        # Two consecutive lines, just add the line
        (LineType.LINE, LineType.LINE): LineAction.ADD_LINE,
    }

    return comparisons.get((previous_line, current_line), LineAction.ADD_LINE)
