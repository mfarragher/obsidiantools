import json
from pathlib import Path
from ._io import (get_relpaths_from_dir,
                  get_relpaths_matching_subdirs)


def get_canvas_relpaths_from_dir(dir_path: Path) -> list[Path]:
    """Get list of relative paths for canvas files in a given directory,
    including any subdirectories.

    Thus if the vault directory is the argument, then the function returns
    a list of all the canvas files found in the vault.

    Args:
        dir_path (pathlib Path): Path object representing the directory
            to search.

    Returns:
        list of Path objects
    """
    return get_relpaths_from_dir(dir_path, extension='canvas')


def get_canvas_relpaths_matching_subdirs(dir_path: Path, *,
                                         include_subdirs: list = None,
                                         include_root: bool = True) -> list[Path]:
    """Get list of relative paths for canvas files in a given directory,
    filtered to include specified subdirectories (with include_subdirs
    kwarg).  The default arguments align with get_canvas_relpaths_from_dir
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
        include_subdirs (list, optional): list of string paths to include
            in the filtered list of md files (e.g. ['p1', 'p2', 'p3/sp1']).
            If no list is specified, then no filtering is done on paths.
            Defaults to None.
        include_root (bool, optional): include files that are directly in
            the dir_path (root dir).  Defaults to True.

    Returns:
        list of Path objects
    """
    return get_relpaths_matching_subdirs(
        dir_path,
        extension='canvas',
        include_subdirs=include_subdirs,
        include_root=include_root)


def get_canvas_content(filepath: Path) -> dict:
    """Get JSON content from canvas file as a Python dict.

    Args:
        filepath (Path): Path object representing the canvas file.

    Returns:
        dict
    """
    with open(filepath, encoding='utf-8') as f:
        json_as_dict = json.load(f)
    return json_as_dict
