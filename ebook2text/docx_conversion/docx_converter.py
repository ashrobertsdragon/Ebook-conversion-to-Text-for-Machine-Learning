from typing import List

import docx

from ebook2text._types import Document, Paragraph
from ebook2text.abstract_book import BookConversion
from ebook2text.docx_conversion import (
    DocxChapterSplitter,
    DocxImageExtractor,
    DocxTextExtractor,
)


class DocxConverter(BookConversion):
    """
    Class to convert a Word document to structured text.

    Attributes:
        file_path (str): The path to the Word document.
        metadata (dict): Metadata related to the document.
        doc (Document): The parsed Word document object.
        paragraphs (list): List of paragraphs objects extracted from the
            document.
    """

    def __init__(self, file_path: str, metadata: dict):
        """
        Initializes the DocxConverter with file path and metadata.
        """
        super().__init__(file_path, metadata)
        self.paragraphs: list = self.extract_paragraphs()

    def _read_file(self, file_path: str) -> Document:
        """
        Reads a Word document from the specified file path.

        Returns:
            Document: The parsed Word document object.
        """
        return docx.Document(file_path)

    def extract_paragraphs(self) -> list:
        """
        Extracts paragraphs from the Word document.

        Returns:
            list: A list of paragraph objects extracted from the document.
        """
        return self.book.paragraphs

    def extract_images(self, paragraph: Paragraph) -> List[str]:
        image_extractor = DocxImageExtractor()
        return image_extractor.extract_images(paragraph)

    def extract_text(self, paragraph: Paragraph) -> str:
        text_extractor = DocxTextExtractor(self)
        return text_extractor.extract_text(paragraph)

    def split_chapters(self) -> str:
        """
        Splits the paragraphs into chapters using the ChapterSplitter.
        """
        splitter = DocxChapterSplitter(self.paragraphs, self.metadata, self)
        return splitter.split_chapters()
