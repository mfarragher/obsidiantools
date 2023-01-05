import pytest
from pathlib import Path
import networkx as nx


from obsidiantools.api import Vault

# NOTE: run the tests from the project dir.
WKD = Path().cwd()


@pytest.fixture
def actual_connected_vault():
    return Vault(WKD / 'tests/vault-stub').connect().gather()


def test_attr_setters_main_setup(actual_connected_vault):
    actual_connected_vault.md_file_index = {}
    assert actual_connected_vault.md_file_index == {}

    actual_connected_vault.canvas_file_index = {'New.canvas': ''}
    assert actual_connected_vault.canvas_file_index == {'New.canvas': ''}


def test_attr_setters_md_connect_related(actual_connected_vault):
    actual_connected_vault.attachments = True
    assert actual_connected_vault.attachments

    actual_connected_vault.is_connected = True
    assert actual_connected_vault.is_connected

    actual_connected_vault.is_gathered = True
    assert actual_connected_vault.is_gathered

    actual_connected_vault.front_matter_index = {}
    assert actual_connected_vault.front_matter_index == {}

    actual_connected_vault.backlinks_index = {}
    assert actual_connected_vault.backlinks_index == {}

    actual_connected_vault.wikilinks_index = {}
    assert actual_connected_vault.wikilinks_index == {}

    actual_connected_vault.unique_wikilinks_index = {}
    assert actual_connected_vault.unique_wikilinks_index == {}

    actual_connected_vault.embedded_files_index = {}
    assert actual_connected_vault.embedded_files_index == {}

    actual_connected_vault.math_index = {}
    assert actual_connected_vault.math_index == {}

    actual_connected_vault.md_links_index = {}
    assert actual_connected_vault.md_links_index == {}

    actual_connected_vault.unique_md_links_index = {}
    assert actual_connected_vault.unique_md_links_index == {}

    actual_connected_vault.tags_index = {}
    assert actual_connected_vault.tags_index == {}

    actual_connected_vault.nonexistent_notes = []
    assert actual_connected_vault.nonexistent_notes == []

    actual_connected_vault.isolated_notes = []
    assert actual_connected_vault.isolated_notes == []

    actual_connected_vault.media_file_index = {}
    assert actual_connected_vault.media_file_index == {}

    actual_connected_vault.nonexistent_media_files = []
    assert actual_connected_vault.nonexistent_media_files == []

    actual_connected_vault.isolated_media_files = []
    assert actual_connected_vault.isolated_media_files == []

    actual_connected_vault.nonexistent_canvas_files = []
    assert actual_connected_vault.nonexistent_canvas_files == []

    actual_connected_vault.isolated_canvas_files = []
    assert actual_connected_vault.isolated_canvas_files == []

    # check that graph is set AND recognised as empty:
    actual_connected_vault.graph = nx.MultiDiGraph()
    assert nx.is_empty(actual_connected_vault.graph)


def test_attr_setters_md_gather_related(actual_connected_vault):
    actual_connected_vault.source_text_index = {'Isolated note': '`new text`'}
    assert actual_connected_vault.source_text_index == {'Isolated note': '`new text`'}

    actual_connected_vault.readable_text_index = {'Isolated note': 'Test'}
    assert actual_connected_vault.readable_text_index == {'Isolated note': 'Test'}


def test_attr_setters_canvas_connect_related(actual_connected_vault):
    actual_connected_vault.canvas_content_index = {}
    assert actual_connected_vault.canvas_content_index == {}

    actual_connected_vault.canvas_graph_detail_index = {}
    assert actual_connected_vault.canvas_graph_detail_index == {}
