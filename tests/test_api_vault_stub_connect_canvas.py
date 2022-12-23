import pytest
import os
from pathlib import Path


from obsidiantools.api import Vault

# NOTE: run the tests from the project dir.
WKD = Path(os.getcwd())


@pytest.fixture
def expected_canvas_file_index():
    return {'Crazy wall.canvas': Path('Crazy wall.canvas'),
            'Crazy wall 2.canvas': Path('Crazy wall 2.canvas')}


@pytest.fixture
def actual_connected_vault():
    return Vault(WKD / 'tests/vault-stub').connect()


def test_canvas_file_index(actual_connected_vault,
                           expected_canvas_file_index):
    assert (actual_connected_vault.canvas_file_index
            == expected_canvas_file_index)


def test_canvas_content_index(actual_connected_vault):
    actual_crazy_wall_2_content = (
        actual_connected_vault.canvas_content_index
        .get('Crazy wall 2.canvas'))
    actual_crazy_wall_2_text = (actual_crazy_wall_2_content
                                .get('nodes')[0].get('text'))
    expected_crazy_wall_2_text = "Now we're getting meta..."
    assert actual_crazy_wall_2_text == expected_crazy_wall_2_text
