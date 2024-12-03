import pytest
from bs4 import BeautifulSoup

from ebook2text.epub_conversion import (
    EpubConverter,
    EpubImageExtractor,
    EpubTextExtractor,
)


@pytest.fixture
def epub_file(test_files_dir):
    return str(test_files_dir / "test_epub.epub")


@pytest.fixture
def epub_file_with_image(test_files_dir):
    return str(test_files_dir / "test_epub_with_image.epub")


@pytest.fixture
def sample_element_with_text():
    html = "<div><p>This is a sample paragraph.</p></div>"
    soup = BeautifulSoup(html, "html.parser")
    return soup.find("p")


@pytest.fixture
def sample_element_with_image():
    html = '<img src="chapter_one.jpg"/>'
    soup = BeautifulSoup(html, "html.parser")
    return soup.find("img")


@pytest.fixture
def epub_image_extractor():
    return EpubImageExtractor()


@pytest.fixture
def epub_text_extractor(epub_image_extractor):
    return EpubTextExtractor(epub_image_extractor)


@pytest.fixture
def epub_converter(epub_file, metadata, epub_text_extractor):
    return EpubConverter(epub_file, metadata, epub_text_extractor)


@pytest.fixture
def epub_converter_with_image(
    epub_file_with_image, metadata, epub_text_extractor
):
    return EpubConverter(epub_file_with_image, metadata, epub_text_extractor)


class TestEpubConverter:
    def test_parse_file_returns_valid_chapters(self, epub_converter):
        chapters = list(epub_converter.parse_file())
        assert len(chapters)
        assert all(isinstance(chapter, str) for chapter in chapters)
        assert all(len(chapter.strip()) > 0 for chapter in chapters)

    def test_process_chapter_text_extracts_content(
        self, epub_converter, epub_file
    ):
        page_4 = list(epub_converter._read_file(epub_file))[4]
        text = epub_converter._process_chapter_text(page_4)
        assert isinstance(text, str)
        assert text == "First chapter paragraph text."

    def test_empty_epub_file_returns_empty_generator(
        self, tmp_path, epub_text_extractor
    ):
        empty_file = tmp_path / "empty.epub"
        empty_file.touch()
        converter = EpubConverter(empty_file, {}, epub_text_extractor)
        chapters = list(converter.parse_file())
        assert not len(chapters)

    def test_return_string_with_separators(self, epub_converter):
        chapters = list(epub_converter.parse_file())
        result_string = epub_converter.return_string(chapters)
        assert isinstance(result_string, str)
        assert (
            result_string.count(epub_converter.chapter_separator)
            == len(chapters) - 1
        )
        assert all(chapter in result_string for chapter in chapters)

    def test_write_text_with_chapter_separators(
        self, epub_converter, tmp_path
    ):
        content = "This is a test chapter."
        file_path = tmp_path / "output.txt"

        epub_converter.write_text(content, file_path)
        with file_path.open("r", encoding="utf-8") as f:
            written_content = f.read()
        expected_content = f"\n{epub_converter.CHAPTER_SEPARATOR}\n{content}"
        assert written_content == expected_content
