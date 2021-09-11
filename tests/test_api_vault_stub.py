import pytest
import numpy as np
import pandas as pd
import os
from pathlib import Path
from pandas.testing import assert_series_equal


from obsidian_tools.api import Vault

# NOTE: run the tests from the project dir.
WKD = Path(os.getcwd())


@pytest.fixture
def expected_metadata_dict():
    return {
        'rel_filepath': {'Sussudio': Path('Sussudio.md'),
                         'Brevissimus moenia': Path('lipsum/Brevissimus moenia.md'),
                         'Ne fuit': Path('lipsum/Ne fuit.md'),
                         'Alimenta': Path('lipsum/Alimenta.md'),
                         'Vulnera ubera': Path('lipsum/Vulnera ubera.md'),
                         'Causam mihi': Path('lipsum/Causam mihi.md'),
                         'Tarpeia': np.NaN,
                         'Caelum': np.NaN,
                         'Vita': np.NaN,
                         'Aras Teucras': np.NaN,
                         'Manus': np.NaN,
                         'Bacchus': np.NaN,
                         'Amor': np.NaN,
                         'Virtus': np.NaN,
                         'Tydides': np.NaN,
                         'Dives': np.NaN,
                         'Aetna': np.NaN},
        # abs_filepath would be here
        'note_exists': {'Sussudio': True,
                        'Brevissimus moenia': True,
                        'Ne fuit': True,
                        'Alimenta': True,
                        'Vulnera ubera': True,
                        'Causam mihi': True,
                        'Tarpeia': False,
                        'Caelum': False,
                        'Vita': False,
                        'Aras Teucras': False,
                        'Manus': False,
                        'Bacchus': False,
                        'Amor': False,
                        'Virtus': False,
                        'Tydides': False,
                        'Dives': False,
                        'Aetna': False},
        'n_backlinks': {'Sussudio': 0,
                        'Brevissimus moenia': 1,
                        'Ne fuit': 2,
                        'Alimenta': 0,
                        'Vulnera ubera': 0,
                        'Causam mihi': 1,
                        'Tarpeia': 3,
                        'Caelum': 3,
                        'Vita': 3,
                        'Aras Teucras': 1,
                        'Manus': 3,
                        'Bacchus': 2,
                        'Amor': 2,
                        'Virtus': 1,
                        'Tydides': 1,
                        'Dives': 1,
                        'Aetna': 1},
        'n_wikilinks': {'Sussudio': 0.0,
                        'Brevissimus moenia': 3.0,
                        'Ne fuit': 6.0,
                        'Alimenta': 9.0,
                        'Vulnera ubera': 3.0,
                        'Causam mihi': 4.0,
                        'Tarpeia': np.NaN,
                        'Caelum': np.NaN,
                        'Vita': np.NaN,
                        'Aras Teucras': np.NaN,
                        'Manus': np.NaN,
                        'Bacchus': np.NaN,
                        'Amor': np.NaN,
                        'Virtus': np.NaN,
                        'Tydides': np.NaN,
                        'Dives': np.NaN,
                        'Aetna': np.NaN}
    }


@pytest.fixture
def actual_connected_vault():
    return Vault(WKD / 'tests/vault-stub').connect()


@pytest.fixture
def actual_metadata_df(actual_connected_vault):
    return actual_connected_vault.get_note_metadata()


def test_get_metadata_cols(actual_metadata_df):
    assert isinstance(actual_metadata_df, pd.DataFrame)

    expected_cols = ['rel_filepath', 'abs_filepath',
                     'note_exists',
                     'n_backlinks', 'n_wikilinks']
    assert actual_metadata_df.columns.tolist() == expected_cols


def test_get_metadata_dtypes(actual_metadata_df):
    assert actual_metadata_df['rel_filepath'].dtype == 'object'
    assert actual_metadata_df['abs_filepath'].dtype == 'object'
    assert actual_metadata_df['note_exists'].dtype == 'bool'
    assert actual_metadata_df['n_backlinks'].dtype == 'int'
    assert actual_metadata_df['n_wikilinks'].dtype == 'float'


def test_get_metadata_rel_filepath(actual_metadata_df,
                                   expected_metadata_dict):
    TEST_COL = 'rel_filepath'

    actual_series = actual_metadata_df[TEST_COL]
    expected_series = (pd.Series(expected_metadata_dict.get(TEST_COL),
                                 name=TEST_COL)
                       .rename_axis('note'))
    assert_series_equal(actual_series, expected_series)


def test_get_metadata_note_exists(actual_metadata_df,
                                  expected_metadata_dict):
    TEST_COL = 'note_exists'

    actual_series = actual_metadata_df[TEST_COL]
    expected_series = (pd.Series(expected_metadata_dict.get(TEST_COL),
                                 name=TEST_COL)
                       .rename_axis('note'))
    assert_series_equal(actual_series, expected_series)


def test_get_metadata_wikilinks(actual_metadata_df,
                                expected_metadata_dict):
    TEST_COL = 'n_wikilinks'

    actual_series = actual_metadata_df[TEST_COL]
    expected_series = (pd.Series(expected_metadata_dict.get(TEST_COL),
                                 name=TEST_COL)
                       .rename_axis('note'))
    assert_series_equal(actual_series, expected_series)


def test_get_metadata_backlinks(actual_metadata_df,
                                expected_metadata_dict):
    TEST_COL = 'n_backlinks'

    actual_series = actual_metadata_df[TEST_COL]
    expected_series = (pd.Series(expected_metadata_dict.get(TEST_COL),
                                 name=TEST_COL)
                       .rename_axis('note'))
    assert_series_equal(actual_series, expected_series)


def test_backlink_and_wikilink_totals_equal(actual_metadata_df):
    # every wikilink is another note's backlink
    assert (actual_metadata_df['n_backlinks'].sum()
            == actual_metadata_df['n_wikilinks'].sum())


def test_backlink_individual_notes(actual_connected_vault):
    actual_bl_ix = actual_connected_vault.backlinks_index

    assert isinstance(actual_bl_ix, dict)

    expected_bl_subset = {
        'Sussudio': [],
        'Alimenta': [],
        'Tarpeia': ['Brevissimus moenia', 'Alimenta', 'Vulnera ubera'],
        'Ne fuit': ['Alimenta', 'Causam mihi']
    }

    for k in list(expected_bl_subset.keys()):
        assert set(expected_bl_subset.get(k)) == set(actual_bl_ix.get(k))

    with pytest.raises(ValueError):
        actual_connected_vault.get_backlinks("Note that isn't in vault at all")

    # check that every note is in the backlinks_index
    graph_nodes = [n for n in actual_connected_vault.graph.nodes]
    assert (len(actual_bl_ix)
            == (actual_connected_vault.graph.number_of_nodes()))
    for k in list(expected_bl_subset.keys()):
        assert k in graph_nodes


def test_backlink_counts(actual_connected_vault):
    expected_bl_count_subset = {
        'Sussudio': {},
        'Alimenta': {},
        'Tarpeia': {'Brevissimus moenia': 1,
                    'Alimenta': 1,
                    'Vulnera ubera': 1},
        'Ne fuit': {'Alimenta': 1,
                    'Causam mihi': 1}
    }

    for k in list(expected_bl_count_subset.keys()):
        assert (actual_connected_vault.get_backlink_counts(k)
                == expected_bl_count_subset.get(k))

    with pytest.raises(ValueError):
        actual_connected_vault.get_backlink_counts("Note that isn't in vault at all")


def test_wikilink_individual_notes(actual_connected_vault):
    actual_wl_ix = actual_connected_vault.wikilinks_index

    assert isinstance(actual_wl_ix, dict)

    # these notes exist
    expected_wl_subset = {
        'Sussudio': [],
        'Alimenta': ['Manus', 'Bacchus', 'Amor', 'Ne fuit', 'Virtus',
                     'Brevissimus moenia', 'Tarpeia', 'Tydides', 'Vita'],
        'Ne fuit': ['Aras Teucras', 'Manus', 'Bacchus',
                    'Amor', 'Caelum', 'Causam mihi']
    }

    assert (actual_connected_vault.get_wikilinks('Alimenta')
            == expected_wl_subset.get('Alimenta'))

    for k in list(expected_wl_subset.keys()):
        # list - sequence the links appear in notes
        assert expected_wl_subset.get(k) == actual_wl_ix.get(k)

    with pytest.raises(ValueError):
        actual_connected_vault.get_wikilinks('Tarpeia')

    # check that every existing note (file) has wikilink info
    assert len(actual_wl_ix) == len(actual_connected_vault.file_index)
    for k in list(actual_wl_ix.keys()):
        assert isinstance(actual_connected_vault.file_index.get(k),
                          Path)
