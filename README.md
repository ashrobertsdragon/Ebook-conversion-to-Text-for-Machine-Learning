
# Convert Ebook File

## Overview
This Python script provides functionality for converting various ebook file formats (EPUB, DOCX, PDF, TXT) into a standardized text format. The script processes each file, identifying chapters, and replaces chapter headers with asterisks. It also performs OCR (Optical Character Recognition) for image-based text and standardizes the text by desmartenizing punctuation.

## Features
- **File Format Support**: Handles EPUB, DOCX, PDF, and TXT formats.
- **Chapter Identification**: Detects and marks chapter breaks.
- **OCR Capability**: Converts text from images using OCR.
- **Text Standardization**: Replaces smart punctuation with ASCII equivalents.

## Requirements
To run this script, you need Python 3.8 or above and the following packages:
- `python-docx`
- `ebooklib`
- `requests`
- `python-dotenv`
- `bs4`
- `ebooklib`
- `pdfminer.six`
- `pillow`

## Usage
1. Ensure all dependencies are installed.
2. Set your environment variable for the OpenAI API key.
3. Place your ebook files in a known directory.
4. Run the script with the ebook file as an argument.

## Functions
- `read_text_file(file: str) -> str`: Reads a text file and returns its content.
- `write_to_file(content: str, file: str)`: Writes content to a file.
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

- **v0.3.1** (Release date: Januar 23, 2024)
  - fixed concantation of text in pdf conversion
  - updated pillow version to secure version

- **v1.0.0** (Release date: January 23, 2024)
  - created library instead of single module