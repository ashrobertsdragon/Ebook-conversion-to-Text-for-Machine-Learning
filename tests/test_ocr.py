from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from ebook2text.ocr import (
    clean_response,
    create_image_role_list,
    create_payload,
    encode_image_file,
    run_ocr,
)


@pytest.fixture
def base64_images():
    return [
        "iVBORw0KGgoAAAANSUhEUgAAAAMAAAADCAAAAABzQ+pjAAAAEElEQVR4nGNg+M/A8B9CAAAX9AP9aK8TcAAAAABJRU5ErkJggg=="
    ]


@pytest.fixture
def api_client_mock():
    with patch("ebook2text.ocr.CLIENT.chat.completions.create") as mock:
        yield mock


@pytest.fixture
def saved_image(tmp_path):
    img_file = tmp_path / "test.png"
    stream = b"\x00\xff\x00\xff\x00\xff\x00\xff\x00"
    image = Image.frombytes("L", (3, 3), stream)
    image.save(img_file, format="PNG")
    return str(img_file)


def test_encode_image_file(saved_image):
    encoded_str = encode_image_file(saved_image)
    assert isinstance(encoded_str, str)
    assert (
        encoded_str
        == "iVBORw0KGgoAAAANSUhEUgAAAAMAAAADCAAAAABzQ+pjAAAAEElEQVR4nGNg+M/A8B9CAAAX9AP9aK8TcAAAAABJRU5ErkJggg=="
    )


def test_create_image_role_list(base64_images):
    role_list = create_image_role_list(base64_images)
    assert isinstance(role_list, list)
    assert len(role_list) == 1
    assert role_list[0]["type"] == "image_url"
    assert (
        role_list[0]["image_url"]["url"]
        == f"data:image/png;base64,{base64_images[0]}"
    )
    assert role_list[0]["image_url"]["detail"] == "low"


def test_create_payload(base64_images):
    payload = create_payload(base64_images)
    assert isinstance(payload, list)
    assert len(payload) == 1
    assert payload[0]["role"] == "user"
    assert (
        "Please provide the text in these images as a single combined statement"
        in payload[0]["content"][0]["text"]
    )
    assert payload[0]["content"][1]["type"] == "image_url"
    assert (
        payload[0]["content"][1]["image_url"]["url"]
        == f"data:image/png;base64,{base64_images[0]}"
    )


@pytest.mark.parametrize(
    "answer,expected",
    [
        ("No text found", ""),
        ("I'm sorry", ""),
        ("I cannot read this", ""),
        ("As a text-based model", ""),
        ("Readable text", "Readable text"),
    ],
)
def test_clean_response(answer, expected):
    assert clean_response(answer) == expected


def test_run_ocr_no_images(api_client_mock):
    result = run_ocr([])
    assert result == ""
    api_client_mock.assert_not_called()


def test_run_ocr_single_image(api_client_mock, base64_images):
    api_client_mock.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Detected text"))]
    )
    result = run_ocr(base64_images)
    assert result == "Detected text"
    api_client_mock.assert_called_once()


def test_run_ocr_no_response_error(api_client_mock, base64_images):
    api_client_mock.return_value = MagicMock(choices=[None])
    result = run_ocr(base64_images)
    assert result == ""
    api_client_mock.assert_called_once()


def test_run_ocr_refusal(api_client_mock, base64_images):
    api_client_mock.return_value = MagicMock(
        choices=[
            MagicMock(message=MagicMock(content="I'm sorry, I cannot do that"))
        ]
    )
    result = run_ocr(base64_images)
    assert result == ""
    assert api_client_mock.call_count == 4  # due to retries


def test_run_ocr_no_response_exception(api_client_mock, base64_images):
    api_client_mock.side_effect = Exception("Some error")
    result = run_ocr(base64_images)
    assert result == ""
    api_client_mock.assert_called_once()
