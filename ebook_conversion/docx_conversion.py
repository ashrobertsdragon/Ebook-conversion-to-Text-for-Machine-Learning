import base64
from io import BytesIO

import docx

from .chapter_check import is_chapter
from .ocr import run_ocr
from .text_conversion import desmarten_text


def contains_page_break(paragraph: str) -> bool:
  """
  Checks if the given paragraph contains a page break.
  Arguments:
    paragraph: A paragraph from a docx document.

  Returns True if a page break is found, False otherwise.
  """

  for run in paragraph.runs:
    if "<w:lastRenderedPageBreak/>" in run._element.xml or "<w:br " in run.element.xml:
      return True
  return False

def extract_images(paragraph, doc) -> str:
  for run in paragraph.runs:
    for inline_shape in run.element.findall(".//a:blip", namespaces=docx.oxml.ns.nsmap):
      image_blip = inline_shape.get('{http://schemas.openxmlformats.org/drawingml/2006/main}embed')
      image_part = doc.part.related_parts[image_blip]
      stream = BytesIO(image_part.blob)
      base64_images = [base64.b64encode(stream.read().decode("utf-8"))]
      ocr_text = run_ocr(base64_images)
      if ocr_text:
        return ocr_text
      else:
        return ""

def read_docx(file_path: str, metadata: dict) -> str:
  """
  Reads the contents of a docx file and returns it as a string.
  Arguments:
    file_path: Path to the docx file.
  Returns the contents of the docx file as a string.
  """

  current_page = []
  pages = []
  line_counter = 0
  max_lines_to_check = 3
  chapter_header = False
  not_chapter_flag = False
  doc = docx.Document(file_path)
  for paragraph in doc.paragraphs:
    if line_counter < max_lines_to_check:
      ocr_text = extract_images(paragraph)
    paragraph_text = ocr_text if ocr_text else paragraph.text.strip()
    if contains_page_break(paragraph) and current_page:
      pages.append("\n".join(current_page))
      chapter_header = False
      not_chapter_flag = False
      current_page = []
      line_counter = 0
    if not paragraph_text:
      continue
    elif is_chapter(paragraph_text):
      chapter_header = True
      not_chapter_flag = False
      if pages:
        paragraph_text = "***"
      else:
        continue
    elif line_counter < max_lines_to_check and not chapter_header and is_not_chapter(paragraph_text, metadata):
      not_chapter_flag = True
      current_page = []
      continue
    elif not_chapter_flag is True:
        continue
    paragraph_text = desmarten_text(paragraph_text)
    current_page.append(paragraph_text)
    line_counter += 1
  if current_page:
    pages.append("\n".join(current_page))   
  return "\n".join(pages)