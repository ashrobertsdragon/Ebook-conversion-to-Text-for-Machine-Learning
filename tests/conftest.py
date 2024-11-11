from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def test_files_dir():
    return Path(__file__).parent / "test_files"


@pytest.fixture
def metadata():
    """Fixture for mock metadata dictionary."""
    return {"author": "Sample Author", "title": "Sample Title"}
