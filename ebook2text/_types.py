from typing import List, Union

from docx import Document
from docx.text.paragraph import Paragraph
from ebooklib.epub import EpubBook
from pdfminer.layout import LTChar, LTContainer, LTPage, LTText
from pdfminer.pdftypes import PDFStream

SplitType = Union[List[Paragraph], EpubBook, List[LTPage]]

__all__ = [
    "Document",
    "EpubBook",
    "LTChar",
    "LTContainer",
    "LTText",
    "LTPage",
    "PDFStream",
    "Paragraph",
    "SplitType",
]
