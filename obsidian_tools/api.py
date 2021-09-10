import networkx as nx
from collections import Counter

from .md_utils import (get_md_relpaths_from_dir, get_unique_wikilinks,
                       get_wikilinks)


class Vault:
    def __init__(self, dirpath):
        """A Vault object lets you dig into your Obsidian vault, by giving
        you a toolkit for analysing its contents.  Specify a dirpath to
        instantiate the class.  This class is intended to support multiple
        operating systems so pass a pathlib Path object.

        By calling CONNECT you generate a graph of your vault.
        All the wikilinks in the vault are used to produce the graph, to
        reflect how analytics are displayed in Obsidian, where links are
        counted rather than notes.  For example, if a note has 2 backlinks
        then there will be 2 wikilinks (to another note) visible when you do
        analysis of the edges & nodes.

        The API is fluent so you can set up your vault and connect your
        notes in one line:

        vault = Vault(dirpath).connect()

        The class supports subdirectories and relies heavily on relative
        paths for the API.

        Args:
            dirpath (pathlib Path): the directory to analyse.  This would
                typically be the vault's directory.  If you have a
                subdirectory of the vault with notes you want to inspect,
                then you could pass that.

        Methods for setup:
            connect

        Methods for analysis:
            get_backlinks
            get_backlink_counts

        Attributes:
            dirpath (arg)
            file_index
            graph
            is_connected
        """
        self._dirpath = dirpath
        self._file_index = self._get_md_relpaths_by_name()

        # graph setup
        self._graph = None
        self._is_connected = False

    @property
    def dirpath(self):
        """pathlib Path"""
        return self._dirpath

    @property
    def file_index(self):
        """dict: one-to-one mapping of filename (k) to relative path (v)"""
        return self._file_index

    @property
    def graph(self):
        """networkx Graph"""
        return self._graph

    @property
    def is_connected(self):
        """Bool: has the connect function been called to set up graph?"""
        return self._is_connected

    def connect(self):
        """connect your notes together by representing the vault as a
        Networkx graph object, G.

        With your vault instantiated, set up the graph through:
            vault.connect()

        The graph G is written to the 'graph' attribute.
        """
        if not self._is_connected:
            # default graph to mirror Obsidian's link counts
            wiki_link_map = self._get_wikilinks_by_md_filename()
            G = nx.MultiDiGraph(wiki_link_map)
            self._graph = G

            self._is_connected = True

        return self  # fluent

    def get_backlinks(self, filename):
        """Get backlinks for a note (given its filename).

        Args:
            filename (str): the filename string that is in the file_index.
                This is NOT the filepath!

        Returns:
            list
        """
        if not self._is_connected:
            raise AttributeError('Connect notes before calling the function')

        if filename not in self._file_index:
            raise ValueError('{} not found in file_index.'.format(filename))
        else:
            return [n[0] for n in self._graph.in_edges(filename)]

    def get_backlink_counts(self, filename):
        """Get counts of backlinks for a note (given its filename).

        Args:
            filename (str): the filename string that is in the file_index.
                This is NOT the filepath!

        Returns:
            dict of integers >= 1
        """
        if not self._is_connected:
            raise AttributeError('Connect notes before calling the function')

        if filename not in self._file_index:
            raise ValueError('{} not found in file_index.'.format(filename))
        else:
            backlinks = self.get_backlinks(filename)
            return dict(Counter(backlinks))

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

    def _get_wikilinks_by_md_filename(self):
        """Return k,v pairs
        where k is the md filename
        and v is list of ALL wikilinks found in k"""
        return {k: get_wikilinks(self._dirpath / v)
                for k, v in self._file_index.items()}

    def _get_unique_wikilinks_by_md_filename(self):
        """Return k,v pairs
        where k is the md filename
        and v is list of UNIQUE wikilinks found in k"""
        return {k: get_unique_wikilinks(self._dirpath / v)
                for k, v in self._file_index.items()}
