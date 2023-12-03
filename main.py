import os
import re
from typing import Tuple

import docx
import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub
from PyPDF2 import PdfReader

from common_functions import read_text_file, write_json_file, write_to_file

NOT_CHAPTER = ["about", "acknowledgements", "afterward", "annotation", "appendix", "assessment", "backmatter", "bibliography", "colophon", "conclusion", "contents", "contributors", "copyright", "cover", "credits", "dedication", "division", "endnotes", "epigraph", "errata", "footnotes", "forward", "frontmatter", "glossary", "imprintur", "imprint", "index", "introduction", "landmarks", "list", "notice", "page", "preamble", "preface", "prologue", "question", "rear", "revision", "table", "toc", "volume", "warning"]

def roman_to_int(roman: str) -> str:
  """
  Convert a Roman numeral to an integer.

  Arguments:
    roman (str): A string representing the Roman numeral.
  
  Returns int: The integer value of the Roman numeral.
  """

  roman_numerals = {
    'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000
  }

  roman = roman.upper()

  total = 0
  prev_value = 0

  for char in reversed(roman):
    value = roman_numerals[char]

    if value < prev_value:
      total -= value
    else:
      total += value

    prev_value = value

  if not total:
    raise ValueError("Unknown number word")


  return str(total)

def word_to_num_str(number_str: str) -> str:
  """
  Convert a spelled-out number without spaces or hyphens to a string of the integer.  The function supports numbers from 0 to 99 and is case insensitive.

  Argumentss:
    number_str (str): A string representing the spelled-out number.

  Returns str: The string representation of the integer value of the spelled-out number.
  """

  num_words = {
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
    'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
    'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
    'fourteen': 14, 'fifteen': 15, 'sixteen': 16,
    'seventeen': 17, 'eighteen': 18, 'nineteen': 19
  }

  tens_words = {
    'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
    'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90
  }

  number_str = number_str.lower()

  total = 0
  temp_word = ''

  for char in number_str:
    temp_word += char

    if temp_word in num_words:
      total += num_words[temp_word]
      temp_word = ''
    elif temp_word in tens_words:
      total += tens_words[temp_word]
      temp_word = ''

  if temp_word:
      raise ValueError(f"Unknown number word: {temp_word}")


  return str(total)

def is_chapter(s: str) -> bool:
  """
  Check if a string contains the word 'chapter', a Roman numeral, a spelled-out number, or a digit.

  Args:
    s (str): The string to check.

  Returns bool: True if the string meets the criteria, False otherwise.
  """

  def is_number(s: str) -> bool:
    """
    Check if a string contains a number value either as digits, roman numerals, or spelled-out numbers.
    """

    
    return s.isdigit() or is_roman_numeral(s) or is_spelled_out_number(s):
  
  def is_roman_numeral(word: str) -> bool:
 
    try:
        roman_to_int(word)

      
        return True
    
    except ValueError:
    
      
      return False

  def is_spelled_out_number(word: str) -> bool:
    """Try to convert the word to an integer. If it's not a valid spelled-out number, it will raise a ValueError"""
    
    try:
      word_to_num_str(word)
      
      
      return True

    except ValueError:
    
      
      return False

  words = s.lower().split()

  
  return any(word == "chapter" or is_number(word) for word in words)

def convert_chapter_break(book_content: str) -> str:
  """
  Converts chapter breaks to three askerisks
  
  Arguments:
  book_content: The content of the book.
  
  Returns the book content with askerisks for chapter breaks."""

  book_lines = book_content.split("\n")
  for i, line in enumerate(book_lines):
    if is_chapter(line) and i != 0:
      book_lines[i] = "***"


  return "\n".join(book_lines)

def _extract_chapter_text(item) -> str:
  """
  Extracts text from a chapter item.

  Argumentss:
threa    item: ebooklib item representing a chapter.

  Returns string containing the text of the chapter.
  """

  soup = BeautifulSoup(item.content, "html.parser")
  elements = soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6"])

  for i, element in enumerate(elements[:3]):
    text = element.get_text().strip().lower()

    if any(non_chapter_word in text for non_chapter_word in NOT_CHAPTER):


     return ""

    if is_chapter(element):
      starting_line = i + 1


      return "\n".join(tag.get_text().strip() for tag in elements[starting_line:])


  return ""

def read_epub(file_path: str) -> Tuple[str, dict]:
  """
  Reads the contents of an epub file and returns it as a string.

  Arguments:
    file_path: Path to the epub file.

  Returns the contents of the epub file as a string.
  """
  
  book_content = ""
  chapter_contents = []
  metadata = {}

  book = epub.read_epub(file_path, options={"ignore_ncx": True})
  metadata['title'] = next((item[0] for item in book.get_metadata('DC', 'title')), None)
  metadata['author'] = next((item[0] for item in book.get_metadata('DC', 'creator')), None)

  for item in book.get_items():
    if item.get_type() == ebooklib.ITEM_DOCUMENT and not any(not_chapter_word in item.file_name.lower() for not_chapter_word in NOT_CHAPTER):
      chapter_contents.append(_extract_chapter_text(item))
      
  book_content = "\n***\n".join(chapter_contents)


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