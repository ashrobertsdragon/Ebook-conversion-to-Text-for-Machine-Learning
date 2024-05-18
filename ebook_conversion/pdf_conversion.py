import base64
import logging
import re
from io import BytesIO
from typing import Any, Tuple, Union

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import resolve1
from pdfminer.pdftypes import PDFStream
from pdfminer.layout import LTChar, LTContainer, LTText
from pdfminer.high_level import extract_pages
from PIL import Image

from .chapter_check import is_chapter, is_not_chapter
from .ocr import run_ocr
from .text_conversion import desmarten_text


error_logger = logging.getLogger("error_logger")
info_logger = logging.getLogger("info_logger")

def create_image_from_binary(binary_data, width: int, height: int) -> str:
  """
  Create an image from binary data.

  Arguments:
    binary_data (bytes): The binary data of the image.
    width (int): The width of the image.
    height (int): The height of the image.

  Returns str: The string representation of the image.
  """
  try:
    image = Image.frombytes('1', (width, height), binary_data)
    image = image.convert('L')
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    image = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return image
  except Exception as e:
    error_logger.exception(f"failed to create base64 encoded image due to {e}")

def extract_image(document: bytes, obj_num: int, attempt: int) -> str:
  """
  Convert binary image data into a base64-encoded JPEG string.

  This function takes binary data of an image, along with its width and 
  height, and converts it into a base64-encoded JPEG format string. This is 
  useful for encoding images in a format that can be easily transmitted or 
  stored.

  Arguments:
    binary_data (bytes): The binary data of the image.
    width (int): The width of the image in pixels.
    height (int): The height of the image in pixels.

  Returns str: A base64-encoded string representing the JPEG image.

  Raises:
    Exception: If there is an error in processing the image data.
  """

  if attempt > 1:
    return None
  try:
    obj = resolve1(document.getobj(obj_num))
    if obj and isinstance(obj, PDFStream):
      width = obj["Width"]
      height = obj["Height"]
      if width < 5 or height < 5:
        raise Exception("Image too small. Not target image")
      if width > 1000 and height > 1000:
        raise Exception("probably full page image")
      stream = obj.get_data()
      return create_image_from_binary(stream, width, height)
  except Exception as e:
    info_logger.info(f"Issue: {e} with object: {obj_num}")
    return extract_image(document, obj_num + 1, attempt + 1)

def parse_img_obj(file_path: str, obj_nums: list) -> str:
  """
  Extracts and processes images from a PDF file, then performs OCR to convert
  images to text.

  This function takes the path of a PDF file and a list of object numbers
  (obj_nums) which are potential image objects within the PDF. It attempts 
  to extract images from these objects and then uses OCR to convert these 
  images into text. The text from all images is concatenated and returned 
  as a single string.

  Arguments:
    file_path (str): The file path to the PDF from which to extract images.
    obj_nums (list): A list of object numbers in the PDF that potentially
    contain images.

  Returns text (str): the concatenated text extracted from all images.
  """

  with open(file_path, 'rb') as f:
    parser = PDFParser(f)
    document = PDFDocument(parser)
    base64_images = []
    for obj_num in obj_nums:
      image = extract_image(document, obj_num, attempt = 0)
      base64_images.append(image) if image else None
  text = run_ocr(base64_images) if base64_images else ""
  return text

def process_element(element: Any) -> Tuple[str, Union[Any, None]]:
  """
  Processes a PDF layout element to identify its type and extract relevant
  data.

  This function categorizes a given PDF layout element into types such as
  image, text, or other. For image elements, it returns the object ID. For
  text elements, it returns the extracted text. The function handles
  container elements by recursively processing their children. If an element
  does not match any specific type, it is categorized as "other".

  Arguments:
    element (Any): A PDF layout element from pdfminer.

  Returns: A tuple containing the element type and its relevant data (object
    ID for images or text content for text elements), or None for other types.
  """

  if hasattr(element, "stream"):
    return ("image", element.stream.objid)
  elif isinstance(element, LTText) and not isinstance(element, LTChar):
    return ("text", element.get_text())
  elif isinstance(element, LTContainer):
    for child in element:
      return process_element(child)
  return ("other", None)

def parse_pdf_page(page: str, metadata: dict) -> str:
  """
  Parses the given pdf page and returns it as a string.
  Arguments:
    page: A pdf page.
  Returns the pdf page as a string.
  """

  page_list = []
  paragraph_list = []

  def parse_paragraph(paragraph_list: list) -> str:
    """
    Check if the first three lines of text contain a identifier for a page
    unrelated to the chapter, or a chapter heading.
    If not a chapter, return an empty list. If a chapter heading, replace with
    three asterisks. Otherwise concantate line to paragraph string and add to
    page list
    """

    text_lines = 0
    paragraph = ""

    for line in paragraph_list:
      if line.strip() or text_lines < 3:
        if is_not_chapter(paragraph, metadata):
          return ""
        elif is_chapter(paragraph):
          return "\n***\n"
      paragraph += line
      text_lines += 1
    return paragraph

  lines = page.split("\n")

  for line in lines:
    if line.strip():
      paragraph_list.append(desmarten_text(line))
    elif paragraph_list:
      paragraph = parse_paragraph(paragraph_list)
      if paragraph:
        page_list.append(paragraph)
        paragraph_list = []
      else:
        return ""

  if paragraph_list:
    paragraph = parse_paragraph(paragraph_list)
    if paragraph:
      page_list.append(paragraph)
    else:
      return ""

  return "\n".join(page_list)

def read_pdf(file_path: str, metadata: dict) -> str:
  """
  Reads the contents of a pdf file and returns it as a string.
  Arguments:
    file_path: Path to the pdf file.
    metadata: Dictionary containing the title and author of the file.
  Returns the contents of the pdf file as a string.
  """

  full_text = ""
  for page in extract_pages(file_path):
    pdf_text = ""
    obj_nums = []
    for element in page:
      obj_tuple = process_element(element)
      if obj_tuple[0] == "image":
        obj_nums.append(obj_tuple[1])
      elif obj_tuple[0] == "text":
        pdf_text += obj_tuple[1] + "\n" if obj_tuple[1] != "No text found" else ""
    ocr_text = parse_img_obj(file_path, obj_nums)
    page_text = ocr_text + "\n" + pdf_text if ocr_text is not None else pdf_text
    pdf_page = parse_pdf_page(page_text, metadata)
    if pdf_page:
      if pdf_page.rstrip().endswith(('.', '!', '?', '."', '!"', '?"')):
        full_text += pdf_page
      else:
        full_text += "\n" + pdf_page
  full_text = re.sub(r"\s+", " ", full_text)
  if full_text.startswith("\n***\n"):
    full_text = full_text.lstrip("\n***\n")

  return full_text