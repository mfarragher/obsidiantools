import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from pandas.testing import (assert_series_equal,
                            assert_frame_equal)


from obsidiantools.api import Vault
from obsidiantools._constants import METADATA_DF_COLS_GENERIC_TYPE

# NOTE: run the tests from the project dir.
WKD = Path().cwd()


@pytest.fixture
def expected_metadata_dict():
    return {
        'rel_filepath': {'Sussudio': Path('Sussudio.md'),
                         'Isolated note': Path('Isolated note.md'),
                         'Brevissimus moenia': Path('lipsum/Brevissimus moenia.md'),
                         'Ne fuit': Path('lipsum/Ne fuit.md'),
                         'Alimenta': Path('lipsum/Alimenta.md'),
                         'Vulnera ubera': Path('lipsum/Vulnera ubera.md'),
                         'lipsum/Isolated note': Path('lipsum/Isolated note.md'),
                         'Causam mihi': Path('lipsum/Causam mihi.md'),
                         'American Psycho (film)': np.NaN,
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
                        'Isolated note': True,
                        'Brevissimus moenia': True,
                        'Ne fuit': True,
                        'Alimenta': True,
                        'Vulnera ubera': True,
                        'lipsum/Isolated note': True,
                        'Causam mihi': True,
                        'American Psycho (film)': False,
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
                        'Isolated note': 0,
                        'Brevissimus moenia': 1,
                        'Ne fuit': 2,
                        'Alimenta': 0,
                        'Vulnera ubera': 0,
                        'lipsum/Isolated note': 0,
                        'Causam mihi': 1,
                        'American Psycho (film)': 1,
                        'Tarpeia': 3,
                        'Caelum': 3,
                        'Vita': 3,
                        'Aras Teucras': 1,
                        'Manus': 3,
                        'Bacchus': 5,
                        'Amor': 2,
                        'Virtus': 1,
                        'Tydides': 1,
                        'Dives': 1,
                        'Aetna': 1},
        'n_wikilinks': {'Sussudio': 1.0,
                        'Isolated note': 0.0,
                        'Brevissimus moenia': 3.0,
                        'Ne fuit': 6.0,
                        'Alimenta': 12.0,
                        'Vulnera ubera': 3.0,
                        'lipsum/Isolated note': 0.0,
                        'Causam mihi': 4.0,
                        'American Psycho (film)': np.NaN,
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
        'n_tags': {'Sussudio': 5.0,
                   'Isolated note': 0.0,
                   'Brevissimus moenia': 0.0,
                   'Ne fuit': 0.0,
                   'Alimenta': 0.0,
                   'Vulnera ubera': 0.0,
                   'lipsum/Isolated note': 0.0,
                   'Causam mihi': 0.0,
                   'American Psycho (film)': np.NaN,
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
        'n_embedded_files': {'Isolated note': 0.0,
                             'Sussudio': 2.0,
                             'Brevissimus moenia': 0.0,
                             'Ne fuit': 0.0,
                             'Alimenta': 0.0,
                             'Vulnera ubera': 0.0,
                             'lipsum/Isolated note': 0.0,
                             'Causam mihi': 0.0,
                             'American Psycho (film)': np.NaN,
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
def expected_embedded_files_index():
    return {'Isolated note': [],
            'lipsum/Isolated note': [],
            'Sussudio': ['Sussudio.mp3', '1999.flac'],
            'Brevissimus moenia': [],
            'Ne fuit': [],
            'Alimenta': [],
            'Vulnera ubera': [],
            'Causam mihi': []}


@pytest.fixture
def expected_front_matter_index():
    return {'Isolated note': {},
            'lipsum/Isolated note': {},
            'Sussudio': {'title': 'Sussudio',
                         'artist': 'Phil Collins',
                         'category': 'music',
                         'year': 1985,
                         'url': 'https://www.discogs.com/Phil-Collins-Sussudio/master/106239',
                         'references': [[['American Psycho (film)']], 'Polka Party!'],
                         'chart_peaks': [{'US': 1}, {'UK': 12}]},
            'Brevissimus moenia': {},
            'Ne fuit': {},
            'Alimenta': {},
            'Vulnera ubera': {},
            'Causam mihi': {'title': 'Causam mihi',
                            'author': 'Ovid',
                            'category': 'literature',
                            'year': 8,
                            'language': 'la',
                            'description': '\\{\\{description\\}\\}'}}


@pytest.fixture
def expected_md_links_index():
    return {'Isolated note': [],
            'lipsum/Isolated note': [],
            'Sussudio': [],
            'Brevissimus moenia': ['http://www.alii.io/',
                                   'http://fronti.com/tumiseris.html'],
            'Ne fuit': ['http://vires.io/',
                        'http://excoquitprotinus.net/quae.html',
                        'http://medullis-me.net/novat',
                        'http://sedibus.io/levemmonstra'],
            'Alimenta': ['http://fugitaer.net/dignus',
                         'http://www.a-iuveni.com/',
                         'http://cibos.net/venulus-redito.html',
                         'http://et-pronus.com/',
                         'http://iuppiter.net/'],
            'Vulnera ubera': [],
            'Causam mihi': []}


@pytest.fixture
def expected_tags_main_only_index():
    return {'Isolated note': [],
            'lipsum/Isolated note': [],
            'Sussudio': ['y1982', 'y_1982', 'y-1982', 'y1982', 'y2000'],
            'Brevissimus moenia': [],
            'Ne fuit': [],
            'Alimenta': [],
            'Vulnera ubera': [],
            'Causam mihi': []}


@pytest.fixture
def expected_math_index():
    return {'Isolated note': [],
            'lipsum/Isolated note': [],
            'Sussudio': [],
            'Brevissimus moenia': [],
            'Ne fuit': [],
            'Alimenta': [],
            'Vulnera ubera': [],
            'Causam mihi': []}


@pytest.fixture
def actual_connected_vault():
    return Vault(WKD / 'tests/vault-stub').connect()


@pytest.fixture
def actual_connected_vault_md_files_only():
    return Vault(WKD / 'tests/vault-stub/lipsum').connect()


@pytest.fixture
def actual_metadata_df(actual_connected_vault):
    return actual_connected_vault.get_note_metadata()


def test_get_metadata_cols(actual_metadata_df):
    assert isinstance(actual_metadata_df, pd.DataFrame)

    expected_cols = ['rel_filepath', 'abs_filepath',
                     'note_exists',
                     'n_backlinks', 'n_wikilinks',
                     'n_tags',
                     'n_embedded_files',
                     'modified_time']
    assert actual_metadata_df.columns.tolist() == expected_cols


def test_get_metadata_dtypes(actual_metadata_df):
    assert actual_metadata_df['rel_filepath'].dtype == 'object'
    assert actual_metadata_df['abs_filepath'].dtype == 'object'
    assert actual_metadata_df['note_exists'].dtype == 'bool'
    assert actual_metadata_df['n_backlinks'].dtype == 'int'
    assert actual_metadata_df['n_wikilinks'].dtype == 'float'
    assert actual_metadata_df['n_tags'].dtype == 'float'
    assert actual_metadata_df['n_embedded_files'].dtype == 'float'
    assert actual_metadata_df['modified_time'].dtype == 'datetime64[ns]'


def test_get_metadata_rel_filepath(actual_metadata_df,
                                   expected_metadata_dict):
    TEST_COL = 'rel_filepath'

    actual_series = actual_metadata_df[TEST_COL]
    expected_series = (pd.Series(expected_metadata_dict.get(TEST_COL),
                                 name=TEST_COL)
                       .rename_axis('note'))
    assert_series_equal(actual_series, expected_series,
                        check_like=True)


def test_get_metadata_note_exists(actual_metadata_df,
                                  expected_metadata_dict):
    TEST_COL = 'note_exists'

    actual_series = actual_metadata_df[TEST_COL]
    expected_series = (pd.Series(expected_metadata_dict.get(TEST_COL),
                                 name=TEST_COL)
                       .rename_axis('note'))
    assert_series_equal(actual_series, expected_series,
                        check_like=True)


def test_get_metadata_wikilinks(actual_metadata_df,
                                expected_metadata_dict):
    TEST_COL = 'n_wikilinks'

    actual_series = actual_metadata_df[TEST_COL]
    expected_series = (pd.Series(expected_metadata_dict.get(TEST_COL),
                                 name=TEST_COL)
                       .rename_axis('note'))
    assert_series_equal(actual_series, expected_series,
                        check_like=True)


def test_get_metadata_backlinks(actual_metadata_df,
                                expected_metadata_dict):
    TEST_COL = 'n_backlinks'

    actual_series = actual_metadata_df[TEST_COL]
    expected_series = (pd.Series(expected_metadata_dict.get(TEST_COL),
                                 name=TEST_COL)
                       .rename_axis('note'))
    assert_series_equal(actual_series, expected_series,
                        check_like=True)


def test_get_metadata_tags(actual_metadata_df,
                           expected_metadata_dict):
    TEST_COL = 'n_tags'

    actual_series = actual_metadata_df[TEST_COL]
    expected_series = (pd.Series(expected_metadata_dict.get(TEST_COL),
                                 name=TEST_COL)
                       .rename_axis('note'))
    assert_series_equal(actual_series, expected_series,
                        check_like=True)


def test_backlink_and_wikilink_totals_equal(actual_metadata_df):
    # every wikilink is another note's backlink
    # equality is expected when canvas files are excluded from wikilinks list
    # for ANY VAULT under the defaults
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
                    'Causam mihi': 1},
        'Bacchus': {'Ne fuit': 1,
                    'Alimenta': 4}
    }

    for k in list(expected_bl_count_subset.keys()):
        assert (actual_connected_vault.get_backlink_counts(k)
                == expected_bl_count_subset.get(k))

    with pytest.raises(ValueError):
        actual_connected_vault.get_backlink_counts("Note that isn't in vault at all")


def test_wikilink_counts(actual_connected_vault):
    expected_wl_count_subset = {
        'Sussudio': {'American Psycho (film)': 1},
        'Isolated note': {},
        'Vulnera ubera': {'Caelum': 1,
                          'Tarpeia': 1,
                          'Vita': 1},
        'Ne fuit': {'Aras Teucras': 1,
                    'Manus': 1,
                    'Bacchus': 1,
                    'Amor': 1,
                    'Caelum': 1,
                    'Causam mihi': 1},
        'Causam mihi': {'Dives': 1,
                        'Manus': 1,
                        'Ne fuit': 1,
                        'Aetna': 1},
        'Brevissimus moenia': {'Tarpeia': 1,
                               'Caelum': 1,
                               'Vita': 1},
        'Alimenta': {'Manus': 1,
                     'Bacchus': 4,
                     'Amor': 1,
                     'Ne fuit': 1,
                     'Virtus': 1,
                     'Brevissimus moenia': 1,
                     'Tarpeia': 1,
                     'Tydides': 1,
                     'Vita': 1}
    }

    for k in list(expected_wl_count_subset.keys()):
        assert (actual_connected_vault.get_wikilink_counts(k)
                == expected_wl_count_subset.get(k))

    with pytest.raises(ValueError):
        actual_connected_vault.get_wikilink_counts("Note that isn't in vault at all")


def test_wikilink_individual_notes(actual_connected_vault):
    actual_wl_ix = actual_connected_vault.wikilinks_index

    assert isinstance(actual_wl_ix, dict)

    # these notes exist
    expected_wl_subset = {
        'Sussudio': ['American Psycho (film)'],
        'Alimenta': ['Manus', 'Bacchus', 'Amor', 'Ne fuit', 'Virtus',
                     'Brevissimus moenia', 'Tarpeia', 'Tydides', 'Vita',
                     'Bacchus', 'Bacchus', 'Bacchus'],
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
    assert len(actual_wl_ix) == len(actual_connected_vault.md_file_index)
    for k in list(actual_wl_ix.keys()):
        assert isinstance(actual_connected_vault.md_file_index.get(k),
                          Path)


def test_unique_wikilinks(actual_connected_vault):
    actual_u_wl_ix = actual_connected_vault.unique_wikilinks_index

    assert isinstance(actual_u_wl_ix, dict)

    # these notes exist
    expected_u_wl_subset = {
        'Sussudio': ['American Psycho (film)'],
        'Alimenta': ['Manus', 'Bacchus', 'Amor', 'Ne fuit', 'Virtus',
                     'Brevissimus moenia', 'Tarpeia', 'Tydides', 'Vita'],
        'Ne fuit': ['Aras Teucras', 'Manus', 'Bacchus',
                    'Amor', 'Caelum', 'Causam mihi']
    }

    assert (actual_u_wl_ix.get('Alimenta')
            == expected_u_wl_subset.get('Alimenta'))


def test_nonexistent_notes(actual_connected_vault, actual_metadata_df):
    expected_non_e_notes = ['Tarpeia', 'Caelum', 'Vita', 'Aras Teucras',
                            'Manus', 'Bacchus', 'Amor', 'Virtus',
                            'Tydides', 'Dives', 'Aetna',
                            'American Psycho (film)']

    assert isinstance(actual_connected_vault.nonexistent_notes, list)

    assert (set(actual_connected_vault.nonexistent_notes)
            == set(expected_non_e_notes))
    assert (set(actual_metadata_df.loc[~actual_metadata_df['note_exists'], :]
                .index.tolist())
            == set(expected_non_e_notes))


def test_isolated_notes(actual_connected_vault):
    expected_isol_notes = ['Isolated note', 'lipsum/Isolated note']

    assert isinstance(actual_connected_vault.isolated_notes, list)

    assert (set(actual_connected_vault.isolated_notes)
            == set(expected_isol_notes))

    # isolated notes can't have backlinks
    for n in actual_connected_vault.isolated_notes:
        assert actual_connected_vault.get_backlink_counts(n) == {}
    # isolated notes can't have wikilinks
    for n in actual_connected_vault.isolated_notes:
        assert actual_connected_vault.get_wikilinks(n) == []


def test_front_matter_index(
        actual_connected_vault, expected_front_matter_index):
    assert isinstance(actual_connected_vault.front_matter_index, dict)

    actual_front_matter_index = actual_connected_vault.front_matter_index
    assert actual_front_matter_index == expected_front_matter_index


def test_front_matter_sussudio(actual_connected_vault):
    expected_fm = {'title': 'Sussudio',
                   'artist': 'Phil Collins',
                             'category': 'music',
                             'year': 1985,
                             'url': 'https://www.discogs.com/Phil-Collins-Sussudio/master/106239',
                             'references': [[['American Psycho (film)']], 'Polka Party!'],
                             'chart_peaks': [{'US': 1}, {'UK': 12}]}

    actual_fm = actual_connected_vault.get_front_matter('Sussudio')
    assert actual_fm == expected_fm


def test_front_matter_constructorerror(actual_connected_vault):
    actual_fm = actual_connected_vault.get_front_matter('Causam mihi')
    assert actual_fm['description'] == '\\{\\{description\\}\\}'


def test_embedded_files_sussudio(actual_connected_vault):
    expected_files = ['Sussudio.mp3', '1999.flac']

    actual_files = actual_connected_vault.get_embedded_files('Sussudio')
    assert actual_files == expected_files


def test_nodes_gte_files(actual_connected_vault):
    act_f_len = len(actual_connected_vault.md_file_index)
    act_n_len = len(actual_connected_vault.wikilinks_index)

    assert act_n_len >= act_f_len


def test_embedded_files_index(
        actual_connected_vault, expected_embedded_files_index):
    actual_files_ix = actual_connected_vault.embedded_files_index
    assert actual_files_ix == expected_embedded_files_index


def test_math_index(
        actual_connected_vault, expected_math_index):
    actual_math_index = actual_connected_vault.math_index
    assert actual_math_index == expected_math_index


def test_md_links_index(
        actual_connected_vault, expected_md_links_index):
    actual_md_links_ix = actual_connected_vault.md_links_index
    assert actual_md_links_ix == expected_md_links_index


def test_tags_index(
        actual_connected_vault, expected_tags_main_only_index):
    actual_tags_ix = actual_connected_vault.tags_index
    assert actual_tags_ix == expected_tags_main_only_index


def test_unique_md_links(
        actual_connected_vault, expected_md_links_index):
    actual_u_md_links_ix = (actual_connected_vault.
                            _unique_md_links_index)
    # all notes in stub have unique md links:
    assert actual_u_md_links_ix == expected_md_links_index


def test_md_links_individual_notes(actual_connected_vault):
    actual_md_links = actual_connected_vault.get_md_links('Ne fuit')
    expected_md_links = ['http://vires.io/',
                         'http://excoquitprotinus.net/quae.html',
                         'http://medullis-me.net/novat',
                         'http://sedibus.io/levemmonstra']
    assert actual_md_links == expected_md_links


def test_tags_individual_notes(actual_connected_vault):
    actual_md_links = actual_connected_vault.get_tags('Ne fuit')
    expected_md_links = []
    assert actual_md_links == expected_md_links


def test_md_links_not_existing(actual_connected_vault):
    with pytest.raises(ValueError):
        actual_connected_vault.get_md_links('Tarpeia')


def test_tags_not_existing(actual_connected_vault):
    with pytest.raises(ValueError):
        actual_connected_vault.get_tags('Tarpeia')


def test_front_matter_not_existing(actual_connected_vault):
    with pytest.raises(ValueError):
        actual_connected_vault.get_front_matter('Tarpeia')


def test_embedded_notes_not_existing(actual_connected_vault):
    with pytest.raises(ValueError):
        actual_connected_vault.get_embedded_files('Tarpeia')


def test_media_file_metadata_df_empty(actual_connected_vault_md_files_only):
    # use the lipsum dir as the 'vault' dir (md only)
    df_media = (actual_connected_vault_md_files_only
                .get_media_file_metadata())

    assert len(df_media) == 0

    expected_cols = METADATA_DF_COLS_GENERIC_TYPE
    actual_cols = df_media.columns.tolist()
    assert actual_cols == expected_cols


def test_canvas_file_metadata_df_empty(actual_connected_vault_md_files_only):
    # use the lipsum dir as the 'vault' dir (md only)
    df_media = (actual_connected_vault_md_files_only
                .get_canvas_file_metadata())

    assert len(df_media) == 0

    expected_cols = METADATA_DF_COLS_GENERIC_TYPE
    actual_cols = df_media.columns.tolist()
    assert actual_cols == expected_cols


def test_all_file_metadata_df(actual_connected_vault):
    with pytest.warns(UserWarning):
        actual_all_df = actual_connected_vault.get_all_file_metadata()

    actual_note_df = actual_connected_vault.get_note_metadata()

    # check that notes metadata was only used:
    assert_frame_equal(
        actual_all_df.drop(columns=['graph_category']),
        actual_note_df.rename(columns={'note_exists': 'file_exists'}))

    # check that only notes are used for backlinks:
    assert (actual_all_df['n_backlinks'].sum()
            == (actual_all_df['n_wikilinks'].sum()))


def test_internal_canvas_backlink_counts_func_errors(
        actual_connected_vault):
    with pytest.raises(AttributeError):
        (actual_connected_vault.
         _get_backlink_counts_for_canvas_files_only())
