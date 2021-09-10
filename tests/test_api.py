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
