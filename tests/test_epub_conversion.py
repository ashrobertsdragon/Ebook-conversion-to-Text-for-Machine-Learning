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
def epub_file_with_images(test_files_dir):
    return str(test_files_dir / "test_epub_with_images.epub")


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
def epub_converter(epub_file, sample_metadata, epub_text_extractor):
    return EpubConverter(epub_file, sample_metadata, epub_text_extractor)


@pytest.fixture
def epub_converter_with_images(
    epub_file_with_images, sample_metadata, epub_text_extractor
):
    return EpubConverter(
        epub_file_with_images, sample_metadata, epub_text_extractor
    )


def test_split_chapters(epub_converter):
    result = epub_converter.split_chapters()
    assert isinstance(result, str)
    assert "Sample Title" in result
    assert "***" in result


def test_split_chapters_with_images(epub_converter_with_images):
    result = epub_converter_with_images.split_chapters()
    assert isinstance(result, str)
    assert "Sample Title" in result
    assert "***" in result


def test_extract_text(epub_converter, sample_element_with_text):
    text_extractor = EpubTextExtractor(epub_converter)
    extracted_text = text_extractor.extract_text(sample_element_with_text)
    assert extracted_text == "This is a sample paragraph."


def test_extract_text_with_image(
    epub_converter_with_images, sample_element_with_image, monkeypatch
):
    ocr_output = "Extracted OCR text"

    monkeypatch.setattr("ebook2text.ocr.run_ocr", lambda x: ocr_output)
    text_extractor = EpubTextExtractor(epub_converter_with_images)
    extracted_text = text_extractor.extract_text(sample_element_with_image)

    assert extracted_text == ocr_output


def test_extract_images_with_image_element(
    epub_converter_with_images, sample_element_with_image
):
    image_extractor = EpubImageExtractor(epub_converter_with_images.book)
    images = image_extractor.extract_images(sample_element_with_image)

    assert isinstance(images, list)
    assert len(images) > 0
    assert all(isinstance(img, str) for img in images)
