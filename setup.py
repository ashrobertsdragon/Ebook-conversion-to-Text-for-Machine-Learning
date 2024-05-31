import os
import pathlib
import re

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")


def get_version():
    version_file = os.path.join("ebook2text", "VERSION.py")
    with open(version_file) as f:
        version_content = f.read()
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_content, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="ebook2text",
    version=get_version(),
    description="Convert common book file types to text for machine learning",
    long_description=long_description,
    author="Ashlynn Antrobus",
    author_email="ashlynn@prosepal.io",
    packages=find_packages(),
    install_requires=[
        "pdfminer.six",
        "pillow",
        "EbookLib",
        "beautifulsoup4",
        "python-docx",
        "python-dotenv",
        "openai",
    ],
)
