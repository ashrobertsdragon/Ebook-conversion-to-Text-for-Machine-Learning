
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

## Functions

- `convert_file(file_path: str, metadata: dict) -> str`: Main function to convert an ebook file to text.

## Contributing

Contributions to this project are welcome. Please ensure that your code follows the existing style for consistency.

## License

This project is licensed by ProsePal LLC under the MIT license

## Version History

- **v0.1.0** (Release date: November 30, 2023)
  - Initial release

- **v0.1.1** (Release date: December 2, 2023)
  - fixed false positives for is_number

- **v0.2.0** (Release date: December 3, 2023)
  - Conversion of docx files

- **v0.3.0** (Release date: December 8, 2023)
  - Conversion of PDF files

- **v0.3.1** (Release date: January 23, 2024)
  - fixed concatenation of text in pdf conversion
  - updated pillow version to secure version

- **v1.0.0** (Release date: January 23, 2024)
  - created library instead of single module

- **v1.0.1** (Release date: March 13, 2024)
  - setup.py and requirements.txt typo fixed

- **v1.0.2** (Release date: May 17, 2024)
  - added tests, fixed minor typos

- **v1.1.0** (Release date: May 30, 2024)
  - Change to abstract factory pattern

- **v1.1.1** (Release date: May 31, 2024)
  - Pull current version of ebooklib from Github and folded it into library since package repo out of date

- **v1.1.2** (Release date: May 31, 2024)
  - FIX: Put ebooklib in correct directory.

- **v1.1.3** (Release date: October 27, 2024)
  - FIX: Initialize logging

- **v1.1.4** (Release date: November 7, 2024)
  - YANKED

- **v1.1.5** (Release date: November 7, 2024)
  - FIX: Move logging to own module

- **v1.1.6** (Release date: November 9, 2024)
  - FIX: Catch PDFSyntaxError and empty image lists, small performance improvement to run_ocr

- **v1.1.7** (Release date November 10, 2024)
  - FIX: Line concatenation issue in PDFs
