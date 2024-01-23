import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

from .chapter_check import is_chapter, is_not_chapter, NOT_CHAPTER
from .ocr import encode_image, run_ocr
from .text_conversion import desmarten_text


def extract_epub_chapter_text(item, book) -> str:
  """
  Extracts text from a chapter item.
  Arguments:
    item: ebooklib item representing a chapter.
  Returns string containing the text of the chapter.
  """

  soup = BeautifulSoup(item.content, "html.parser")
  elements = soup.find_all(["p", "img", "h1", "h2", "h3", "h4", "h5", "h6"])
  for i, element in enumerate(elements[:3]):
    if element.name == "img":
      image_data=book.read_item(element["src"])
      base64_images = [encode_image(image_data)]
      text = run_ocr(base64_images)
    else:
      text = element.get_text().strip().lower()
    if any(non_chapter_word in text for non_chapter_word in NOT_CHAPTER):
      return ""
    elif is_chapter(text):
      starting_line = i + 1
      return "\n".join(tag.get_text().strip() for tag in elements[starting_line:] if tag != "img")
  return ""

def read_epub(file_path: str, metadata: dict) -> str:
  """
  Reads the contents of an epub file and returns it as a string.
  Arguments:
    file_path: Path to the epub file.
  Returns the contents of the epub file as a string.
  """

  chapter_contents = []
  book = epub.read_epub(file_path, options={"ignore_ncx": True})
  for item in book.get_items():
    if item.get_type() == ebooklib.ITEM_DOCUMENT and not is_not_chapter(item.file_name.lower(), metadata):
      chapter_text = extract_epub_chapter_text(item, book)
      if chapter_text:
        chapter_text = desmarten_text(chapter_text)
        chapter_contents.append(chapter_text)
  return "\n***\n".join(chapter_contents)
