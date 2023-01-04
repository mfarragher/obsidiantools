from pathlib import Path
import numpy as np
from ._constants import (IMG_EXT_SET, AUDIO_EXT_SET,
                         VIDEO_EXT_SET, PDF_EXT_SET)
from ._io import _get_valid_filepaths_by_ext_set


def _get_all_valid_media_file_relpaths(dirpath):
    return (_get_valid_filepaths_by_ext_set(
        dirpath,
        exts=(IMG_EXT_SET | AUDIO_EXT_SET
              | VIDEO_EXT_SET | PDF_EXT_SET)))


def _get_shortest_path_by_filename(relpaths_list: list[Path]) -> dict[str, Path]:
    # get filename w/ ext only:
    all_file_names_list = [f.name for f in relpaths_list]

    # get indices of dupe 'filename w/ ext':
    _, inverse_ix, counts = np.unique(
        np.array(all_file_names_list),
        return_inverse=True,
        return_counts=True,
        axis=0)
    dupe_names_ix = np.where(counts[inverse_ix] > 1)[0]

    # get shortest paths via mask:
    shortest_paths_arr = np.array(all_file_names_list, dtype=object)
    shortest_paths_arr[dupe_names_ix] = np.array(
        [str(fpath)
         for fpath in relpaths_list])[dupe_names_ix]
    return {fn: path for fn, path in zip(shortest_paths_arr, relpaths_list)}
