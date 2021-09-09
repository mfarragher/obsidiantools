import pytest

from obsidian_tools.md_utils import (_get_html_from_md_file,
                                     _get_ascii_plaintext_from_md_file)
from obsidian_tools.md_utils import (get_md_links,
                                     get_wiki_links)

# tmp_path

@pytest.fixture
def mocker_md_file(mocker):
    mocked_output = mocker.mock_open()
    mocker.patch('builtins.open', mocked_output)
    return mocked_output


def test_get_html_from_md_file(mocker_md_file):
    # test fake file open returns str
    actual_html = _get_html_from_md_file(mocker_md_file)

    assert isinstance(actual_html, str)


def test_get_plaintext_from_md_file(mocker_md_file):
    # test fake file open returns str
    actual_txt = _get_ascii_plaintext_from_md_file(mocker_md_file)

    assert isinstance(actual_txt, str)


def test_get_md_links(mocker_md_file):
    # test fake file open returns list

    actual_links = get_md_links(mocker_md_file)
    assert isinstance(actual_links, list)


def test_get_wiki_links(mocker_md_file):
    # test fake file open returns list

    actual_links = get_wiki_links(mocker_md_file)
    assert isinstance(actual_links, list)
