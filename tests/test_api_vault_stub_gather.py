import pytest
from pathlib import Path


from obsidiantools.api import Vault

# NOTE: run the tests from the project dir.
WKD = Path().cwd()


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


def test_vault_not_gathered(actual_unconnected_vault):
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


def test_source_text_existing_file(actual_gathered_vault_defaults):
    actual_in_text = (actual_gathered_vault_defaults
                      .get_source_text('Isolated note'))
    expected_start = '# Isolated note'
    expected_end = 'an isolated note ~~an orphan~~.\n'
    assert actual_in_text.startswith(expected_start)
    assert actual_in_text.endswith(expected_end)


def test_readable_text_existing_file(actual_gathered_vault_defaults):
    actual_in_text = (actual_gathered_vault_defaults
                      .get_readable_text('Sussudio'))
    expected_start = '# Sussudio'
    expected_end = '\\- #hash_char_not_tag\n'
    assert actual_in_text.startswith(expected_start)
    assert actual_in_text.endswith(expected_end)


def test_isolated_note_md_text(actual_gathered_vault_defaults):
    expected_text = r"""# Isolated note

This is an isolated note ~~an orphan~~.
"""

    assert actual_gathered_vault_defaults.is_gathered

    actual_text = actual_gathered_vault_defaults.get_source_text('Isolated note')
    assert actual_text == expected_text


def test_all_files_are_in_source_text_index(actual_gathered_vault_defaults):
    file_keys = set(actual_gathered_vault_defaults.md_file_index.keys())
    text_keys = set(actual_gathered_vault_defaults.source_text_index.keys())
    assert file_keys == text_keys


def test_all_files_are_in_readable_text_index(actual_gathered_vault_defaults):
    file_keys = set(actual_gathered_vault_defaults.md_file_index.keys())
    text_keys = set(actual_gathered_vault_defaults.readable_text_index.keys())
    assert file_keys == text_keys


def test_sussudio_readable_text(actual_gathered_vault_defaults):
    """Some nuances on how readable text is different vs source text:
    - Code, LaTeX and embedded files are removed for readable text.
    - Wikilinks, links & tags will better reflect how they look in md preview
        in the readable text.
    - Double spaces in source text become single spaces in readable text.

    Neither form of text will have front matter.
    """
    expected_text = r"""# Sussudio

Another word with absolutely no meaning 😄

This will be a note inside the vault dir. Others will be lipsum in a subdirectory.

The song has been compared to the Prince's "1999" ( #y1982 ) <\- oh look, a tag!

More tags: \- #y_1982 \- #y-1982 \- #y1982/sep \- #y2000/party-over/oops/out-of-time

However these shouldn't be recognised as tags: \- (#y1985 ) \- #1985 \- American Psycho (film)#Patrick Bateman \- #hash_char_not_tag
"""
    actual_text = actual_gathered_vault_defaults.get_readable_text('Sussudio')
    assert actual_text == expected_text
