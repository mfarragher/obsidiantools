import pytest
import networkx as nx
from pathlib import Path


from obsidiantools.api import Vault

# NOTE: run the tests from the project dir.
WKD = Path().cwd()


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


def test_canvas_graph_detail_index_graph(actual_connected_vault):
    actual_crazy_wall_graph_detail = (
        actual_connected_vault.canvas_graph_detail_index
        .get('Crazy wall.canvas'))

    G, _, _ = actual_crazy_wall_graph_detail

    # check nodes in overall graph:
    expected_nodes = ['0fb63a211244ab98',
                      '5b04fb9cabc4b282',
                      '8f032f9a663e27b5',
                      'd3f112f83760095a',
                      'c168506f5b075d91',
                      '9d13d42f967553bf',
                      '2919b72bf3df3791']
    actual_nodes = [i for i in G.nodes()]
    assert actual_nodes == expected_nodes
    # expect group node not in graph:
    assert not set(['a10aaf054261706d']).issubset(set(actual_nodes))

    # isolated nodes:
    actual_isolated_nodes = [cv for cv in nx.isolates(G)]
    expected_isolated_nodes = ['0fb63a211244ab98', '2919b72bf3df3791']
    assert actual_isolated_nodes == expected_isolated_nodes

    # check main node's connections:
    actual_in_degree = {n[0]: n[1] for n in G.in_degree}
    actual_out_degree = {n[0]: n[1] for n in G.out_degree}
    assert actual_in_degree.get('c168506f5b075d91') == 2
    assert actual_out_degree.get('c168506f5b075d91') == 1

    # edge count:
    actual_n_edges = G.number_of_edges()
    assert actual_n_edges == 4


def test_canvas_graph_detail_index_graph_other_attributes(actual_connected_vault):
    actual_crazy_wall_graph_detail = (
        actual_connected_vault.canvas_graph_detail_index
        .get('Crazy wall.canvas'))

    _, pos, edge_labels = actual_crazy_wall_graph_detail

    # check pos:
    assert pos.get('2919b72bf3df3791') == (-1363, 812)
    actual_x_locs = {c: pos[0] for (c, pos) in pos.items()}
    assert max(actual_x_locs, key=actual_x_locs.get) == 'c168506f5b075d91'
    assert min(actual_x_locs, key=actual_x_locs.get) == '2919b72bf3df3791'
    actual_y_locs = {c: pos[1] for (c, pos) in pos.items()}
    assert max(actual_y_locs, key=actual_y_locs.get) == '0fb63a211244ab98'
    assert min(actual_y_locs, key=actual_y_locs.get) == '5b04fb9cabc4b282'

    # check edge_labels:
    actual_non_blank_edge_labels = {
        pair: label for pair, label in edge_labels.items()
        if label != ''}
    expected_non_blank_edge_labels = {
        ('d3f112f83760095a', 'c168506f5b075d91'): 'inspires?'}
    assert actual_non_blank_edge_labels == expected_non_blank_edge_labels


def test_n_backlinks_null_in_canvas_file_metadata(actual_connected_vault):
    df_canvas = actual_connected_vault.get_canvas_file_metadata()
    assert df_canvas['n_backlinks'].isna().mean() == 1
