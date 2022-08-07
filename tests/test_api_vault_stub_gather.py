import pytest
import os
from pathlib import Path


from obsidiantools.api import Vault

# NOTE: run the tests from the project dir.
WKD = Path(os.getcwd())


@pytest.fixture
def actual_unconnected_vault():
    return Vault(WKD / 'tests/vault-stub')


@pytest.fixture
def actual_connected_vault(actual_unconnected_vault):
    return actual_unconnected_vault.connect()


@pytest.fixture
def actual_gathered_vault_defaults(actual_connected_vault):
    return actual_connected_vault.gather()


def test_vault_not_connected(actual_unconnected_vault):
    assert not actual_unconnected_vault.is_gathered
    assert actual_unconnected_vault.source_text_index == {}
    assert actual_unconnected_vault.readable_text_index == {}

    with pytest.raises(AttributeError):
        actual_unconnected_vault.gather()

    with pytest.raises(AttributeError):
        actual_unconnected_vault.get_source_text('Isolated note')
    with pytest.raises(AttributeError):
        actual_unconnected_vault.get_readable_text('Isolated note')


def test_text_not_existing(actual_gathered_vault_defaults):
    assert actual_gathered_vault_defaults.is_gathered
    with pytest.raises(ValueError):
        actual_gathered_vault_defaults.get_source_text('Tarpeia')
    with pytest.raises(ValueError):
        actual_gathered_vault_defaults.get_readable_text('Tarpeia')


def test_isolated_note_md_text(actual_gathered_vault_defaults):
    expected_text = r"""# Isolated note

This is an isolated note.
"""

    assert actual_gathered_vault_defaults.is_gathered

    actual_text = actual_gathered_vault_defaults.get_source_text('Isolated note')
    assert actual_text == expected_text


def test_all_files_are_in_source_text_index(actual_gathered_vault_defaults):
    file_keys = set(actual_gathered_vault_defaults.file_index.keys())
    text_keys = set(actual_gathered_vault_defaults.source_text_index.keys())
    assert file_keys == text_keys


def test_all_files_are_in_readable_text_index(actual_gathered_vault_defaults):
    file_keys = set(actual_gathered_vault_defaults.file_index.keys())
    text_keys = set(actual_gathered_vault_defaults.readable_text_index.keys())
    assert file_keys == text_keys
