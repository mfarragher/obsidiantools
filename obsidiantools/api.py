import os
import networkx as nx
import numpy as np
import pandas as pd
from collections import Counter
from pathlib import Path

# init
from .md_utils import (get_md_relpaths_matching_subdirs)
from .canvas_utils import (get_canvas_relpaths_matching_subdirs)
# connect
from .md_utils import (_get_md_front_matter_and_content,
                       _get_html_from_md_content,
                       _get_md_links_from_source_text,
                       _get_unique_md_links_from_source_text,
                       _get_unique_wikilinks_from_source_text,
                       _get_all_wikilinks_from_source_text,
                       _get_all_embedded_files_from_source_text,
                       get_tags,
                       get_source_text_from_html,
                       _get_all_latex_from_html_content)
# gather
from .md_utils import (get_source_text_from_md_file,
                       get_readable_text_from_md_file)
# canvas:
from .canvas_utils import (get_canvas_content,
                           get_canvas_graph_detail)


class Vault:
    def __init__(self, dirpath: Path, *,
                 include_subdirs: list[str] = None, include_root: bool = True):
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
        Detail on canvas files is also stored when calling this method.

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
            get_wikilink_counts
            get_embedded_files
            get_math
            get_front_matter
            get_md_links
            get_tags
            get_source_text
            get_readable_text

        Methods for analysis across multiple notes:
            get_note_metadata

        Attributes - general:
            dirpath (arg)
            is_connected
            is_gathered
        Attributes - md-related:
            file_index
            graph
            backlinks_index
            wikilinks_index
            unique_wikilinks_index
            embedded_files_index
            math_index
            md_links_index
            unique_md_links_index
            tags_index
            nonexistent_notes
            isolated_notes
            source_text_index
            readable_text_index
        Attributes - canvas-related:
            canvas_file_index
            canvas_content_index
            canvas_graph_detail_index
        """
        self._dirpath = dirpath
        self._file_index = self._get_md_relpaths_by_name(
            include_subdirs=include_subdirs,
            include_root=include_root)
        self._canvas_file_index = self._get_canvas_relpaths_by_name(
            include_subdirs=include_subdirs,
            include_root=include_root)

        self._is_connected = False
        self._is_gathered = False

        # via md content:
        self._graph = None
        self._backlinks_index = {}
        self._wikilinks_index = {}
        self._unique_wikilinks_index = {}
        self._embedded_files_index = {}
        self._math_index = {}
        self._md_links_index = {}
        self._unique_md_links_index = {}
        self._tags_index = {}
        self._nonexistent_notes = []
        self._isolated_notes = []
        self._front_matter_index = {}
        self._source_text_index = {}
        self._readable_text_index = {}

        # via canvas content:
        self._canvas_content_index = {}
        self._canvas_graph_detail_index = {}

    @property
    def dirpath(self) -> Path:
        """pathlib Path"""
        return self._dirpath

    @property
    def file_index(self) -> dict[str, Path]:
        """dict: one-to-one mapping of md filename (k) to relative path (v)"""
        return self._file_index

    @file_index.setter
    def file_index(self, value) -> dict[str, Path]:
        self._file_index = value

    @property
    def canvas_file_index(self) -> dict[str, Path]:
        """dict: one-to-one mapping of canvas filename (k) to relative path
        (v)"""
        return self._canvas_file_index

    @canvas_file_index.setter
    def canvas_file_index(self, value) -> dict[str, Path]:
        self._canvas_file_index = value

    @property
    def graph(self) -> nx.MultiDiGraph:
        """networkx Graph"""
        return self._graph

    @property
    def backlinks_index(self) -> dict[str, list[str]]:
        """dict of lists: note name (k) to lists (v).  v is [] if k
        has no backlinks."""
        return self._backlinks_index

    @property
    def wikilinks_index(self) -> dict[str, list[str]]:
        """dict of lists: filename (k) to lists (v).  v is [] if k
        has no wikilinks."""
        return self._wikilinks_index

    @property
    def unique_wikilinks_index(self) -> dict[str, list[str]]:
        """dict of lists: filename (k) to lists (v).  v is [] if k
        has no wikilinks."""
        return self._unique_wikilinks_index

    @property
    def embedded_files_index(self) -> dict[str, list[str]]:
        """dict: note name (k) to list of embedded file string (v).
        v is [] if k has no embedded files."""
        return self._embedded_files_index

    @property
    def math_index(self) -> dict[str, list[str]]:
        """dict: note name (k) to list of LaTeX math string (v).  v is [] if
        k has no LaTeX."""
        return self._math_index

    @property
    def md_links_index(self) -> dict[str, list[str]]:
        """dict of lists: filename (k) to lists (v).  v is [] if k
        has no markdown links."""
        return self._md_links_index

    @property
    def unique_md_links_index(self) -> dict[str, list[str]]:
        """dict of lists: filename (k) to lists (v).  v is [] if k
        has no markdown links."""
        return self._unique_md_links_index

    @property
    def tags_index(self) -> dict[str, list[str]]:
        """dict of lists: filename (k) to lists (v).  v is [] if k
        has no tags."""
        return self._tags_index

    @property
    def nonexistent_notes(self) -> list[str]:
        """list: notes without files, i.e. the notes have backlink(s) but
        their md files don't exist yet.

        They are ideas floating around in the Obsidian graph... waiting to
        be created as actual notes one day :-)"""
        return self._nonexistent_notes

    @property
    def isolated_notes(self) -> list[str]:
        """list: notes (with their own md files) that lack backlinks and
        lack wikilinks.  They are not connected to other notes in the
        Obsidian graph at all."""
        return self._isolated_notes

    @property
    def front_matter_index(self) -> dict[str, list[str]]:
        """dict: note name (k) to front matter (v).  v is {} if no front
        matter was extracted from note."""
        return self._front_matter_index

    @property
    def is_connected(self) -> bool:
        """Bool: has the connect function been called to set up graph?"""
        return self._is_connected

    @property
    def is_gathered(self) -> bool:
        """Bool: has the gather function been called to gather text?"""
        return self._is_gathered

    @property
    def source_text_index(self) -> dict[str, str]:
        """dict of strings: filename (k) to source text string (v).  v is ''
        if k has no text.

        Source text aims to preserve as much of the text written to a file
        as possible.  This is done through the use of pymarkdown extensions
        to maintain the additional markdown features that Obsidian uses."""
        return self._source_text_index

    @source_text_index.setter
    def source_text_index(self, value) -> dict[str, str]:
        self._source_text_index = value

    @property
    def readable_text_index(self) -> dict[str, str]:
        """dict of strings: filename (k) to 'readable' string (v).  v is ''
        if k has no text.

        Readable text has all the main formatting removed.  This makes it
        easier to use the text for NLP analysis, with minimal processing
        needed, while still maintaining the meaning of text."""
        return self._readable_text_index

    @readable_text_index.setter
    def readable_text_index(self, value) -> dict[str, str]:
        self._readable_text_index = value

    @property
    def canvas_content_index(self) -> dict[str, str]:
        """dict of dict: 'shortest path when possible' filepath with canvas
        ext (k), to canvas content dict (v).  v is {} if k has no content."""
        return self._canvas_content_index

    @canvas_content_index.setter
    def canvas_content_index(self, value) -> dict[str, str]:
        self._canvas_content_index = value

    @property
    def canvas_graph_detail_index(self) -> \
        dict[str, tuple[nx.MultiDiGraph,
                        dict[str, tuple[int, int]],
                        dict[tuple[str, str], str]]
             ]:
        """dict of tuple: 'shortest path when possible' filepath with canvas
        ext (k), to canvas graph detail tuple (v)."""
        return self._canvas_graph_detail_index

    @canvas_graph_detail_index.setter
    def canvas_graph_detail_index(self, value) -> \
        dict[str, tuple[nx.MultiDiGraph,
                        dict[str, tuple[int, int]],
                        dict[tuple[str, str], str]]
             ]:
        self._canvas_graph_detail_index = value

    def connect(self, *, show_nested_tags: bool = False):
        """connect your notes together by representing the vault as a
        Networkx graph object, G.

        With your vault instantiated, set up the graph through:
            vault.connect()

        The graph G is written to the 'graph' attribute, to represent the
        Obsidian graph of your notes.

        Args:
            show_nested_tags (Boolean): show nested tags in the output.
                Defaults to False (which would mean only the highest level
                of any nested tags are included in the output).
        """
        # md content:
        if not self._is_connected:
            # index dicts, where k is a note name in the vault:
            md_links_ix = {}
            md_links_unique_ix = {}
            embedded_files_ix = {}
            tags_ix = {}
            math_ix = {}
            front_matter_ix = {}
            wikilinks_ix = {}
            wikilinks_unique_ix = {}

            # loop through md files:
            for f, relpath in self._file_index.items():
                # MAIN file read:
                front_matter, content = _get_md_front_matter_and_content(
                    self._dirpath / relpath)
                html = _get_html_from_md_content(content)
                src_txt = get_source_text_from_html(
                    html, remove_code=True)

                # info from core text:
                md_links_ix[f] = _get_md_links_from_source_text(src_txt)
                md_links_unique_ix[f] = _get_unique_md_links_from_source_text(src_txt)
                embedded_files_ix[f] = _get_all_embedded_files_from_source_text(
                    src_txt, remove_aliases=True)
                wikilinks_ix[f] = _get_all_wikilinks_from_source_text(
                    src_txt, remove_aliases=True)
                wikilinks_unique_ix[f] = _get_unique_wikilinks_from_source_text(
                    src_txt, remove_aliases=True)
                # info from html:
                math_ix[f] = _get_all_latex_from_html_content(html)
                # split out front matter:
                front_matter_ix[f] = front_matter

                # MORE file reads needed for extra info:
                tags_ix[f] = get_tags(self._dirpath / relpath,
                                      show_nested=show_nested_tags)

            self._md_links_index = md_links_ix
            self._unique_md_links_index = md_links_unique_ix
            self._embedded_files_index = embedded_files_ix
            self._tags_index = tags_ix
            self._math_index = math_ix
            self._front_matter_index = front_matter_ix
            # to be used for graph:
            self._wikilinks_index = wikilinks_ix
            self._unique_wikilinks_index = wikilinks_unique_ix

            # graph:
            G = nx.MultiDiGraph(wikilinks_ix)
            self._graph = G
            # info obtained from graph:
            self._backlinks_index = self._get_backlinks_index(graph=G)
            self._nonexistent_notes = self._get_nonexistent_notes()
            self._isolated_notes = self._get_isolated_notes(graph=G)

            self._is_connected = True

        # canvas content:
        # loop through canvas files:
        canvas_content_ix = {}
        canvas_graph_detail_ix = {}
        for f, relpath in self._canvas_file_index.items():
            content_c = get_canvas_content(
                self._dirpath / relpath)
            canvas_content_ix[f] = content_c
            G_c, pos_c, edge_labels_c = get_canvas_graph_detail(
                content_c)
            canvas_graph_detail_ix[f] = G_c, pos_c, edge_labels_c
        self._canvas_content_index = canvas_content_ix
        self._canvas_graph_detail_index = canvas_graph_detail_ix

        return self  # fluent

    def gather(self, *, tags: list[str] = None):
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
        # source text will not remove any content:
        self._source_text_index = {
            k: get_source_text_from_md_file(self._dirpath / v,
                                            remove_code=True,
                                            remove_math=True)
            for k, v in self._file_index.items()}
        self._readable_text_index = {
            k: get_readable_text_from_md_file(self._dirpath / v,
                                              tags=tags)
            for k, v in self._file_index.items()}

        self._is_gathered = True

        return self  # fluent

    def get_backlinks(self, note_name: str) -> list[str]:
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

    def get_backlink_counts(self, note_name: str) -> dict[str, int]:
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

    def get_wikilinks(self, file_name: str) -> list[str]:
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

    def get_wikilink_counts(self, note_name: str) -> dict[str, int]:
        """Get counts of wikilinks for a note (given its name).

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
            wikilinks = self.get_wikilinks(note_name)
            return dict(Counter(wikilinks))

    def get_embedded_files(self, file_name: str) -> list[str]:
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

    def get_md_links(self, file_name: str) -> list[str]:
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

    def get_front_matter(self, file_name: str) -> list[dict]:
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

    def get_tags(self, file_name: str, *,
                 show_nested: bool = False) -> list[str]:
        """Get tags for a note (given its filename).
        By default, only the highest level of any nested tags is shown
        in the output.

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

    def get_source_text(self, file_name: str) -> str:
        """Get text for a note (given its filename).  This requires the vault
        function 'gather' to have been called.

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

    def get_readable_text(self, file_name: str) -> str:
        """Get readable text for a note (given its filename).
        This requires the vault function 'gather' to have been called.

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

    def _get_md_relpaths(self, **kwargs) -> list[Path]:
        """Return list of md filepaths *relative* to the directory instantiated
        for the class.

        Returns:
            list
        """
        return get_md_relpaths_matching_subdirs(self._dirpath, **kwargs)

    def _get_canvas_relpaths(self, **kwargs) -> list[Path]:
        """Return list of canvas filepaths *relative* to the directory instantiated
        for the class.

        Returns:
            list
        """
        return get_canvas_relpaths_matching_subdirs(self._dirpath,
                                                    **kwargs)

    def __get_relpaths_by_name(self, *, extension, **kwargs) -> dict[str, Path]:
        """Return k,v pairs
        where k is the file name
        and v is the relpath of the {extension} file

        Returns:
            dict
        """
        # get note names (for k) and relpaths (for v):
        # keep or remove ext, based on how the file refs appear in wikilinks:
        if extension == 'md':
            relpaths_list = self._get_md_relpaths(
                **kwargs)
            # remove .md ext:
            all_file_names_list = [f.stem for f in relpaths_list]
        if extension == 'canvas':
            relpaths_list = self._get_canvas_relpaths(
                **kwargs)
            # keep .canvas ext:
            all_file_names_list = [f.name for f in relpaths_list]

        # get indices of dupe note names:
        _, inverse_ix, counts = np.unique(
            np.array(all_file_names_list),
            return_inverse=True,
            return_counts=True,
            axis=0)
        dupe_names_ix = np.where(counts[inverse_ix] > 1)[0]

        # get shortest paths via mask:
        shortest_paths_arr = np.array(all_file_names_list, dtype=object)
        if extension == 'md':
            shortest_paths_arr[dupe_names_ix] = np.array(
                [str(fpath.with_suffix(''))
                 for fpath in relpaths_list])[dupe_names_ix]
        if extension == 'canvas':
            shortest_paths_arr[dupe_names_ix] = np.array(
                [str(fpath)
                 for fpath in relpaths_list])[dupe_names_ix]
        return {n: p for n, p in zip(shortest_paths_arr, relpaths_list)}

    def _get_md_relpaths_by_name(self, **kwargs) -> dict[str, Path]:
        return self.__get_relpaths_by_name(extension='md',
                                           **kwargs)

    def _get_canvas_relpaths_by_name(self, **kwargs) -> dict[str, Path]:
        return self.__get_relpaths_by_name(extension='canvas',
                                           **kwargs)

    def _get_backlinks_index(self, *,
                             graph: nx.MultiDiGraph) -> dict[str, list[str]]:
        """Return k,v pairs
        where k is the md note name
        and v is list of ALL backlinks found in k"""
        return {n: [n[0] for n in list(graph.in_edges(n))]
                for n in self._graph.nodes}

    def get_note_metadata(self) -> pd.DataFrame:
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

    def _create_note_metadata_columns(self,
                                      df: pd.DataFrame) -> pd.DataFrame:
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
        df['n_tags'] = np.where(df['note_exists'],
                                [len(self._tags_index.get(f, []))
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

    def _clean_up_note_metadata_dtypes(self,
                                       df: pd.DataFrame) -> pd.DataFrame:
        """pipe func for mutating df"""
        df['rel_filepath'] = np.where(df['rel_filepath'].notna(),
                                      [Path(str(f))
                                       for f in df['rel_filepath']],
                                      np.NaN)
        df['n_wikilinks'] = df['n_wikilinks'].astype(float)  # for consistency
        return df

    def _get_nonexistent_notes(self) -> list[str]:
        """Get notes that have backlinks but don't have md files.

        The comparison is done with sets but the result is returned
        as a list."""
        return list(set(self.backlinks_index.keys())
                    .difference(set(self.file_index)))

    def _get_isolated_notes(self, *,
                            graph: nx.MultiDiGraph) -> list[str]:
        """Get notes that are not connected to any other notes in the vault,
        i.e. they have 0 wikilinks and 0 backlinks.

        These notes are retrieved from the graph."""
        return list(nx.isolates(graph))
