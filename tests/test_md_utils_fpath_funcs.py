import pytest

from obsidian_tools.md_utils import (_get_html_from_md_file,
                                     _get_ascii_plaintext_from_md_file)


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
