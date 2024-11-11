import pytest

from ebook2text.file_handling import read_text_file, write_to_file

TEST_CONTENT = "This is test content.\nWith multiple lines."


@pytest.fixture(scope="module")
def test_file(tmp_path_factory):
    """Fixture to create a temporary test file."""
    test_dir = tmp_path_factory.mktemp("test_files")
    test_file = test_dir / "test.txt"
    test_file.write_text(TEST_CONTENT, encoding="utf-8")
    return test_file


class TestFileHandling:
    def test_read_text_file(self, test_file):
        content = read_text_file(str(test_file))
        assert content == TEST_CONTENT

    def test_read_text_file_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            read_text_file("nonexistent_file.txt")

    def test_write_to_file(self, tmp_path):
        new_file = tmp_path / "new_file.txt"
        new_content = "New content for the file."
        write_to_file(new_content, str(new_file))
        assert new_file.read_text(encoding="utf-8") == new_content

    def test_write_to_file_creates_file(self, tmp_path):
        new_file = tmp_path / "brand_new_file.txt"
        new_content = "Brand new file content."
        write_to_file(new_content, str(new_file))
        assert new_file.exists()
        assert new_file.read_text(encoding="utf-8") == new_content
