import base64
import logging
import re
from io import BytesIO
from typing import Any, List, Tuple, Union

from pdfminer.high_level import extract_pages
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import resolve1
from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import PDFStream
from PIL import Image

from ._exceptions import ImageTooLargeError, ImageTooSmallError
from ._types import LTChar, LTContainer, LTPage, LTText
from .abstract_book import (
    BookConversion,
    ChapterSplit,
    ImageExtraction,
    TextExtraction,
)
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
    """

    SENTENCE_PUNCTUATION: set = {".", "!", "?", '."', '!"', '?"'}

    def _read_file(self, file_path: str) -> List[LTPage]:
        """
        Read the PDF file using PDFMiner.Six extract_pages function.

        Args:
            file_path (str): Path to the PDF file.

        Returns:
            List[LTPage]: List of page objects.
        """
        try:
            return list(extract_pages(file_path))
        except Exception as e:
            logging.error(f"Error reading PDF file: {e}")
            return []

    def extract_images(self, obj_nums: list) -> list:
        """
        Extract images from the PDF based on object numbers.

        Args:
            obj_nums (list): List of object numbers to extract images from.

        Returns:
            list: List of extracted images.
        """
        image_extractor = PDFImageExtractor(self.file_path)
        return image_extractor.extract_images(obj_nums)

    def extract_text(self, page: LTPage) -> str:
        """
        Extract text from a given page.

        Args:
            page (LTPage): Page object to extract text from.

        Returns:
            str: Extracted text from the page.
        """
        text_extractor = PDFTextExtractor(self)
        return text_extractor.extract_text(page)

    def split_chapters(self) -> str:
        """
        Split the text into chapters using PDFChapterSplitter.

        Returns:
            str: Split text into chapters.
        """
        splitter = PDFChapterSplitter(self.book, self.metadata, self)
        return splitter.split_chapters()

    def ends_with_punctuation(self, text: str) -> bool:
        """Checks if text ends with sentence punctuation"""
        return any(
            text.rstrip().endswith(p) for p in self.SENTENCE_PUNCTUATION
        )


class PDFChapterSplitter(ChapterSplit):
    """
    Initializes the PDFChapterSplitter object.

    Args:
        book (SplitType): The PDF document to process.
        metadata (dict): Necessary metadata for processing.
        converter: The converter object.
    """

    def __init__(
        self, book: List[LTPage], metadata: dict, converter: PDFConverter
    ):
        super().__init__(book, metadata, converter)
        self.book: List[LTPage] = self.text_obj

        # Without this, MyPy throws bad errror about missing method in parent
        self.converter: PDFConverter = converter

    def _process_text(self, page_text: str) -> str:
        """
        Parses the given pdf page and returns it as a string.
        Args:
            page_text: A pdf page.
        Returns the pdf page as a string.
        """
        pages: List[str] = []
        paragraph_lines: List[str] = []
        lines: List[str] = page_text.split("\n")

        for line in lines:
            stripped = line.strip()
            if stripped:
                cleaned = self.clean_text(line)
                paragraph_lines.append(cleaned)
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

    def _process_paragraph(self, paragraph_lines: List[str]) -> str:
        """
        Processes a list of paragraph lines to filter out chapter boundaries
        and clean the text.

        Args:
            paragraph_lines (list): A list of lines forming a paragraph.

        Returns:
            str: The cleaned paragraph string with chapter boundaries marked.
        """
        checked: int = 0
        paragraph: list = []

        for orig_line in paragraph_lines:
            line = orig_line.strip()
            if line and checked < self.MAX_LINES_TO_CHECK:
                checked += 1
                if is_not_chapter(line, self.metadata):
                    return ""
                if is_chapter(line):
                    line = self.CHAPTER_SEPARATOR
            paragraph.append(line)
        return "".join(paragraph)

    def split_chapters(self) -> str:
        """
        Splits the PDF content into chapters based on chapter boundaries.

        Returns:
            str: The PDF content split into chapters based on chapter
                boundaries.

        Raises:
            Exception: If an error occurs during text extraction or
                processing.
        """
        text_parts: list = []
        for page in self.book:
            extracted_page = self.converter.extract_text(page)
            processed_page = self._process_text(extracted_page)
            if extracted_page:
                text_parts.append(
                    processed_page
                    if self.converter.ends_with_punctuation(processed_page)
                    else "\n" + processed_page
                )
        joined_parts = "".join(text_parts)
        return self._remove_extra_separators(joined_parts)

    def _remove_extra_separators(self, text: str) -> str:
        """
        Remove blank lines and chapter seperators from the beginning of the
        file if there are any using a regex pattern.
        """
        return re.sub(r"^(\*\*\*|\n)+", "", text)


class PDFTextExtractor(TextExtraction):
    """
    The PDFTextExtractor class implements the functionality to extract text
    from a PDF page, including OCR text from images.

    Methods:
        extract_text: Extracts text from a PDF page, including OCR text from
            images.
    """

    def __init__(self, converter: PDFConverter) -> None:
        self.converter = converter

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
        pdf_text_list: List[str] = []
        obj_nums: List[int] = []
        for element in page:
            obj_type, obj_data = self._process_element(element)
            match obj_type:
                case "image":
                    obj_nums.append(int(obj_data))
                case "text":
                    pdf_text_list.append(str(obj_data))
                case _:
                    pass
        ocr_text = self._extract_image_text(obj_nums)
        return (
            self._join_paragraph(pdf_text_list)
            if not ocr_text
            else ocr_text + "\n" + self._join_paragraph(pdf_text_list)
        )

    def _process_element(self, element: Any) -> Tuple[str, Union[int, str]]:
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
            Tuple[str, Union[int, str]]: A tuple containing the element
                type and its relevant data (object ID for images or text
                content for text elements), or None for other types.
        """
        if hasattr(element, "stream"):
            return "image", element.stream.objid
        elif isinstance(element, LTText) and not isinstance(element, LTChar):
            return "text", element.get_text()
        elif isinstance(element, LTContainer):
            for child in element:
                return self._process_element(child)
        return "other", ""

    def _join_paragraph(self, paragraph: List[str]) -> str:
        """
        Joins the list of paragraph lines processed by the
        '_process_paragraph' method based on whether the line ends in a
        punctuation mark or not.

        Args:
            paragraph (List[str]): A list of individual lines from a paragraph
                from a PDF file.
        Returns:
            str: A string of the joined lines of the paragraph.

        Note: The assumption is that if a line ends with a punctuation mark,
        it is also the end of the paragraph.
        """
        return "".join(
            line + "\n"
            if self.converter.ends_with_punctuation(line)
            else line + ""
            for line in paragraph
        )

    def _extract_image_text(self, obj_nums: List[int]) -> str:
        """Collect list of Base64 encoded images and run them through OCR"""
        base64_images = self.converter.extract_images(obj_nums)
        return run_ocr(base64_images)


class PDFImageExtractor(ImageExtraction):
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    """
    PDFImageExtractor class for extracting images from PDF objects.

    This class inherits from ImageExtraction and provides methods to process
    and extract images from PDF files based on the provided object numbers. It
    includes functionality to read the PDF file, retrieve image data, convert
    binary image data into base64-encoded JPEG strings, and handle exceptions
    related to image size.

    Methods:
        extract_images: Processes and extracts images from PDF objects based
            on the provided object numbers.

    Raises:
        ImageTooSmallError: If the image dimensions are too small.
        ImageTooLargeError: If the image dimensions are too large.
        TypeError: If an invalid object type is encountered during image
            retrieval.
        Exception: If there is an error in processing the image data.
    """

    def extract_images(self, obj_nums: List[int]) -> List[str]:
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
            obj_nums (List[int]): A list of object numbers corresponding to
            images in the PDF.

        Returns:
            List[str]: A list of base64-encoded strings representing the
                extracted images.
        """
        with open(self.file_path, "rb") as f:
            parser = PDFParser(f)
            self.document = PDFDocument(parser)
            base64_images: list = [
                self._get_image(obj_num, attempt=0) for obj_num in obj_nums
            ]
        return [image for image in base64_images if image]

    def _create_image_from_binary(
        self, stream: bytes, width: int, height: int
    ) -> str:
        """
        Convert binary image data into a base64-encoded JPEG string.

        Args:
            stream (bytes): The binary data of the image.
            width (int): The width of the image in pixels.
            height (int): The height of the image in pixels.

        Returns:
            str: A base64-encoded string representing the JPEG image.

        Raises:
            Exception: If there is an error in processing the image data.
        """
        try:
            image = Image.frombytes("1", (width, height), stream)
            image = image.convert("L")
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode("utf-8")
        except Exception as e:
            logging.exception(
                "Failed to create base64 encoded image due to %s", str(e)
            )
            return ""

    def _get_image(self, obj_num: int, attempt: int = 0) -> str:
        """
        Processes and retrieves images from a PDF object.

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
                    raise ImageTooSmallError(
                        "Image too small. Not target image"
                    )
                if width > 1000 and height > 1000:
                    raise ImageTooLargeError("probably full page image")
                stream = obj.get_data()
                return self._create_image_from_binary(stream, width, height)
            else:
                obj_typ = type(obj)
                raise TypeError(
                    f"Invalid object. Received {obj_typ} instead of PDFStream"
                )
        except TypeError as e:
            logging.exception("TypeError: %s", str(e))
            return ""
        except ImageTooSmallError as e:
            logging.info(f"Issue: {e} with object: {obj_num}")
            return self._get_image(obj_num + 1, attempt + 1)
        except ImageTooLargeError as e:
            logging.info(f"Issue: {e} with object: {obj_num}")
            return self._get_image(obj_num + 1, attempt + 1)


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
