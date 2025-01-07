
# Convert Ebook File

## Overview

This Python script provides functionality for converting various ebook file formats (EPUB, DOCX, PDF, TXT) into a standardized text format. The script processes each file, identifying chapters, and replaces chapter headers with asterisks. It also performs OCR (Optical Character Recognition) for image-based text using GPT-4o and standardizes the text by desmartening punctuation.

## Features

- **File Format Support**: Handles EPUB, DOCX, PDF, and TXT formats.
- **Chapter Identification**: Detects and marks chapter breaks.
- **OCR Capability**: Converts text from images using OCR.
- **Text Standardization**: Replaces smart punctuation with ASCII equivalents.

## Requirements

To run this script, you need Python 3.9 or above and the following packages:

- `python-docx`
- `openai`
- `python-dotenv`
- `bs4`
- `pdfminer.six`
- `pillow`

## Usage

1. Ensure all dependencies are installed.
2. Set your environment variable for the OpenAI API key.
3. Place your ebook files in a known directory.
4. Run the script with the path to the ebook file and a metadata dictionary with keys of 'title' and 'author' as arguments.

- set `save_file` to False, if you want a string returned.
- provide a Path object of a file name to be written to, to use a custom output filename.

## Functions

- `convert_file(file_path: Path, metadata: dict, *, save_file: bool = True, save_path: Optional[Path] = None) -> Union[str, None]`: Main function to convert an ebook file to text.

## Contributing

Contributions to this project are welcome. Please use Ruff for formatting to ensure that your code follows the existing style for consistency, and follow the [ProsePal Open Source Contributor's Code of Contact](https://github.com/ashrobertsdragon/Ebook-conversion-to-Text-for-Machine-Learning/blob/main/prosepal-contributors-code-of-conduct.md).

## TODO

- Increase test coverage
  - Tests for text converter
  - More edge cases and failure states
- Better handling of ebooklib dependency
- Add additional AI models for OCR as plugins
- Explore additional filetypes
- Other options for determining filetype

## License

This project is licensed by ProsePal LLC under the MIT license
