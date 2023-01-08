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
