import os

import docx
import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub
from PyPDF2 import PdfReader

from common_functions import read_text_file, write_to_file

NOT_CHAPTER = ["about", "acknowledgements", "afterward", "annotation", "appendix", "assessment", "backmatter", "bibliography", "colophon", "conclusion", "contents", "contributors", "copyright", "cover", "credits", "dedication", "division", "endnotes", "epigraph", "errata", "footnotes", "forward", "frontmatter", "glossary", "imprintur", "imprint", "index", "introduction", "landmarks", "list", "notice", "page", "preamble", "preface", "prologue", "question", "rear", "revision", "sign up", "table", "toc", "volume", "warning"]

def roman_to_int(roman: str) -> int:
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
    if char not in roman_numerals:
      raise ValueError("not Romman numeral")
    value = roman_numerals[char]

    if value < prev_value:
      total -= value
    else:
      total += value

    prev_value = value

  if not total:
    raise ValueError("Not roman numeral")

  
  return total

def word_to_num(number_str: str) -> int:
  """
  Convert a spelled-out number without spaces or hyphens to a string of the integer.  The function supports numbers from 0 to 99 and is case insensitive.

  Arguments:
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
  temp_word = ""

  for char in number_str:
    temp_word += char

    if temp_word in num_words:
      total += num_words[temp_word]
      temp_word = ""
    elif temp_word in tens_words:
      total += tens_words[temp_word]
      temp_word = ""

  if temp_word:
      raise ValueError(f"Unknown number word: {temp_word}")

  
  return total



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

    
    return s.isdigit() or is_roman_numeral(s) or is_spelled_out_number(s)
    
  def is_roman_numeral(word: str) -> bool:
    """Try to convert the word to an integer. If it's not a valid roman numeral, it will raise a ValueError"""

    try:
      roman_to_int(word)


      return True

    except ValueError:


      return False

  def is_spelled_out_number(s: str) -> bool:
    """Try to convert the word to an integer. If it's not a valid spelled-out number, it will raise a ValueError"""

    try:
      word_to_num(s)


      return True

    except ValueError:


      return False

  lower_s = s.lower()

  
  return lower_s.startswith("chapter") or (len(lower_s.split()) == 1 and is_number(lower_s))

def _extract_epub_chapter_text(item) -> str:
  """
  Extracts text from a chapter item.

  Arguments:
    item: ebooklib item representing a chapter.

  Returns string containing the text of the chapter.
  """

  soup = BeautifulSoup(item.content, "html.parser")
  elements = soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6"])

  for i, element in enumerate(elements[:3]):
    text = element.get_text().strip().lower()
    
    if any(non_chapter_word in text for non_chapter_word in NOT_CHAPTER):


     return ""

    elif is_chapter(text):
      starting_line = i + 1


      return "\n".join(tag.get_text().strip() for tag in elements[starting_line:])

  return ""

def read_epub(file_path: str, metadata: dict) -> str:
  """
  Reads the contents of an epub file and returns it as a string.

  Arguments:
    file_path: Path to the epub file.

  Returns the contents of the epub file as a string.
  """
  
  book_content = ""
  chapter_contents = []

  book = epub.read_epub(file_path, options={"ignore_ncx": True})

  for item in book.get_items():
    if item.get_type() == ebooklib.ITEM_DOCUMENT and not is_not_chapter(item.file_name.lower(), metadata):
      chapter_text = _extract_epub_chapter_text(item)
      if chapter_text:
        chapter_contents.append(_extract_epub_chapter_text(item))
      
  book_content = "\n***\n".join(chapter_contents)


  return book_content

def desmarten_text(book_content: str) -> str:
  """
  Replace smart punctuation in the given text with regular ASCII punctuation.

  Arguments:
    book_content (str): The input text containing smart punctuation.

  Returns str: The text with smart punctuation replaced by regular punctuation.
  """

  punctuation_map = {
    "‘": "'", "’": "'",
    "“": '"', "”": '"',
    "–": "-", "—": "-",
    "…": "...", "•": "*"
  }

  for smart, regular in punctuation_map.items():
    book_content = book_content.replace(smart, regular)


  return book_content

def convert_chapter_break(book_content: str) -> str:
  """
  Converts chapter breaks to three askerisks

  Arguments:
    book_content: The content of the book.

  Returns the book content with askerisks for chapter breaks."""

  book_lines = book_content.split("\n")

  def replace_chapter_break(line: str) -> str:
    if is_chapter(line):

      
      return "***"

    else:


      return line
  


  return "\n".join(replace_chapter_break(line) for line in book_lines)

def _docx_contains_page_break(paragraph):
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

def is_not_chapter(paragraph: str, metadata: dict) -> bool:
  """
  Checks if the given line is not a chapter.
  """
  title = metadata.get("title", "no title found")
  author = metadata.get("author", "no author found")
  paragraph = paragraph.lower()


  return any(paragraph.startswith(title.lower()) or paragraph.startswith(author.lower()) or paragraph.startswith(not_chapter_word) for not_chapter_word in NOT_CHAPTER)
  
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
    paragraph_text = paragraph.text.strip()
    if _docx_contains_page_break(paragraph) and current_page:
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
        
    current_page.append(paragraph_text)
    line_counter += 1

  if current_page:
    pages.append("\n".join(current_page))   
   
  book_content = "\n".join(pages)


  return book_content

def _parse_pdf_page(page: str, metadata: dict) -> str:
  """
  Parses the given pdf page and returns it as a string.
  
  Arguments:
    page: A pdf page.
    
  Returns the pdf page as a string.
  """
  chapter_list = []
  text_lines = 0
  paragraph = ""
  paragraph_list = []
  
  def parse_paragraph(paragraph: str) -> list:
    nonlocal text_lines

    if text_lines < 3:
      if is_not_chapter(paragraph, metadata):
        return []
      elif is_chapter(paragraph):
        paragraph = "\n***\n"
    chapter_list.append(paragraph)
    text_lines += 1
    return chapter_list
  
  lines = page.split("\n")
  for line in lines:
    line = line.strip()
    if line:
      paragraph_list.append(line)
    elif paragraph_list:
      paragraph = "".join(paragraph_list)
      chapter_list = parse_paragraph(paragraph)
      if not chapter_list:
        return ""
      paragraph_list = []

  if paragraph_list:
    paragraph = " ".join(paragraph_list)
    chapter_list = parse_paragraph(paragraph)
    if not chapter_list:
      return ""
  
  return "\n".join(chapter_list)

def read_pdf(file_path: str, metadata: dict) -> str:
  """
  Reads the contents of a pdf file and returns it as a string.
  
  Arguments:
    file_path: Path to the pdf file.
  
  Returns the contents of the pdf file as a string.
  """
  pdf_pages = []
  
  pdf = PdfReader(file_path)
  
  for page in pdf.pages:
    page_text = page.extract_text()
    pdf_page = _parse_pdf_page(page_text, metadata)
    if pdf_page:
      pdf_pages.append(pdf_page)

  book_content = "\n".join(pdf_pages)


  return book_content

def convert_file(folder_name: str, book_name: str) -> None:
  """
  Converts a book to a text file with 3 asterisks for chapter breaks
  
  Arguments:
    book_name: Name of the book.
    folder_name: Name of the folder containing the book.

  Reutrns the name of the text file.
  """

  book_content = ""
  file_path = os.path.join(folder_name, book_name)

  book_name = book_name.replace(" ", "_")
  book_name = book_name.replace("-", "_")
  filename_list = book_name.split(".")
  if len(filename_list) > 1:
    base_name = "_".join(filename_list[:-1])
  else:
    base_name = filename_list[0]
  extension = filename_list[-1]

  metadata= {"title": "Dragon Run", "author": "Ash Roberts"}
  if extension == "epub":
    book_content = read_epub(file_path, metadata)
  elif extension == "docx":
    book_content = read_docx(file_path, metadata)
  elif extension == "pdf":
    book_content = read_pdf(file_path, metadata)
  elif extension == "txt" or extension == "text":
    book_content = read_text_file(file_path)
  else:
    print("Invalid filetype")
    exit()

  book_content = desmarten_text(book_content)

  book_name = f"{base_name}.txt"
  processed_files_path = os.path.join(folder_name, "processed")
  book_path = os.path.join(processed_files_path, book_name)
  write_to_file(book_content, book_path)

folder_name = "folder"
for book_name in os.listdir(folder_name):
  full_path = os.path.join(folder_name, book_name)
  if os.path.isfile(full_path):
    convert_file(folder_name, book_name)
    