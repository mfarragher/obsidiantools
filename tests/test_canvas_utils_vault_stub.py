import pytest
from pathlib import Path


from obsidiantools.canvas_utils import get_canvas_relpaths_matching_subdirs


# NOTE: run the tests from the project dir.
WKD = Path().cwd()


@pytest.fixture
def actual_vault_path():
    return WKD / 'tests/vault-stub'


def test_get_canvas_relpaths_matching_subdirs(actual_vault_path):
    actual_w_root = get_canvas_relpaths_matching_subdirs(
        actual_vault_path, include_root=True)

    # not including files directly in vault root:
    actual_wo_root = get_canvas_relpaths_matching_subdirs(
        actual_vault_path, include_root=False)
    expected_in_root = [Path('Crazy wall.canvas'),
                        Path('Crazy wall 2.canvas')]
    assert (set(actual_w_root).difference(actual_wo_root)
            == set(expected_in_root))

    # same result but via the other kwarg:
    actual_w_lipsum_only = get_canvas_relpaths_matching_subdirs(
        actual_vault_path, include_subdirs=['lipsum'])
    assert (set(actual_w_lipsum_only).difference(actual_wo_root)
            == set(expected_in_root))

    # both kwargs not default:
    actual_w_lipsum_only = get_canvas_relpaths_matching_subdirs(
        actual_vault_path, include_subdirs=['lipsum'], include_root=False)
    assert (set(actual_w_lipsum_only).difference(actual_wo_root)
            == set())
