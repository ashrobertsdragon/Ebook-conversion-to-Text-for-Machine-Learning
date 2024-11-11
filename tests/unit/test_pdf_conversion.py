import pytest

from ebook2text.pdf_conversion import (
    PDFChapterSplitter,
    PDFConverter,
    PDFImageExtractor,
    PDFTextExtractor,
)


@pytest.fixture
def test_pdf_path(test_files_dir):
    """Fixture for retrieving test PDF without images."""
    return test_files_dir / "test_pdf.pdf"


@pytest.fixture
def test_pdf_with_images_path(test_files_dir):
    """Fixture for retrieving test PDF with images."""
    return test_files_dir / "test_pdf_with_image.pdf"


@pytest.fixture
def pdf_converter(test_pdf_path, metadata):
    """Fixture for initializing a PDFConverter instance."""
    return PDFConverter(file_path=str(test_pdf_path), metadata=metadata)


@pytest.fixture
def pdf_converter_with_images(test_pdf_with_images_path, metadata):
    """Fixture for initializing a PDFConverter instance with images."""
    return PDFConverter(
        file_path=str(test_pdf_with_images_path), metadata=metadata
    )


@pytest.fixture
def pdf_text_extractor(pdf_converter):
    """Fixture for initializing a PDFTextExtractor instance."""
    return PDFTextExtractor(converter=pdf_converter)


@pytest.fixture
def pdf_image_extractor(test_pdf_with_images_path):
    """Fixture for initializing a PDFImageExtractor instance."""
    return PDFImageExtractor(file_path=str(test_pdf_with_images_path))


@pytest.fixture
def pdf_chapter_splitter(pdf_converter):
    """Fixture for initializing a PDFChapterSplitter instance."""
    return PDFChapterSplitter(
        book=pdf_converter._read_file(pdf_converter.file_path),
        metadata=pdf_converter.metadata,
        converter=pdf_converter,
    )


def test_pdf_converter_read_file(pdf_converter):
    """Test the _read_file method to ensure pages are correctly read."""
    pages = pdf_converter._read_file(pdf_converter.file_path)
    assert len(pages) == 7


def test_pdf_converter_extract_text(pdf_converter):
    """Test extract_text method to ensure correct extraction from each page."""
    pages = pdf_converter._read_file(pdf_converter.file_path)
    text = pdf_converter.extract_text(pages[0])
    assert "Sample Title" in text


def test_pdf_converter_split_chapters(pdf_converter):
    """Test split_chapters to verify chapter boundaries are detected and split."""
    chapters_text = pdf_converter.split_chapters()
    assert chapters_text.startswith("First chapter paragraph text.")


def test_pdf_converter_ends_with_punctuation(pdf_converter):
    """Test ends_with_punctuation to confirm sentence end detection."""
    assert pdf_converter.ends_with_punctuation("Hello world!")
    assert not pdf_converter.ends_with_punctuation("Hello world")


def test_pdf_text_extractor_extract_image_text(
    monkeypatch, pdf_text_extractor
):
    """Test _extract_image_text by patching OCR function."""

    def mock_run_ocr(images):
        return "OCR text from image"

    monkeypatch.setattr("ebook2text.pdf_conversion.run_ocr", mock_run_ocr)

    extracted_text = pdf_text_extractor._extract_image_text([1, 2])
    assert extracted_text == "OCR text from image"


def test_pdf_image_extractor_extract_images(pdf_image_extractor):
    """Test extract_images to ensure images are properly processed and extracted."""
    images = pdf_image_extractor.extract_images([24])
    assert len(images) > 0
    assert isinstance(images[0], str)


def test_pdf_image_extractor_create_image_from_binary(pdf_image_extractor):
    """Test _create_image_from_binary to ensure valid base64 image encoding."""
    test_stream = b"\x00\xff\x00\xff\x00\xff\x00\xff\x00"
    encoded_image = pdf_image_extractor._create_image_from_binary(
        stream=test_stream, width=3, height=3, mode="L"
    )
    assert isinstance(encoded_image, str)
    assert (
        encoded_image
        == "iVBORw0KGgoAAAANSUhEUgAAAAMAAAADCAAAAABzQ+pjAAAAEElEQVR4nGNg+M/A8B9CAAAX9AP9aK8TcAAAAABJRU5ErkJggg=="
    )
