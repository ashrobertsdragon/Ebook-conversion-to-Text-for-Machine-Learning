import base64
import logging
import os

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

load_dotenv()


def encode_image_file(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def create_image_role_list(base64_images: list) -> list:
    return [
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                "detail": "low",
            },
        }
        for base64_image in base64_images
    ]


def create_payload(base64_images: list) -> list:
    image_role_list: list = create_image_role_list(base64_images)
    return [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Please provide the text in these images as a single "
                        "combined statement with spaces as appropriate "
                        "without any commentary. Use your judgment on whether"
                        " consecutive images are a single word or multiple "
                        "words. If there is no text in the image, or it is "
                        "unreadable, respond with 'No text found'"
                    ),
                },
                *image_role_list,
            ],
        }
    ]


def clean_response(answer: str) -> str:
    """Strip 'No text found' responses from AI OCR"""
    return "" if answer == "No text found" else answer


def run_ocr(base64_images: list) -> str:
    """
    Perform optical character recognition (OCR) on a list of base64-encoded
    images using the OpenAI API.

    Arguments:
        base64_images (list): A list of base64-encoded images.

    Returns str: The recognized text from the images.
    """
    payload: list = create_payload(base64_images)
    api_key: str = os.getenv("OPENAI_API_KEY")
    client: OpenAI = OpenAI(api_key=api_key)

    try:
        response: ChatCompletion = client.chat.completions.create(
            model="gpt-4o", messages=payload, max_tokens=10
        )
        if response.choices:
            answer = response.choices[0].message.content
            if answer.startswith("I'm sorry, but as an"):
                return run_ocr(base64_images)
            return clean_response(answer)
    except Exception as e:
        logging.exception("An error occured %s", str(e))
        return ""
