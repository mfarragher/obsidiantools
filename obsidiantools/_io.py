from pathlib import Path
from glob import glob


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
