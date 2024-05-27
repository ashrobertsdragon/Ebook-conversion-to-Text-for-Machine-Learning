import base64
import logging
from io import BytesIO
from typing import Any, Optional, Tuple, Union

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTChar, LTContainer, LTPage, LTText
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import resolve1
from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import PDFStream
from PIL import Image

from .abstract_book import BookConversion
from .chapter_check import is_chapter, is_not_chapter
from .ocr import run_ocr


class PDFConverter(BookConversion):
    """
    PDFConverter class for converting PDF files to text and images.

    This class provides methods for extracting text and images from PDF files.
    It includes functions for processing PDF layout elements, extracting
    images in base64 format, running OCR on images, splitting text into
    paragraphs, and checking for chapter boundaries.

    Args:
        file_path (str): Path to the PDF file.
        metadata (dict): Dictionary with title and author name.

    Attributes:
        MAX_LINES_TO_CHECK (int): Maximum number of lines to check for chapter
            identification.

    Methods:
        extract_text: Extracts text from a PDF page,including OCR text from
            images.
        split_chapters: Splits the PDF content into chapters based on chapter
            boundaries.

    Raises:
        Exception: If there is an error in processing image data or text
            extraction.
    """

    def _read_file(self, file_path: str) -> list:
        """Read the PDF file using PDFMiner.Six extract_pages function"""
        return extract_pages(file_path)

    def _create_image_from_binary(
        self, stream: bytes, width: int, height: int
    ) -> str:
        """
        Convert binary image data into a base64-encoded JPEG string.

        This function takes binary data of an image, along with its width and
            height, and converts it into a base64-encoded JPEG format string.

        Args:
            stream (bytes): The binary data of the image.
            width (int): The width of the image in pixels.
            height (int): The height of the image in pixels.

        Returns
            str: A base64-encoded string representing the JPEG image.

        Raises:
            Exception: If there is an error in processing the image data.
        """
        try:
            image: Image = Image.frombytes("1", (width, height), stream)
            image = image.convert("L")
            buffered: BytesIO = BytesIO()
            image.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode("utf-8")
        except Exception as e:
            logging.exception(
                "failed to create base64 encoded image due to %s", str(e)
            )

    def _get_image(self, obj_num: int, attempt: Optional[int] = 0) -> str:
        """
        Processes and retrieves images from a PDF object.

        Attempts to retrieve an image from a PDF object identified by the
        object number. It checks the dimensions of the image and ensures it
        meets certain criteria before converting the binary image data into a
        base64-encoded JPEG format string.

        Args:
            obj_num (int): The object number of the PDF image to retrieve.
            attempt (Optional[int]): The number of attempts made to retrieve
                the image (default is 0).

        Returns:
            str: A base64-encoded string representing the JPEG image if
                successful, otherwise an empty string.

        Raises:
            Exception: If there is an error in processing the image data or if
                the image does not meet the required criteria.
        """
        if attempt > 1:
            return ""
        try:
            obj: object = resolve1(self.document.getobj(obj_num))
            if obj and isinstance(obj, PDFStream):
                width: int = obj["Width"]
                height: int = obj["Height"]
                if width < 5 or height < 5:
                    raise Exception("Image too small. Not target image")
                if width > 1000 and height > 1000:
                    raise Exception("probably full page image")
                stream: PDFStream = obj.get_data()
                return self._create_image_from_binary(stream, width, height)
        except Exception as e:
            logging.info(f"Issue: {e} with object: {obj_num}")
            return self._get_image(obj_num + 1, attempt + 1)

    def _extract_images(self, obj_nums: list) -> list:
        """
        Processes and extracts images from PDF objects based on the provided
        object numbers.

        This method reads the PDF file, initializes a PDF parser, and iterates
        through the list of object numbers. For each object number, it
        attempts to retrieve the image data using the '_get_image' method. If
        successful, the binary image data is converted into a base64-encoded
        JPEG format string and added to the list. The final output is a list
        of base64-encoded strings representing the images extracted from the
        PDF.

        Args:
            obj_nums (list): A list of object numbers corresponding to images
                in the PDF.

        Returns:
            list: A list of base64-encoded strings representing the extracted
                images.
        """
        with open(self.file_path, "rb") as f:
            parser: PDFParser = PDFParser(f)
            self.document: PDFDocument = PDFDocument(parser)
            base64_images: list = []
            for obj_num in obj_nums:
                image: str = self._get_image(obj_num, attempt=0)
                base64_images.append(image) if image else None
        return base64_images

    def _extract_text_from_image(self, obj_nums: list) -> str:
        """Collect list of Base64 encoded images and run them through OCR"""
        base64_images: list = self._extract_images(obj_nums)
        return run_ocr(base64_images)

    def _process_element(self, element: Any) -> Tuple[str, Union[Any, None]]:
        """
        Processes a PDF layout element to identify its type and extract
        relevant data.

        This function categorizes a given PDF layout element into types such
        as image, text, or other. For image elements, it returns the object
        ID. For text elements, it returns the extracted text. The function
        handles container elements by recursively processing their children.
        If an element does not match any specific type, it is categorized as
        "other".

        Args:
            element (Any): A PDF layout element from pdfminer.

        Returns:
            A tuple containing the element type and its relevant data (object
                ID for images or text content for text elements), or None for
                other types.
        """
        if hasattr(element, "stream"):
            return ("image", element.stream.objid)
        elif isinstance(element, LTText) and not isinstance(element, LTChar):
            return ("text", element.get_text())
        elif isinstance(element, LTContainer):
            for child in element:
                return self._process_element(child)
        return ("other", None)

    def extract_text(self, page: LTPage) -> str:
        """
        Extracts text from a PDF page, including OCR text from images.

        This method processes a given PDF page represented by the LTPage
        object. It iterates through the elements on the page, categorizes them
        as images or text using the '_process_element' method, and collects
        the object numbers of images and text content. For text elements, it
        appends the extracted text to a list after checking for the presence
        of actual text. If the element is an image, it adds the object number
        to a separate list. After processing all elements, it calls the
        '_extract_text_from_image' method to extract text from images using
        OCR. Finally, it combines the OCR text with the extracted text content
        from the page and returns the concatenated result as a single string.

        Args:
            page (LTPage): The PDF page represented as an LTPage object.

        Returns:
            str: The extracted text content from the PDF page, including OCR
                text from images.
        """
        pdf_text_list: list = []
        obj_nums: list = []
        for element in page:
            obj_tuple = self._process_element(element)
            if obj_tuple[0] == "image":
                obj_nums.append(obj_tuple[1])
            elif obj_tuple[0] == "text":
                pdf_text_list.append(obj_tuple[1])
        ocr_text = self._extract_text_from_image(obj_nums)
        return (
            self._join_paragraph(pdf_text_list)
            if (ocr_text is None or ocr_text == "")
            else ocr_text + "\n" + self._join_paragraph(pdf_text_list)
        )

    def _join_paragraph(self, paragraph: list) -> str:
        """
        Joins the list of paragraph lines processed by the '_process_paragraph'
        method based on whether the line ends in a punctuation mark or not.

        Args:
            paragraph (list): A list of individual lines from a paragraph
                from a PDF file.
        Returns:
            A string of the joined lines of the paragraph.

        Note: The assumption is that if a line ends with a punctuation mark,
        it is also the end of the paragraph.
        """
        return "".join(
            line + "\n" if self._ends_with_punctuation(line) else line + ""
            for line in paragraph
        )

    def _process_text(self, page_text) -> str:
        """
        Parses the given pdf page and returns it as a string.
        Args:
            page_text: A pdf page.
        Returns the pdf page as a string.
        """

        pages: list = []
        paragraph_lines: list = []

        lines: list = page_text.split("\n")

        for line in lines:
            if line.strip():
                paragraph_lines.append(self.clean_text(line))
            elif paragraph_lines:
                paragraph = self._process_paragraph(paragraph_lines)
                if paragraph:
                    pages.append(paragraph)
                    paragraph_lines = []

        if paragraph_lines:
            paragraph = self._process_paragraph(paragraph_lines)
            if paragraph:
                pages.append(paragraph)

        return "\n".join(pages)

    def _process_paragraph(self, paragraph_lines: list) -> str:
        """
        Processes a list of paragraph lines to filter out chapter boundaries
        and clean the text.

        This method takes a list of lines representing a paragraph and
        iterates through each line. It checks if the line is not empty and has
        not exceeded the maximum lines to check limit. If the line is
        identified as a chapter boundary based on the 'is_chapter' and
        'is_not_chapter' functions, it replaces the line with a chapter
        separator. The processed lines are then joined to form a cleaned
        paragraph string.

        Args:
            paragraph_lines (list): A list of lines forming a paragraph.

        Returns:
            str: The cleaned paragraph string with chapter boundaries marked.
        """
        checked: int = 0
        paragraph: list = []

        for line in paragraph_lines:
            if line.strip() and checked < self.MAX_LINES_TO_CHECK:
                checked += 1
                if is_not_chapter(line, self.metadata):
                    return ""
                elif is_chapter(line):
                    line = "\n***\n"
                paragraph.append(line)
        return "\n".join(paragraph) or ""

    def _ends_with_punctuation(self, text: str) -> bool:
        """Checks if text ends with sentence punctuation"""
        SENTENCE_PUNCTUATION: set = {".", "!", "?", '."', '!"', '?"'}
        return any(text.rstrip().endswith(p) for p in SENTENCE_PUNCTUATION)

    def _split_book(self) -> str:
        """
        Splits the PDF content into chapters based on chapter boundaries.

        This method iterates through each page of the PDF document, extracts
        text using the 'extract_text' method, and processes the text content
        to identify and mark chapter boundaries. It then combines the
        processed text into chapters based on the identified boundaries. If a
        page ends with punctuation, it is considered as the end of a chapter.
        The resulting text parts are stored in a list and concatenated to form
        the final string representing the split chapters.

        Returns:
            str: The PDF content split into chapters based on chapter
                boundaries.

        Raises:
            Exception: If an error occurs during text extraction or
                processing.
        """
        text_parts = []
        for page in self.book:
            page_text: str = self.extract_text(page)
            pdf_page: str = self._process_text(page_text)
            if pdf_page:
                text_parts.append(
                    pdf_page
                    if self._ends_with_punctuation(pdf_page)
                    else "\n" + pdf_page
                )
        self._parsed_book = "".join(text_parts)


def read_pdf(file_path: str, metadata: dict) -> str:
    """
    Reads a PDF file and splits its content into chapters based on chapter
    boundaries.
    This function initializes a PDFConverter object with the provided file
    path and metadata. It then calls the 'split_chapters' method of the
    PDFConverter instance to extract text from the PDF, identify chapter
    boundaries, and split the content into chapters. The resulting text,
    representing the split chapters, is returned as a single string.
    Args:
        file_path (str): The path to the PDF file to be read.
        metadata (dict): A dictionary containing metadata such as title and
            author information.

    Returns:
        str: The content of the PDF file split into chapters based on chapter
            boundaries.
    """
    pdf_converter = PDFConverter(file_path, metadata)
    return pdf_converter.split_chapters()
