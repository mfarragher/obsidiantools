import pytest


from obsidiantools.api import Vault


@pytest.fixture
def mock_initial_vault(tmp_path):
    mock_vault = Vault(tmp_path)
    return mock_vault


def test_get_md_relpaths(mock_initial_vault):
    mock_output = mock_initial_vault._get_md_relpaths()
    assert isinstance(mock_output, list)


def test_get_md_relpaths_by_name(mock_initial_vault):
    mock_output = mock_initial_vault._get_md_relpaths_by_name()
    assert isinstance(mock_output, dict)


def test_get_wikilinks_index(mock_initial_vault):
    mock_output = mock_initial_vault._wikilinks_index
    assert isinstance(mock_output, dict)


def test_get_math_index(mock_initial_vault):
    mock_output = mock_initial_vault._math_index
    assert isinstance(mock_output, dict)


def test_get_embedded_files_index(mock_initial_vault):
    mock_output = mock_initial_vault._embedded_files_index
    assert isinstance(mock_output, dict)


def test_get_unique_wikilinks_index(mock_initial_vault):
    mock_output = mock_initial_vault._unique_wikilinks_index
    assert isinstance(mock_output, dict)


def test_get_tags_index(mock_initial_vault):
    mock_output = mock_initial_vault._tags_index
    assert isinstance(mock_output, dict)


def test_get_front_matter_index(mock_initial_vault):
    mock_output = mock_initial_vault._front_matter_index
    assert isinstance(mock_output, dict)
