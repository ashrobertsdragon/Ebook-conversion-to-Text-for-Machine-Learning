import os
import re
from typing import Tuple

import docx
import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub
from PyPDF2 import PdfReader

from common_functions import read_text_file, write_json_file, write_to_file

CHAPTER_PATTERN = re.compile(r"^\s*chapter\s|\schapter\s*$", re.IGNORECASE)

def detect_chapter(line: str) -> bool:
  """
  Detects if a line is a chapter header.
  """
  return CHAPTER_PATTERN.match(line) is not None

def convert_chapter_break(book_content: str) -> str:
  """
  Converts chapter breaks to three askerisks
  
  Arguments:
  book_content: The content of the book.
  
  Returns the book content with askerisks for chapter breaks."""

  book_lines = book_content.split("\n")
  for i, line in enumerate(book_lines):
    if detect_chapter(line) and i != 0:
      book_lines[i] = "***"


  return "\n".join(book_lines)  

def read_epub(file_path: str) -> Tuple[str, dict]:
  """
  Reads the contents of an epub file and returns it as a string.

  Arguments:
    file_path: Path to the epub file.

  Returns the contents of the epub file as a string.
  """
  
  book_content = ""
  chapter_files = []
  combined_content = []
  metadata = {}

  book = epub.read_epub(file_path, options={"ignore_ncx": True})
  metadata['title'] = next((item[0] for item in book.get_metadata('DC', 'title')), None)
  metadata['author'] = next((item[0] for item in book.get_metadata('DC', 'creator')), None)

  blacklist = ["about", "acknowledgements", "afterward", "annotation", "appendix", "assessment", "backmatter", "bibliography", "colophon", "conclusion", "contents", "contributors", "copyright", "cover", "credits", "dedication", "division", "endnotes", "epigraph", "errata", "footnotes", "forward", "frontmatter", "glossary", "imprintur", "imprint", "index", "introduction", "landmarks", "list", "notice", "page", "preamble", "preface", "prologue", "question", "rear", "revision", "table", "toc", "volume", "warning"]

  for item in book.get_items():
    if item.get_type() == ebooklib.ITEM_DOCUMENT:
      item_href = item.file_name
      if not any(blacklist_word in item_href.lower() for blacklist_word in blacklist):
        chapter_files.append(item_href)  

  for chapter in chapter_files:
    item = book.get_item_with_href(chapter)
    soup = BeautifulSoup(item.content, "html.parser")
    elements = soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6"])
    starting_line = None
    blacklist_found = False

    for i, element in enumerate(elements[:3]):
      text = element.get_text().strip().lower()
      if any(blacklist_word in text for blacklist_word in blacklist):
        blacklist_found = True
        break
      if ("chapter" in text or re.search(r"\d+", text)) and not starting_line:
        starting_line = i + 1

    if starting_line and not blacklist_found:
      chapter_text = "\n".join(tag.get_text().strip() for tag in elements[starting_line:])
      combined_content.append(chapter_text)

  book_content = "\n***\n".join(combined_content)

  return book_content, metadata


def read_docx(file_path: str) -> Tuple[str, dict]:
  """
  Reads the contents of a docx file and returns it as a string.
  
  Arguments:
    file_path: Path to the docx file.

  Returns the contents of the docx file as a string.
  """
  
  metadata = {}

  doc = docx.Document(file_path)
  
  book_content = "\n".join([paragraph.text for paragraph in doc.paragraphs])

  core_properties = doc.core_properties
  metadata["title"] = core_properties.title if core_properties.title else None
  metadata["author"] = core_properties.author if core_properties.author else None


  return book_content, metadata
 
def read_pdf(file_path: str) -> Tuple[str, str]:
  """
  Reads the contents of a pdf file and returns it as a string.
  
  Arguments:
    file_path: Path to the pdf file.
  
  Returns the contents of the pdf file as a string.
  """

  metadata = {}
  
  pdf = PdfReader(file_path)
  book_content = "\n".join([page.extract_text() for page in pdf.pages])

  doc_info = pdf.metadata

  if doc_info:
    metadata["title"] = doc_info.get("title")
    metadata["author"] = doc_info.get("author")

  return book_content, metadata

def convert_file(book_name: str, folder_name: str) -> None:
  """
  Converts a book to a text file with 3 asterisks for chapter breaks
  
  Arguments:
    book_name: Name of the book.
    folder_name: Name of the folder containing the book.

  Reutrns the name of the text file.
  """

  book_content = ""
  file_path = f"{folder_name}/{book_name}"

  book_name = book_name.replace(" ", "_")
  book_name = book_name.replace("-", "_")
  filename_list = book_name.split(".")
  if len(filename_list) > 1:
    base_name = "_".join(filename_list[:-1])
  else:
    base_name = filename_list[0]
  extension = filename_list[-1]
  
  if extension == "epub":
    book_content, metadata = read_epub(file_path)
  elif extension == "docx":
    book_content, metadata = read_docx(file_path)
  elif extension == "pdf":
    book_content, metadata = read_pdf(file_path)
  elif extension == "txt" or extension == "text":
    book_content = read_text_file(file_path)
    metadata = {}
  else:
    print("Invalid filetype")
    exit()

  # book_content = convert_chapter_break(book_content)

  book_name = f"{base_name}.txt"
  write_to_file(book_content, book_name)
  if metadata:
    write_json_file(metadata, f"metadata_{book_name}.json")

folder_name = "folder"

for book_name in os.listdir(folder_name):
  convert_file(book_name, folder_name)