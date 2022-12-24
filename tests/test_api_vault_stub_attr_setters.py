import pytest
import os
from pathlib import Path


from obsidiantools.api import Vault

# NOTE: run the tests from the project dir.
WKD = Path(os.getcwd())


@pytest.fixture
def actual_connected_vault():
    return Vault(WKD / 'tests/vault-stub').connect().gather()


def test_attr_setters(actual_connected_vault):
    actual_connected_vault.file_index = {}
    assert actual_connected_vault.file_index == {}

    actual_connected_vault.canvas_file_index = {'New.canvas': ''}
    assert actual_connected_vault.canvas_file_index == {'New.canvas': ''}

    actual_connected_vault.source_text_index = {'Isolated note': '`new text`'}
    assert actual_connected_vault.source_text_index == {'Isolated note': '`new text`'}

    actual_connected_vault.readable_text_index = {'Isolated note': 'Test'}
    assert actual_connected_vault.readable_text_index == {'Isolated note': 'Test'}
