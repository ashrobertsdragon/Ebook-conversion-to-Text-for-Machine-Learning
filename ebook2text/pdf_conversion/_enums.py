from enum import Enum


class LineType(Enum):
    UNINITIALIZED = 0
    HEADER = 1
    CHAPTER = 2
    NOT_CHAPTER = 3
    LINE = 4


class LineAction(Enum):
    UNINITIALIZED = 0
    FIRST_LINE = 1
    RETURN_EMPTY = 2
    CONTINUE = 3
    ADD_SEPARATOR = 4
    ADD_LINE = 5
