from pathlib import Path
from glob import glob
import numpy as np


def get_relpaths_from_dir(dir_path: Path, *, extension: str) -> list[Path]:
    """Get list of relative paths for {extension} files in a given directory,
    including any subdirectories.

    Thus if the vault directory is the argument, then the function returns
    a list of all the {extension} files found in the vault.

    Args:
        dir_path (pathlib Path): Path object representing the directory
            to search.
        extension (str): file extension like 'md' or 'canvas'.

    Returns:
        list of Path objects
    """
    relpaths_list = [Path(p).relative_to(dir_path)
                     for p in glob(f"{dir_path}/**/*.{extension}",
                     recursive=True)]
    return relpaths_list


def get_relpaths_matching_subdirs(dir_path: Path, *,
                                  extension: str,
                                  include_subdirs: list = None,
                                  include_root: bool = True) -> list[Path]:
    """Get list of relative paths for {extension} files in a given directory,
    filtered to include specified subdirectories (with include_subdirs
    kwarg).  The default arguments align with get_relpaths_from_dir
    function, but this function enables more flexibility.

    For example, if you had a vault with folders named by category, and
    filter them like this in Obsidian:
        path:Category1/ OR path:Category2/ OR path:Category4/
    then you can use the include_subdirs kwarg to do that with this function:
        include_subdirs = ['Category1', 'Category2', 'Category4']

    You can also specify deeper levels to filter on, e.g.:
        include_subdirs = ['Category1/TopicA', 'Category1/TopicB']

    Args:
        dir_path (pathlib Path): Path object representing the directory
            to search.
        extension (str): file extension like 'md' or 'canvas'.
        include_subdirs (list, optional): list of string paths to include
            in the filtered list of md files (e.g. ['p1', 'p2', 'p3/sp1']).
            If no list is specified, then no filtering is done on paths.
            Defaults to None.
        include_root (bool, optional): include files that are directly in
            the dir_path (root dir).  Defaults to True.

    Returns:
        list of Path objects
    """
    # Obsidian's 'shortest path' for files uses forward slash across
    # operating systems, so as_posix() is used to yield paths with
    # forward slash consistently here.

    if include_subdirs:
        include_subdirs_final = [str(Path(i).as_posix())
                                 for i in include_subdirs]

    if not include_subdirs and include_root:
        return get_relpaths_from_dir(dir_path,
                                     extension=extension)
    elif not include_subdirs and not include_root:
        return [i for i in get_relpaths_from_dir(dir_path,
                                                 extension=extension)
                if str(i.parent.as_posix()) != '.']
    else:
        if include_root:
            return [i for i in get_relpaths_from_dir(dir_path,
                                                     extension=extension)
                    if str(i.parent.as_posix())
                    in include_subdirs_final + ['.']]
        else:
            return [i for i in get_relpaths_from_dir(dir_path,
                                                     extension=extension)
                    if str(i.parent.as_posix())
                    in include_subdirs_final]


def _get_valid_filepaths_by_ext_set(dirpath: Path, *,
                                    exts: set[str]):
    all_files = [p.relative_to(dirpath)
                 for p in Path(dirpath).glob("**/*")
                 if p.suffix in exts]
    return all_files


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
