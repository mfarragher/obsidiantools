import os
import networkx as nx
import numpy as np
import pandas as pd
from collections import Counter
from pathlib import Path

from .md_utils import (get_md_relpaths_matching_subdirs, get_unique_md_links,
                       get_unique_wikilinks,
                       get_md_links,
                       get_wikilinks,
                       get_embedded_files,
                       get_front_matter,
                       get_tags,
                       _get_source_text_from_md_file,
                       _get_readable_text_from_md_file,
                       _get_all_latex_from_md_file)


class Vault:
    def __init__(self, dirpath, *, include_subdirs=None, include_root=True):
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

        By calling GATHER you store the plaintext of your vault in the notes
        index attribute.  You can specify rules for how the text is
        processed, e.g. whether code blocks should be removed.

        The API is fluent so you can set up your vault, by connecting
        and gathering your notes in one line:

        vault = Vault(dirpath).connect().gather()

        The class supports subdirectories and relies heavily on relative
        paths for the API.

        Args:
            dirpath (pathlib Path): the directory to analyse.  This would
                typically be the vault's directory.  If you have a
                subdirectory of the vault with notes you want to inspect,
                then you could pass that.
            include_subdirs (list, optional): list of string paths to include
                in the filtered list of md files (e.g. ['p1', 'p2', 'p3/sp1']).
                If no list is specified, then no filtering is done on paths.
                Defaults to None.
            include_root (bool, optional): include files that are directly in
                the dir_path (root dir).  Defaults to True.

        Methods for setup:
            connect: connect notes in a graph
            gather: gather text content of notes

        Methods for analysis of an individual note:
            get_backlinks
            get_backlink_counts
            get_wikilinks
            get_embedded_files
            get_math
            get_front_matter
            get_md_links
            get_tags
            get_source_text

        Methods for analysis across multiple notes:
            get_note_metadata

        Attributes:
            dirpath (arg)
            file_index
            backlinks_index
            wikilinks_index
            embedded_files_index
            math_index
            md_links_index
            tags_index
            nonexistent_notes
            isolated_notes
            graph
            source_text_index
            readable_text_index
            is_connected
            is_gathered
        """
        self._dirpath = dirpath
        self._file_index = self._get_md_relpaths_by_name(
            include_subdirs=include_subdirs,
            include_root=include_root)

        # graph setup
        self._graph = None
        self._is_connected = False
        self._is_gathered = False
        self._backlinks_index = {}
        self._wikilinks_index = {}
        self._embedded_files_index = {}
        self._math_index = {}
        self._md_links_index = {}
        self._tags_index = {}
        self._nonexistent_notes = []
        self._isolated_notes = []
        self._front_matter_index = {}
        self._source_text_index = {}
        self._readable_text_index = {}

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
    def backlinks_index(self):
        """dict of lists: note name (k) to lists (v).  v is [] if k
        has no backlinks."""
        return self._backlinks_index

    @property
    def wikilinks_index(self):
        """dict of lists: filename (k) to lists (v).  v is [] if k
        has no wikilinks."""
        return self._wikilinks_index

    @property
    def embedded_files_index(self):
        """dict: note name (k) to list of embedded file strimg (v).
        v is [] if k has no embedded files."""
        return self._embedded_files_index

    @property
    def math_index(self):
        """dict: note name (k) to list of LaTeX math strimg (v).  v is [] if
        k has no LaTeX."""
        return self._math_index

    @property
    def md_links_index(self):
        """dict of lists: filename (k) to lists (v).  v is [] if k
        has no markdown links."""
        return self._md_links_index

    @property
    def tags_index(self):
        """dict of lists: filename (k) to lists (v).  v is [] if k
        has no tags."""
        return self._tags_index

    @property
    def nonexistent_notes(self):
        """list: notes without files, i.e. the notes have backlink(s) but
        their md files don't exist yet.

        They are ideas floating around in the Obsidian graph... waiting to
        be created as actual notes one day :-)"""
        return self._nonexistent_notes

    @property
    def isolated_notes(self):
        """list: notes (with their own md files) that lack backlinks and
        lack wikilinks.  They are not connected to other notes in the
        Obsidian graph at all."""
        return self._isolated_notes

    @property
    def front_matter_index(self):
        """dict: note name (k) to front matter (v).  v is {} if no front
        matter was extracted from note."""
        return self._front_matter_index

    @property
    def is_connected(self):
        """Bool: has the connect function been called to set up graph?"""
        return self._is_connected

    @property
    def is_gathered(self):
        """Bool: has the gather function been called to gather text?"""
        return self._is_gathered

    @property
    def source_text_index(self):
        """dict of strings: filename (k) to source text string (v).  v is ''
        if k has no text.

        Source text aims to preserve as much of the text written to a file
        as possible.  This is done through the use of pymarkdown extensions
        to maintain the additional markdown features that Obsidian uses."""
        return self._source_text_index

    @property
    def readable_text_index(self):
        """dict of strings: filename (k) to 'readable' string (v).  v is ''
        if k has no text.

        Readable text has all the main formatting removed.  This makes it
        easier to use the text for NLP analysis, with minimal processing
        needed, while still maintaining the meaning of text."""
        return self._readable_text_index

    def connect(self):
        """connect your notes together by representing the vault as a
        Networkx graph object, G.

        With your vault instantiated, set up the graph through:
            vault.connect()

        The graph G is written to the 'graph' attribute.
        """
        if not self._is_connected:
            # default graph to mirror Obsidian's link counts
            wiki_link_map = self._get_wikilinks_index()
            G = nx.MultiDiGraph(wiki_link_map)
            self._graph = G
            self._backlinks_index = self._get_backlinks_index(graph=G)
            self._wikilinks_index = wiki_link_map
            self._md_links_index = self._get_md_links_index()
            self._tags_index = self._get_tags_index()
            self._nonexistent_notes = self._get_nonexistent_notes()
            self._isolated_notes = self._get_isolated_notes(graph=G)
            self._embedded_files_index = self._get_embedded_files_index()
            self._math_index = self._get_math_index()
            self._front_matter_index = self._get_front_matter_index()

            self._is_connected = True

        return self  # fluent

    def gather(self, *, tags=None):
        """gather the content of your notes so that all the plaintext is
        stored in one place for easy access.

        The content of each note is stored in the source_text_index attribute.
        This enables text from the files to be accessible in one place.

        The stripped down content of the notes' text is stored in the
        readable_text_index attribute.  This enables text to be used more
        easily in NLP analysis.

        With your vault connected, gather your note content through:
            vault.gather()

        Args:
            tags (list, optional): Defaults to None, to keep all headers
                and paragraph formatting in the readable_text for notes.
                Otherwise specify a list of HTML tags to use to preserve
                their formatting in the final text.  For example, tags=[]
                will remove all header formatting (e.g. '#', '##' chars)
                and produces a one-line string.
        """
        if not self._is_connected:
            raise AttributeError('Connect vault before gathering notes.')

        # source text will not remove any content:
        self._source_text_index = {
            k: _get_source_text_from_md_file(self._dirpath / v,
                                             remove_code=False)
            for k, v in self._file_index.items()}
        self._readable_text_index = {
            k: _get_readable_text_from_md_file(self._dirpath / v,
                                               tags=tags)
            for k, v in self._file_index.items()}

        self._is_gathered = True

        return self  # fluent

    def get_backlinks(self, note_name):
        """Get backlinks for a note (given its name).

        If a note has not been created, but has wikilinks pointing to it
        elsewhere in the vault, then it will return those backlinks.

        If a note is not in the graph at all, then the function will raise
        an AttributeError.

        Args:
            note_name (str): the string that is the name in the graph.
                This is NOT a filepath!

        Returns:
            list
        """
        if not self._is_connected:
            raise AttributeError('Connect notes before calling the function')

        if note_name not in self._graph.nodes:
            raise ValueError('"{}" not found in graph.'.format(note_name))
        else:
            return self._backlinks_index[note_name]

    def get_backlink_counts(self, note_name):
        """Get counts of backlinks for a note (given its name).

        Args:
            note_name (str): the string that is the name in the graph.
                This is NOT a filepath!

        Returns:
            dict of integers >= 1
        """
        if not self._is_connected:
            raise AttributeError('Connect notes before calling the function')

        if note_name not in self._graph.nodes:
            raise ValueError('"{}" not found in graph.'.format(note_name))
        else:
            backlinks = self.get_backlinks(note_name)
            return dict(Counter(backlinks))

    def get_wikilinks(self, file_name):
        """Get wikilinks for a note (given its filename).

        Wikilinks can only appear in notes that already exist, so if a
        note is not in the file_index at all then the function will raise
        a ValueError.

        Args:
            file_name (str): the filename string that is in the file_index.
                This is NOT the filepath!

        Returns:
            list
        """
        if not self._is_connected:
            raise AttributeError('Connect notes before calling the function')

        if file_name not in self._file_index:
            raise ValueError('"{}" does not exist so it cannot have wikilinks.'.format(file_name))
        else:
            return self._wikilinks_index[file_name]

    def get_embedded_files(self, file_name):
        """Get embedded files for a note (given its filename).

        Embedded files can only appear in notes that already exist, so if a
        note is not in the file_index at all then the function will raise
        a ValueError.

        Args:
            file_name (str): the filename string that is in the file_index.
                This is NOT the filepath!

        Returns:
            list
        """
        if not self._is_connected:
            raise AttributeError('Connect notes before calling the function')

        if file_name not in self._file_index:
            raise ValueError('"{}" does not exist so it cannot have embedded files.'.format(file_name))
        else:
            return self._embedded_files_index[file_name]

    def get_md_links(self, file_name):
        """Get markdown links for a note (given its filename).

        Markdown links can only appear in notes that already exist, so if a
        note is not in the file_index at all then the function will raise
        a ValueError.

        Args:
            file_name (str): the filename string that is in the file_index.
                This is NOT the filepath!

        Returns:
            list
        """
        if not self._is_connected:
            raise AttributeError('Connect notes before calling the function')

        if file_name not in self._file_index:
            raise ValueError('"{}" does not exist so it cannot have md links.'.format(file_name))
        else:
            return self._md_links_index[file_name]

    def get_front_matter(self, file_name):
        """Get front matter for a note (given its filename).

        Front matter can only appear in notes that already exist, so if a
        note is not in the file_index at all then the function will raise
        a ValueError.

        Args:
            file_name (str): the filename string that is in the file_index.
                This is NOT the filepath!

        Returns:
            list
        """
        if not self._is_connected:
            raise AttributeError('Connect notes before calling the function')
        if file_name not in self._file_index:
            raise ValueError('"{}" does not exist so it cannot have front matter.'.format(file_name))
        else:
            return self._front_matter_index[file_name]

    def get_tags(self, file_name):
        """Get tags for a note (given its filename).
        Only top-level tags are supported (NOT nested tags).

        Tags can only appear in notes that already exist, so if a
        note is not in the file_index at all then the function will raise
        a ValueError.

        Args:
            file_name (str): the filename string that is in the file_index.
                This is NOT the filepath!

        Returns:
            list
        """
        if not self._is_connected:
            raise AttributeError('Connect notes before calling the function')
        if file_name not in self._file_index:
            raise ValueError('"{}" does not exist so it cannot have tags.'.format(file_name))
        else:
            return self._tags_index[file_name]

    def get_source_text(self, file_name):
        """Get text for a note (given its filename).  This requires the vault
        functions 'connect' AND 'gather' to have been called.

        Text can only appear in notes that already exist, so if a
        note is not in the file_index at all then the function will raise
        a ValueError.

        Args:
            file_name (str): the filename string that is in the file_index.
                This is NOT the filepath!

        Returns:
            str
        """
        if not self._is_gathered:
            raise AttributeError('Gather notes before calling the function')
        if file_name not in self._file_index:
            raise ValueError('"{}" does not exist so it cannot have text.'.format(file_name))
        else:
            return self._source_text_index[file_name]

    def get_readable_text(self, file_name):
        """Get readable text for a note (given its filename).
        This requires the vault functions 'connect' AND 'gather' to have
        been called.

        Change the arguments of the 'gather' function to specify how the text
        output should be stored, e.g. whether all HTML tags should be removed
        before the final output.

        Text can only appear in notes that already exist, so if a
        note is not in the file_index at all then the function will raise
        a ValueError.

        Args:
            file_name (str): the filename string that is in the file_index.
                This is NOT the filepath!

        Returns:
            str
        """
        if not self._is_gathered:
            raise AttributeError('Gather notes before calling the function')
        if file_name not in self._file_index:
            raise ValueError('"{}" does not exist so it cannot have text.'.format(file_name))
        else:
            return self._readable_text_index[file_name]

    def _get_md_relpaths(self, **kwargs):
        """Return list of filepaths *relative* to the directory instantiated
        for the class.

        Returns:
            list
        """
        return get_md_relpaths_matching_subdirs(self._dirpath, **kwargs)

    def _get_md_relpaths_by_name(self, **kwargs):
        """Return k,v pairs
        where k is the file name
        and v is the relpath of the md file

        Returns:
            dict
        """
        return {f.stem: f for f in self._get_md_relpaths(**kwargs)}

    def _get_wikilinks_index(self):
        """Return k,v pairs
        where k is the md filename
        and v is list of ALL wikilinks found in k"""
        return {k: get_wikilinks(self._dirpath / v)
                for k, v in self._file_index.items()}

    def _get_embedded_files_index(self):
        """Return k,v pairs
        where k is the md filename
        and v is list of ALL embedded files found in k"""
        return {k: get_embedded_files(self._dirpath / v)
                for k, v in self._file_index.items()}

    def _get_math_index(self):
        """Return k,v pairs
        where k is the md filename
        and v is list of ALL LaTeX math strings found in k"""
        return {k: _get_all_latex_from_md_file(self._dirpath / v)
                for k, v in self._file_index.items()}

    def _get_unique_wikilinks_index(self):
        """Return k,v pairs
        where k is the md filename
        and v is list of UNIQUE wikilinks found in k"""
        return {k: get_unique_wikilinks(self._dirpath / v)
                for k, v in self._file_index.items()}

    def _get_md_links_index(self):
        """Return k,v pairs
        where k is the md note name
        and v is list of ALL markdown links found in k"""
        return {k: get_md_links(self._dirpath / v)
                for k, v in self._file_index.items()}

    def _get_unique_md_links_index(self):
        """Return k,v pairs
        where k is the md note name
        and v is list of UNIQUE markdown links found in k"""
        return {k: get_unique_md_links(self._dirpath / v)
                for k, v in self._file_index.items()}

    def _get_backlinks_index(self, *, graph):
        """Return k,v pairs
        where k is the md note name
        and v is list of ALL backlinks found in k"""
        return {n: [n[0] for n in list(graph.in_edges(n))]
                for n in self._graph.nodes}

    def _get_front_matter_index(self):
        """Return k,v pairs
        where k is the md filename
        and v is list of file matter metadata found in k"""
        return {k: get_front_matter(self._dirpath / v)
                for k, v in self._file_index.items()}

    def _get_tags_index(self):
        """Return k,v pairs
        where k is the md filename
        and v is list of tags found in k"""
        return {k: get_tags(self._dirpath / v)
                for k, v in self._file_index.items()}

    def get_note_metadata(self):
        """Structured dataset of metadata on the vault's notes.  This
        includes filepaths and counts of different link types.

        The df is indexed by 'note' (i.e. nodes in the graph).

        Notes that haven't been created will only have info on the number
        of backlinks - other columns will have NaN.

        Returns:
            pd.DataFrame
        """

        if not self._is_connected:
            raise AttributeError('Connect notes before calling the function')

        df = (pd.DataFrame(index=list(self._backlinks_index.keys()))
              .rename_axis('note')
              .pipe(self._create_note_metadata_columns)
              .pipe(self._clean_up_note_metadata_dtypes)
              )
        return df

    def _create_note_metadata_columns(self, df):
        """pipe func for mutating df"""
        df['rel_filepath'] = [self._file_index.get(f, np.NaN)
                              for f in df.index]
        df['abs_filepath'] = np.where(df['rel_filepath'].notna(),
                                      [self._dirpath / Path(str(f))
                                       for f in df['rel_filepath']],
                                      np.NaN)
        df['note_exists'] = np.where(df['rel_filepath'].notna(),
                                     True, False)
        df['n_backlinks'] = [len(self.get_backlinks(f)) for f in df.index]
        df['n_wikilinks'] = np.where(df['note_exists'],
                                     [len(self._wikilinks_index.get(f, []))
                                     for f in df.index],
                                     np.NaN)
        df['n_embedded_files'] = np.where(df['note_exists'],
                                          [len(self._embedded_files_index.get(
                                              f, []))
                                           for f in df.index],
                                          np.NaN)
        df['modified_time'] = pd.to_datetime(
            [os.path.getmtime(f) if not pd.isna(f) else np.NaN
             for f in df['abs_filepath']],
            unit='s'
        )
        return df

    def _clean_up_note_metadata_dtypes(self, df):
        """pipe func for mutating df"""
        df['rel_filepath'] = np.where(df['rel_filepath'].notna(),
                                      [Path(str(f))
                                       for f in df['rel_filepath']],
                                      np.NaN)
        df['n_wikilinks'] = df['n_wikilinks'].astype(float)  # for consistency
        return df

    def _get_nonexistent_notes(self):
        """Get notes that have backlinks but don't have md files.

        The comparison is done with sets but the result is returned
        as a list."""
        return list(set(self.backlinks_index.keys())
                    .difference(set(self.file_index)))

    def _get_isolated_notes(self, *, graph):
        """Get notes that are not connected to any other notes in the vault,
        i.e. they have 0 wikilinks and 0 backlinks.

        These notes are retrieved from the graph."""
        return list(nx.isolates(graph))
