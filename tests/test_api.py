import pytest


from obsidian_tools.api import Vault


@pytest.fixture
def mock_initial_vault(tmp_path):
    mock_vault = Vault(tmp_path)
    return mock_vault


def test_vault_initialisation(tmp_path):
    actual_vault = Vault(tmp_path)

    assert isinstance(actual_vault, Vault)

    # dirpath
    assert actual_vault.dirpath == tmp_path

    # file_index
    assert isinstance(actual_vault.file_index, dict)


def test_vault_initialisation_needs_directory():
    with pytest.raises(TypeError):
        Vault()


def test_get_md_relpaths(mock_initial_vault):
    mock_output = mock_initial_vault._get_md_relpaths()
    assert isinstance(mock_output, list)


def test_get_md_relpaths_by_name(mock_initial_vault):
    mock_output = mock_initial_vault._get_md_relpaths_by_name()
    assert isinstance(mock_output, dict)


def test_get_wikilinks_by_md_filename(mock_initial_vault):
    mock_output = mock_initial_vault._get_wikilinks_by_md_filename()
    assert isinstance(mock_output, dict)


def test_get_unique_wikilinks_by_md_filename(mock_initial_vault):
    mock_output = mock_initial_vault._get_unique_wikilinks_by_md_filename()
    assert isinstance(mock_output, dict)
