from pathlib import Path

import pytest

from ebook2text._exceptions import TextConversionError
from ebook2text.text_parser import TextParser


class TestTextParser:
    def test_read_line_yields_file_content(self, tmp_path):
        test_content = "line1\nline2\nline3"
        test_file = tmp_path / "test.txt"
        test_file.write_text(test_content)
        parser = TextParser(test_file)

        result = list(parser.read_line())

        assert result == ["line1\n", "line2\n", "line3"]

    def test_read_line_empty_file(self, tmp_path):
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")
        parser = TextParser(test_file)

        result = list(parser.read_line())

        assert not result

    def test_write_text_appends_content_with_newline(self, tmp_path):
        initial_content = "existing content\n"
        new_content = "new content"
        test_file = tmp_path / "test.txt"
        test_file.write_text(initial_content)
        parser = TextParser(test_file)

        parser.write_text(new_content, test_file)

        with test_file.open("r", encoding="utf-8") as f:
            result = f.read()
        assert result == initial_content + new_content + "\n"

    def test_return_string_joins_generator_output(self, mocker):
        mock_generator = mocker.MagicMock()
        mock_generator.__iter__.return_value = iter(
            [
                "line1",
                "line2",
                "line3",
            ]
        )
        parser = TextParser(mocker.Mock())

        result = parser.return_string(mock_generator)

        assert result == "line1\nline2\nline3"

    def test_parse_file_raises_error_when_file_does_not_exist(self):
        non_existent_file = Path("non_existent_file.txt")
        parser = TextParser(non_existent_file)

        with pytest.raises(TextConversionError):
            list(parser.parse_file())
