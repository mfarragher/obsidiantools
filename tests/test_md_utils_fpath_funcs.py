from pathlib import Path
import pytest

from obsidiantools.md_utils import (_get_html_from_md_file,
                                    get_source_text_from_md_file)
from obsidiantools.md_utils import (get_md_relpaths_from_dir,
                                    get_md_links,
                                    get_unique_wikilinks,
                                    get_wikilinks)


@pytest.fixture
def mocker_md_file(mocker):
    mocked_output = mocker.mock_open()
    mocker.patch('builtins.open', mocked_output)
    return mocked_output


def test_get_md_relpaths_from_dir(tmp_path):
    # test fake dir returns list of pathlike objs (with md ext)
    actual_relpaths = get_md_relpaths_from_dir(tmp_path)

    assert isinstance(actual_relpaths, list)
    for p in actual_relpaths:
        assert isinstance(p, Path)
        assert p.suffix == 'md'


def test_get_html_from_md_file(mocker_md_file):
    # test fake file open returns str
    actual_html = _get_html_from_md_file(mocker_md_file)

    assert isinstance(actual_html, str)


def test_get_source_text_from_md_file(mocker_md_file):
    # test fake file open returns str
    actual_txt = get_source_text_from_md_file(mocker_md_file)

    assert isinstance(actual_txt, str)


def test_get_md_links(mocker_md_file):
    # test fake file open returns list

    actual_links = get_md_links(mocker_md_file)
    assert isinstance(actual_links, list)


def test_get_unique_wikilinks(mocker_md_file):
    # test fake file open returns list

    actual_links = get_unique_wikilinks(mocker_md_file)
    assert isinstance(actual_links, list)


def test_get_wikilinks(mocker_md_file):
    # test fake file open returns list

    actual_links = get_wikilinks(mocker_md_file)
    assert isinstance(actual_links, list)
