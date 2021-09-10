from .md_utils import get_md_relpaths_from_dir, get_unique_wiki_links


class Vault:
    def __init__(self, filepath):
        """A Vault object lets you dig into your Obsidian vault, by giving
        you a toolkit for analysing its contents.  Specify a filepath to
        instantiate the class.  This class is intended to support multiple
        operating systems so pass a pathlib Path object.

        The class supports subdirectories and relies heavily on relative
        paths for the API.

        Args:
            filepath (pathlib Path): the directory to analyse.  This would
                typically be the vault's directory.  If you have a
                subdirectory of the vault with notes you want to inspect,
                then you could pass that.
        """
        self._filepath = filepath

    @property
    def filepath(self):
        """pathlib Path"""
        return self._filepath

    def get_md_relpaths(self):
        """Return list of filepaths *relative* to the directory instantiated
        for the class.

        Returns:
            list
        """
        return get_md_relpaths_from_dir(self._filepath)

    def get_md_relpaths_by_name(self):
        """Return k,v pairs
        where k is the file name
        and v is the relpath of the md file

        Returns:
            dict
        """
        return {f.stem: f for f in self.get_md_relpaths()}

    def _get_unique_wiki_links_by_md_relpaths(self):
        """Return k,v pairs
        where k is relpath of vault page
        and v is list of wiki links found in k"""
        relpaths = get_md_relpaths_from_dir(self._filepath)
        return {f: get_unique_wiki_links(self._filepath / f) for f in relpaths}

    def _get_unique_wiki_links_by_md_filename(self):
        links_to_relpaths = self._get_unique_wiki_links_by_md_relpaths()
        return {k.stem: v for k, v in links_to_relpaths.items()}
