import base64
import os

import requests
from dotenv import load_dotenv

load_dotenv()


def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def run_ocr(base64_images: list) -> str:
  """
  Perform optical character recognition (OCR) on a list of base64-encoded 
  images using the OpenAI API.

  Arguments:
    base64_images (list): A list of base64-encoded images.

  Returns str: The recognized text from the images.
  """

  api_key = os.getenv("OPENAI_API_KEY")
  image_role_list = []
  headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {api_key}"
  }
  for base64_image in base64_images:
    image_role_list.append({
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}",
            "detail": "low"
        }
    })
  payload = {
      "model":
      "gpt-4-vision-preview",
      "messages": [{
          "role":
          "user",
          "content": [{
              "type":
              "text",
              "text":
              (
                "Please provide the text in these images as a single combined "
                "statement with spaces as appropriate without any commentary. Use "
                "your judgment on whether consecutive images are a single word or "
                "multiple words. If there is no text in the image, or it is "
                "unreadable, respond with 'No text found'"
              )
          }, *image_role_list]
      }],
      "max_tokens":
      10
  }
  try:
    response = requests.post(
      "https://api.openai.com/v1/chat/completions",
      headers=headers,
      json=payload
    )
    if response.json()["choices"]:
      answer = response.json()["choices"][0]["message"]["content"]
      return answer
    if response.json()["error"]:
      error = response.json()["error"]["message"]
      raise Exception(error)
  except KeyError as e:
    print(f"KeyError: {e}")
    print("Response:", response.text)
    return None
