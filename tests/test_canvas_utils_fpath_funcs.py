from pathlib import Path
import pytest


from obsidiantools.canvas_utils import (get_canvas_relpaths_from_dir)


@pytest.fixture
def mocker_md_file(mocker):
    mocked_output = mocker.mock_open()
    mocker.patch('builtins.open', mocked_output)
    return mocked_output


def test_get_canvas_relpaths_from_dir(tmp_path):
    # test fake dir returns list of pathlike objs (with md ext)
    actual_relpaths = get_canvas_relpaths_from_dir(tmp_path)

    assert isinstance(actual_relpaths, list)
    for p in actual_relpaths:
        assert isinstance(p, Path)
        assert p.suffix == 'canvas'
