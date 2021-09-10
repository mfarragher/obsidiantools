from .md_utils import (get_md_relpaths_from_dir, get_unique_wiki_links,
                       get_wiki_links)


class Vault:
    def __init__(self, dirpath):
        """A Vault object lets you dig into your Obsidian vault, by giving
        you a toolkit for analysing its contents.  Specify a dirpath to
        instantiate the class.  This class is intended to support multiple
        operating systems so pass a pathlib Path object.

        The class supports subdirectories and relies heavily on relative
        paths for the API.

        Args:
            dirpath (pathlib Path): the directory to analyse.  This would
                typically be the vault's directory.  If you have a
                subdirectory of the vault with notes you want to inspect,
                then you could pass that.

        Attributes:
            dirpath
        """
        self._dirpath = dirpath
        self._file_index = self._get_md_relpaths_by_name()

    @property
    def dirpath(self):
        """pathlib Path"""
        return self._dirpath

    @property
    def file_index(self):
        """dict: one-to-one mapping of filename (k) to relative path (v)"""
        return self._file_index

    def _get_md_relpaths(self):
        """Return list of filepaths *relative* to the directory instantiated
        for the class.

        Returns:
            list
        """
        return get_md_relpaths_from_dir(self._dirpath)

    def _get_md_relpaths_by_name(self):
        """Return k,v pairs
        where k is the file name
        and v is the relpath of the md file

        Returns:
            dict
        """
        return {f.stem: f for f in self._get_md_relpaths()}

    def _get_wiki_links_by_md_filename(self):
        """Return k,v pairs
        where k is the md filename
        and v is list of ALL wiki links found in k"""
        return {k: get_wiki_links(self._dirpath / v)
                for k, v in self._file_index.items()}

    def _get_unique_wiki_links_by_md_filename(self):
        """Return k,v pairs
        where k is the md filename
        and v is list of UNIQUE wiki links found in k"""
        return {k: get_unique_wiki_links(self._dirpath / v)
                for k, v in self._file_index.items()}
