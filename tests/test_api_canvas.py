import pytest


from obsidiantools.api import Vault


@pytest.fixture
def mock_initial_vault(tmp_path):
    mock_vault = Vault(tmp_path)
    return mock_vault


def test_get_canvas_relpaths(mock_initial_vault):
    mock_output = mock_initial_vault._get_canvas_relpaths()
    assert isinstance(mock_output, list)


def test_get_canvas_relpaths_by_name(mock_initial_vault):
    mock_output = mock_initial_vault._get_canvas_relpaths_by_name()
    assert isinstance(mock_output, dict)
