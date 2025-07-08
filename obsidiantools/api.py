import warnings
import networkx as nx
import numpy as np
import pandas as pd
from collections import Counter
from pathlib import Path
from itertools import chain

# init
from .md_utils import (get_md_relpaths_matching_subdirs)
from .canvas_utils import (get_canvas_relpaths_matching_subdirs,
                           _get_all_valid_canvas_file_relpaths)
# connect
from .md_utils import (_get_md_front_matter_and_content,
                       _get_html_from_md_content,
                       _get_md_links_from_source_text,
                       _get_unique_md_links_from_source_text,
                       _get_unique_wikilinks_from_source_text,
                       _get_all_wikilinks_from_source_text,
                       _get_all_embedded_files_from_source_text,
                       get_tags,
                       _get_all_latex_from_html_content)
from ._constants import METADATA_DF_COLS_GENERIC_TYPE
from ._io import _get_shortest_path_by_filename
from .media_utils import _get_all_valid_media_file_relpaths
# gather:
from .md_utils import (get_source_text_from_html,
                       _get_readable_text_from_html)
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

        -- ARGS --
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

        -- METHODS --
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
        Methods for analysis across multiple media & canvas files:
            get_media_file_metadata
            get_canvas_file_metadata
        Method for all file types:
            get_all_file_metadata

        -- ATTRIBUTES --
        - The main file lookups have (*) next to them -
        Attributes - general:
            dirpath (arg)
            attachments (kwarg)
            is_connected
            is_gathered
        Attributes - md-related:
            md_file_index (*)
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
        Attributes - media files:
            media_file_index (*)
            nonexistent_media_files
            isolated_media_files
        Attributes - canvas-related:
            canvas_file_index (*)
            nonexistent_canvas_files
            isolated_canvas_files
            canvas_content_index
            canvas_graph_detail_index
        """
        if not isinstance(dirpath, Path):
            raise TypeError("Specify a pathlib.Path for the dirpath argument (not other types like strings)")

        # args:
        self._dirpath = dirpath
        self._attachments = None  # connect()

        self._md_file_index = self._get_md_relpaths_by_name(
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

        # via media files:
        self._media_file_index = {}
        self._nonexistent_media_files = []
        self._isolated_media_files = []

        # via canvas content:
        self._canvas_content_index = {}
        self._canvas_graph_detail_index = {}
        self._nonexistent_canvas_files = []
        self._isolated_canvas_files = []

    @property
    def dirpath(self) -> Path:
        """pathlib Path"""
        return self._dirpath

    @property
    def attachments(self) -> bool:
        """bool: argument for connect method.  True to include 'attachment'
        files.
        """
        return self._attachments

    @attachments.setter
    def attachments(self, value) -> bool:
        self._attachments = value

    @property
    def md_file_index(self) -> dict[str, Path]:
        """dict: one-to-one mapping of md filename (k) to relative path (v)"""
        return self._md_file_index

    @md_file_index.setter
    def md_file_index(self, value) -> dict[str, Path]:
        self._md_file_index = value

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

    @graph.setter
    def graph(self, value) -> nx.MultiDiGraph:
        self._graph = value

    @property
    def backlinks_index(self) -> dict[str, list[str]]:
        """dict of lists: note name (k) to lists (v).  v is [] if k
        has no backlinks."""
        return self._backlinks_index

    @backlinks_index.setter
    def backlinks_index(self, value) -> dict[str, list[str]]:
        self._backlinks_index = value

    @property
    def wikilinks_index(self) -> dict[str, list[str]]:
        """dict of lists: filename (k) to lists (v).  v is [] if k
        has no wikilinks."""
        return self._wikilinks_index

    @wikilinks_index.setter
    def wikilinks_index(self, value) -> dict[str, list[str]]:
        self._wikilinks_index = value

    @property
    def unique_wikilinks_index(self) -> dict[str, list[str]]:
        """dict of lists: filename (k) to lists (v).  v is [] if k
        has no wikilinks."""
        return self._unique_wikilinks_index

    @unique_wikilinks_index.setter
    def unique_wikilinks_index(self, value) -> dict[str, list[str]]:
        self._unique_wikilinks_index = value

    @property
    def embedded_files_index(self) -> dict[str, list[str]]:
        """dict: note name (k) to list of embedded file string (v).
        v is [] if k has no embedded files."""
        return self._embedded_files_index

    @embedded_files_index.setter
    def embedded_files_index(self, value) -> dict[str, list[str]]:
        self._embedded_files_index = value

    @property
    def math_index(self) -> dict[str, list[str]]:
        """dict: note name (k) to list of LaTeX math string (v).  v is [] if
        k has no LaTeX."""
        return self._math_index

    @math_index.setter
    def math_index(self, value) -> dict[str, list[str]]:
        self._math_index = value

    @property
    def md_links_index(self) -> dict[str, list[str]]:
        """dict of lists: filename (k) to lists (v).  v is [] if k
        has no markdown links."""
        return self._md_links_index

    @md_links_index.setter
    def md_links_index(self, value) -> dict[str, list[str]]:
        self._md_links_index = value

    @property
    def unique_md_links_index(self) -> dict[str, list[str]]:
        """dict of lists: filename (k) to lists (v).  v is [] if k
        has no markdown links."""
        return self._unique_md_links_index

    @unique_md_links_index.setter
    def unique_md_links_index(self, value) -> dict[str, list[str]]:
        self._unique_md_links_index = value

    @property
    def tags_index(self) -> dict[str, list[str]]:
        """dict of lists: filename (k) to lists (v).  v is [] if k
        has no tags."""
        return self._tags_index

    @tags_index.setter
    def tags_index(self, value) -> dict[str, list[str]]:
        self._tags_index = value

    @property
    def nonexistent_notes(self) -> list[str]:
        """list: notes without files, i.e. the notes have backlink(s) but
        their md files don't exist yet.

        They are ideas floating around in the Obsidian graph... waiting to
        be created as actual notes one day :-)"""
        return self._nonexistent_notes

    @nonexistent_notes.setter
    def nonexistent_notes(self, value) -> list[str]:
        self._nonexistent_notes = value

    @property
    def isolated_notes(self) -> list[str]:
        """list: notes (with their own md files) that lack backlinks and
        lack wikilinks.  They are not connected to other notes in the
        Obsidian graph at all."""
        return self._isolated_notes

    @isolated_notes.setter
    def isolated_notes(self, value) -> list[str]:
        self._isolated_notes = value

    @property
    def front_matter_index(self) -> dict[str, list[str]]:
        """dict: note name (k) to front matter (v).  v is {} if no front
        matter was extracted from note."""
        return self._front_matter_index

    @front_matter_index.setter
    def front_matter_index(self, value) -> dict[str, list[str]]:
        self._front_matter_index = value

    @property
    def media_file_index(self) -> dict[str, Path]:
        """dict: media file (k) to relative path (v).

        These will appear in the index:
        1. Embedded files that exist.
        2. Embedded files that don't exist.
        3. Files that exist in the vault but haven't been embedded.
        """
        return self._media_file_index

    @media_file_index.setter
    def media_file_index(self, value) -> dict[str, Path]:
        self._media_file_index = value

    @property
    def nonexistent_media_files(self) -> list[str]:
        """list: media files that don't exist on the file system yet."""
        return self._nonexistent_media_files

    @nonexistent_media_files.setter
    def nonexistent_media_files(self, value) -> list[str]:
        self._nonexistent_media_files = value

    @property
    def isolated_media_files(self) -> list[str]:
        """list: media files that lack backlinks from md files.
        They are not connected to other notes in the Obsidian graph at all."""
        return self._isolated_media_files

    @isolated_media_files.setter
    def isolated_media_files(self, value) -> list[str]:
        self._isolated_media_files = value

    @property
    def nonexistent_canvas_files(self) -> list[str]:
        """list: canvas files that don't exist on the file system yet."""
        return self._nonexistent_canvas_files

    @nonexistent_canvas_files.setter
    def nonexistent_canvas_files(self, value) -> list[str]:
        self._nonexistent_canvas_files = value

    @property
    def isolated_canvas_files(self) -> list[str]:
        """list: canvas files that lack backlinks from md files.
        They are not connected to other notes in the Obsidian graph at all."""
        return self._isolated_canvas_files

    @isolated_canvas_files.setter
    def isolated_canvas_files(self, value) -> list[str]:
        self._isolated_canvas_files = value

    @property
    def is_connected(self) -> bool:
        """Bool: has the connect function been called to set up graph?"""
        return self._is_connected

    @is_connected.setter
    def is_connected(self, value) -> bool:
        self._is_connected = value

    @property
    def is_gathered(self) -> bool:
        """Bool: has the gather function been called to gather text?"""
        return self._is_gathered

    @is_gathered.setter
    def is_gathered(self, value) -> bool:
        self._is_gathered = value

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

    def connect(self, *, show_nested_tags: bool = False,
                attachments=False):
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
            attachments (Boolean): Defaults to False.  'Attachments' refers
                to the graph toggle option in the Obsidian app.  By default,
                obsidiantools will only include md files (notes) in the
                graph (i.e. like Attachments is toggled off in Obsidian app).
                To include media files in the graph, set this option to True.
                This will lead to the inclusion of media files' in the
                backlinks_index.
        """
        if not self._is_connected:
            self._attachments = attachments

            # md content:
            # index dicts, where k is a note name in the vault:
            self._md_links_index = {}
            self._unique_md_links_index = {}
            self._embedded_files_index = {}
            self._tags_index = {}
            self._math_index = {}
            self._front_matter_index = {}
            # to be used for graph:
            self._wikilinks_index = {}
            self._unique_wikilinks_index = {}

            # loop through md files:
            for f, relpath in self._md_file_index.items():
                self._connect_update_based_on_new_relpath(
                    relpath, note=f,
                    show_nested_tags=show_nested_tags)

            # canvas content:
            # loop through canvas files:
            self._canvas_content_index = {}
            self._canvas_graph_detail_index = {}
            for f, relpath in self._canvas_file_index.items():
                content_c = get_canvas_content(
                    self._dirpath / relpath)
                self._canvas_content_index[f] = content_c
                G_c, pos_c, edge_labels_c = get_canvas_graph_detail(
                    content_c)
                self._canvas_graph_detail_index[f] = G_c, pos_c, edge_labels_c

            # set these up before graph is created:
            self._set_canvas_file_attrs()
            self._set_media_file_attrs()

            # graph setup:
            graph_data_dict = self.__get_graph_data_dict(
                attachments=attachments)
            G = nx.MultiDiGraph(graph_data_dict)
            self._graph = G
            self._set_graph_related_attributes()

            # set these again so that they are finally correct
            # (to remove notes / md files from the 'nonexistent_*' attrs,
            # the nonexistent_notes are required from the graph)
            self._set_canvas_file_attrs()
            self._set_media_file_attrs()

            self._is_connected = True

        return self  # fluent

    def _connect_update_based_on_new_relpath(self, relpath: Path, *,
                                             note: str,
                                             show_nested_tags: bool):
        """Individual file read & associated attrs update for the
        connect method."""
        exclude_canvas = not self._attachments

        # MAIN file read:
        front_matter, content = _get_md_front_matter_and_content(
            self._dirpath / relpath)
        html = _get_html_from_md_content(content)
        src_txt = get_source_text_from_html(
            html, remove_code=True)

        # info from core text:
        self._md_links_index[note] = (
            _get_md_links_from_source_text(src_txt))
        self._unique_md_links_index[note] = (
            _get_unique_md_links_from_source_text(src_txt))
        self._embedded_files_index[note] = (
            _get_all_embedded_files_from_source_text(
                src_txt, remove_aliases=True)
            # (aliases are redundant for connect method)
            )
        self._wikilinks_index[note] = (
            _get_all_wikilinks_from_source_text(
                src_txt, remove_aliases=True,
                exclude_canvas=exclude_canvas))
        self._unique_wikilinks_index[note] = (
            _get_unique_wikilinks_from_source_text(
                src_txt, remove_aliases=True,
                exclude_canvas=exclude_canvas))
        # info from html:
        self._math_index[note] = (_get_all_latex_from_html_content(
            html))
        # split out front matter:
        self._front_matter_index[note] = front_matter

        # MORE file reads needed for extra info:
        self._tags_index[note] = get_tags(
            self._dirpath / relpath,
            show_nested=show_nested_tags)

    def _set_media_file_attrs(self):
        (embedded_files_by_short_path,
         non_embedded_files_by_short_path,
         nonexistent_files_by_short_path) = (
            self._get_media_file_dicts_tuple())

        # only set media file index once:
        if not self._media_file_index:
            files_ix = {**embedded_files_by_short_path,
                        **non_embedded_files_by_short_path}
            self._media_file_index = files_ix
        # these attrs can be set again, once graph is created:
        self._nonexistent_media_files = list(
            nonexistent_files_by_short_path.keys())
        self._isolated_media_files = list(
            non_embedded_files_by_short_path.keys())

    def _set_canvas_file_attrs(self):
        (linked_files_by_short_path,
         non_linked_files_by_short_path,
         nonexistent_files_by_short_path) = (
            self._get_canvas_file_dicts_tuple())

        self._nonexistent_canvas_files = list(
            nonexistent_files_by_short_path.keys())
        self._isolated_canvas_files = list(
            non_linked_files_by_short_path.keys())

    def _get_media_file_dicts_tuple(self) \
            -> tuple[dict[str, Path], dict[str, Path], dict[str, Path]]:
        """Return (existent files embedded,
        existent files not embedded,
        nonexistent files embedded).

        The reason this logic is complex is that media files are embedded in
        md files in the Obsidian app using the shortest possible filepath,
        but they all need to be cross-checked against actual media filepaths.
        """

        # detail on all embedded files AND ones that exist:
        all_files_embedded_in_notes = list(
            chain.from_iterable(self._embedded_files_index.values()))
        media_file_relpaths_existent = _get_all_valid_media_file_relpaths(
            self._dirpath)
        return self.__get_file_dicts_tuple(
            all_files_embedded_in_notes,
            links_index=self._embedded_files_index,
            existing_file_relpaths=media_file_relpaths_existent,
            file_type='media')

    def _get_canvas_file_dicts_tuple(self) \
            -> tuple[dict[str, Path], dict[str, Path], dict[str, Path]]:
        """Return (existent files linked,
        existent files not linked,
        nonexistent files linked).

        The reason this logic is complex is that media files are embedded in
        md files in the Obsidian app using the shortest possible filepath,
        but they all need to be cross-checked against actual media filepaths.
        """

        # detail on all linked files AND ones that exist:
        all_files_linked_in_notes = list(
            chain.from_iterable(self._wikilinks_index.values()))
        canvas_file_relpaths_existent = _get_all_valid_canvas_file_relpaths(
            self._dirpath)
        return self.__get_file_dicts_tuple(
            all_files_linked_in_notes,
            links_index=self._wikilinks_index,
            existing_file_relpaths=canvas_file_relpaths_existent,
            file_type='canvas')

    def __get_file_dicts_tuple(self, linked_files_list: list[str], *,
                               links_index: dict[list[str]],
                               existing_file_relpaths: list[Path],
                               file_type: str):
        # get shortest path for each 'linked' file of chosen type;
        # check whether each exists
        shortest_names_existent = _get_shortest_path_by_filename(
            existing_file_relpaths)
        # for nonexistent files, don't want to catch other types:
        short_names_not_wanted_set = (
            set(shortest_names_existent)
            .union(set(self._nonexistent_notes))
            .union(set(self._md_file_index)))
        if file_type == 'canvas':
            other_fpaths_not_wanted_set = _get_all_valid_media_file_relpaths(
                self._dirpath)
        elif file_type == 'media':
            other_fpaths_not_wanted_set = _get_all_valid_canvas_file_relpaths(
                self._dirpath)
        else:
            raise ValueError('Value for type is either "canvas" or "media".')
        shortest_names_nonexistent = {
            fn: Path(fn) for fn in chain(*links_index.values())
            if fn not in short_names_not_wanted_set
            and Path(fn) not in other_fpaths_not_wanted_set}
        shortest_names = {**shortest_names_existent,
                          **shortest_names_nonexistent}

        # SETS
        # existent files (either linked or not):
        set_files_existent_linked = (
            set(shortest_names_existent)
            .intersection(set(linked_files_list)))
        set_files_existent_not_linked = (
            set(shortest_names_existent)
            .difference(set_files_existent_linked))
        # nonexistent files:
        set_files_nonexistent_linked = (
            set(linked_files_list)
            .intersection(set(shortest_names_nonexistent)))

        # DICTS
        # existent files (either linked or not):
        linked_files_by_short_path = {
            short_path: rel_path
            for short_path, rel_path in shortest_names.items()
            if short_path in set_files_existent_linked}
        non_linked_files_by_short_path = {
            short_path: rel_path
            for short_path, rel_path in shortest_names.items()
            if short_path in set_files_existent_not_linked}
        # nonexistent files:
        nonexistent_files_by_short_path = {
            short_path: np.nan
            for short_path in shortest_names_nonexistent.keys()
            if short_path in set_files_nonexistent_linked}

        return (linked_files_by_short_path,
                non_linked_files_by_short_path,
                nonexistent_files_by_short_path)

    def _get_backlink_counts_for_media_files_only(self) -> dict[str, int]:
        dict_out = dict.fromkeys(self._media_file_index.keys(), 0)
        dict_counts = dict(
            Counter(list(chain(*self._embedded_files_index.values()))))
        # merge counts into dict_out:
        dict_out = {**dict_out, **dict_counts}
        return dict_out

    def _get_backlink_counts_for_canvas_files_only(self) -> dict[str, int]:
        if not self._attachments:
            raise AttributeError('Set attachments=True in connect() to get backlink counts for canvas files.')
        dict_out = dict.fromkeys(self._canvas_file_index.keys(), 0)
        dict_counts = dict(
            Counter(list(chain(*self._wikilinks_index.values()))))
        # merge counts into dict_out:
        dict_out = {**dict_out, **dict_counts}
        return dict_out

    def __get_graph_data_dict(self, *, attachments=False) -> \
            dict[str, list[str]]:
        """Get the dict {k: v} of the graph's data:
        where k is a note name and v is a list of the 'wikilinks' in
        a note.

        The data are used to build the graph, based on the 'wikilinks'
        in each note.  Media files cannot have wikilinks, so they are not
        in the dict keys, but can be inside the dict values as backlinks.
        The detail in the dictionary is used to build the nodes and
        edges in the graph.

        Args:
            attachments (Bool): Defaults to False.  If True, then 'Attachments'
                files will be included as nodes in the graph.  The shortest
                possible filepath will be used for those files (as they are
                would appear in the note editor itself, rather than the full
                relative paths in the Obsidian app's graph view).

        Returns:
            dict
        """
        if not attachments:
            # i) graph uses wikilinks (no embedded files).
            # ii) the wikilinks index will have been set before based on the
            # attachments kwarg to exclude canvas files
            return self._wikilinks_index
        else:
            # attachments include 'media' files and canvas files:
            # i) use wikilinks & embedded file info for graph edges:
            d_out = {
                n: (self._wikilinks_index.get(n, [])
                    + self._embedded_files_index.get(n, [])
                    )
                for n in (set(list(self._wikilinks_index.keys())
                              + list(self._embedded_files_index.keys())))
            }
            # ii) add isolated media files & canvas files as nodes:
            isolated_files_dict = {
                short_path: [] for short_path
                in [*self._isolated_media_files,
                    *self._isolated_canvas_files]}
            d_out = {**d_out,
                     **isolated_files_dict}
            return d_out

    def _set_graph_related_attributes(self):
        self._backlinks_index = self._get_backlinks_index(
            graph=self._graph)
        self._nonexistent_notes = self._get_nonexistent_notes()
        self._isolated_notes = self._get_isolated_notes(
            graph=self._graph)

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
        for f, relpath in self._md_file_index.items():
            self._gather_update_based_on_new_relpath(
                relpath,
                note=f, tags=tags)
        self._is_gathered = True

        return self  # fluent

    def _gather_update_based_on_new_relpath(self, relpath: Path, *,
                                            note: str, tags: list[str]):
        """Individual file read & associated attrs update for the
        gather method."""
        # MAIN file read:
        _, content = _get_md_front_matter_and_content(
            self._dirpath / relpath)
        html = _get_html_from_md_content(content)
        # (also remove LaTeX for source text:)
        src_txt = get_source_text_from_html(
            html, remove_code=True, remove_math=True)

        # 'source' text will not remove any content, but 'readable' will:
        self._source_text_index[note] = src_txt
        self._readable_text_index[note] = (
            _get_readable_text_from_html(
                html, tags=tags))

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
        note is not in the md_file_index at all then the function will raise
        a ValueError.

        Args:
            file_name (str): the filename string that is in the
                md_file_index. This is NOT the filepath!

        Returns:
            list
        """
        if not self._is_connected:
            raise AttributeError('Connect notes before calling the function')

        if file_name not in self._md_file_index:
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
        note is not in the md_file_index at all then the function will raise
        a ValueError.

        Args:
            file_name (str): the filename string that is in the md_file_index.
                This is NOT the filepath!

        Returns:
            list
        """
        if not self._is_connected:
            raise AttributeError('Connect notes before calling the function')

        if file_name not in self._md_file_index:
            raise ValueError('"{}" does not exist so it cannot have embedded files.'.format(file_name))
        else:
            return self._embedded_files_index[file_name]

    def get_md_links(self, file_name: str) -> list[str]:
        """Get markdown links for a note (given its filename).

        Markdown links can only appear in notes that already exist, so if a
        note is not in the md_file_index at all then the function will raise
        a ValueError.

        Args:
            file_name (str): the filename string that is in the md_file_index.
                This is NOT the filepath!

        Returns:
            list
        """
        if not self._is_connected:
            raise AttributeError('Connect notes before calling the function')

        if file_name not in self._md_file_index:
            raise ValueError('"{}" does not exist so it cannot have md links.'.format(file_name))
        else:
            return self._md_links_index[file_name]

    def get_front_matter(self, file_name: str) -> list[dict]:
        """Get front matter for a note (given its filename).

        Front matter can only appear in notes that already exist, so if a
        note is not in the md_file_index at all then the function will raise
        a ValueError.

        Args:
            file_name (str): the filename string that is in the md_file_index.
                This is NOT the filepath!

        Returns:
            list
        """
        if not self._is_connected:
            raise AttributeError('Connect notes before calling the function')
        if file_name not in self._md_file_index:
            raise ValueError('"{}" does not exist so it cannot have front matter.'.format(file_name))
        else:
            return self._front_matter_index[file_name]

    def get_tags(self, file_name: str) -> list[str]:
        """Get tags for a note (given its filename).
        By default, only the highest level of any nested tags is shown
        in the output.

        Tags can only appear in notes that already exist, so if a
        note is not in the md_file_index at all then the function will raise
        a ValueError.

        Args:
            file_name (str): the filename string that is in the
                md_file_index. This is NOT the filepath!

        Returns:
            list
        """
        if not self._is_connected:
            raise AttributeError('Connect notes before calling the function')
        if file_name not in self._md_file_index:
            raise ValueError('"{}" does not exist so it cannot have tags.'.format(file_name))
        else:
            return self._tags_index[file_name]

    def get_source_text(self, file_name: str) -> str:
        """Get text for a note (given its filename).  This requires the vault
        function 'gather' to have been called.

        Text can only appear in notes that already exist, so if a
        note is not in the md_file_index at all then the function will raise
        a ValueError.

        Args:
            file_name (str): the filename string that is in the md_file_index.
                This is NOT the filepath!

        Returns:
            str
        """
        if not self._is_gathered:
            raise AttributeError('Gather notes before calling the function')
        if file_name not in self._md_file_index:
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
        note is not in the md_file_index at all then the function will raise
        a ValueError.

        Args:
            file_name (str): the filename string that is in the md_file_index.
                This is NOT the filepath!

        Returns:
            str
        """
        if not self._is_gathered:
            raise AttributeError('Gather notes before calling the function')
        if file_name not in self._md_file_index:
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

        dict_out = {n: p for n, p in zip(shortest_paths_arr, relpaths_list)}
        return dict_out

    def _get_md_relpaths_by_name(self, **kwargs) -> dict[str, Path]:
        return self.__get_relpaths_by_name(extension='md',
                                           **kwargs)

    def _get_canvas_relpaths_by_name(self, **kwargs) -> dict[str, Path]:
        return self.__get_relpaths_by_name(extension='canvas',
                                           **kwargs)

    @staticmethod
    def _get_backlinks_index(*,
                             graph: nx.MultiDiGraph) -> dict[str, list[str]]:
        """Return k,v pairs
        where k is the md note name
        and v is list of ALL backlinks found in k"""
        return {n: [n[0] for n in list(graph.in_edges(n))]
                for n in graph.nodes}

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

        ix_list = list(set(self._backlinks_index.keys())
                       .difference(set(self._media_file_index))
                       .difference(set(self._nonexistent_media_files))
                       .difference(set(self._canvas_file_index))
                       )

        df = (pd.DataFrame(index=ix_list,
                           columns=METADATA_DF_COLS_GENERIC_TYPE)
              .rename(columns={'file_exists': 'note_exists'})
              .rename_axis('note'))
        df = (df.pipe(self._create_note_metadata_columns)
              .pipe(self._clean_up_note_metadata_dtypes)
              )
        return df

    def _create_note_metadata_columns(self,
                                      df: pd.DataFrame) -> pd.DataFrame:
        """pipe func for mutating df"""
        df['rel_filepath'] = [self._md_file_index.get(f, np.nan)
                              for f in df.index.tolist()]
        df['abs_filepath'] = np.where(df['rel_filepath'].notna(),
                                      [self._dirpath / str(f)
                                       for f in df['rel_filepath'].tolist()],
                                      np.nan)
        df['note_exists'] = np.where(df['rel_filepath'].notna(),
                                     True, False)
        df['n_backlinks'] = [len(self.get_backlinks(f)) for f in df.index]
        df['n_wikilinks'] = np.where(df['note_exists'],
                                     [len(self._wikilinks_index.get(f, []))
                                      for f in df.index.tolist()],
                                     np.nan)
        df['n_tags'] = np.where(df['note_exists'],
                                [len(self._tags_index.get(f, []))
                                 for f in df.index.tolist()],
                                np.nan)
        df['n_embedded_files'] = np.where(df['note_exists'],
                                          [len(self._embedded_files_index.get(
                                              f, []))
                                           for f in df.index.tolist()],
                                          np.nan)
        df['modified_time'] = pd.to_datetime(
            [f.lstat().st_mtime if not pd.isna(f)
             else pd.NaT
             for f in df['abs_filepath'].tolist()],
            unit='s'
        )
        return df

    def _clean_up_note_metadata_dtypes(self,
                                       df: pd.DataFrame) -> pd.DataFrame:
        """pipe func for mutating df"""
        df['rel_filepath'] = np.where(df['rel_filepath'].notna(),
                                      [Path(str(f))
                                       for f in df['rel_filepath']],
                                      np.nan)
        df['n_wikilinks'] = df['n_wikilinks'].astype(float)  # for consistency
        return df

    def get_media_file_metadata(self) -> pd.DataFrame:
        """Get a structured dataset of metadata on the vault's
        media files.  This includes filepaths and counts of different
        link types.

        The df is indexed by media 'file' (i.e. nodes in the graph).
        These will appear in the index:
        1. Embedded files that exist.
        2. Embedded files that don't exist.
        3. Files that exist in the vault but haven't been embedded.

        This dataset is available for however the vault object has
        been set up: it will have metadata on the media files whether
        or not you have configured media files to appear in the
        obsidiantools graph.

        Files that haven't been created will only have info on the number
        of backlinks - other columns will have NaN.

        Returns:
            pd.DataFrame
        """
        ix_list = [*list(self._media_file_index.keys()),
                   *self._nonexistent_media_files]
        df = (pd.DataFrame(index=ix_list,
                           columns=METADATA_DF_COLS_GENERIC_TYPE)
              .rename_axis('file'))
        if not ix_list:
            return df
        else:
            df = df.pipe(self._create_media_file_metadata_columns)
            return df

    def _create_media_file_metadata_columns(self,
                                            df: pd.DataFrame) -> pd.DataFrame:
        """pipe func for mutating df"""
        df['rel_filepath'] = [self._media_file_index.get(f, np.nan)
                              for f in df.index.tolist()]
        df['abs_filepath'] = np.where(df['rel_filepath'].notna(),
                                      [self._dirpath / str(f)
                                       for f in df['rel_filepath'].tolist()],
                                      np.nan)
        df['file_exists'] = pd.Series(
            np.logical_not(df.index.isin(self._nonexistent_media_files)),
            index=df.index)
        df['n_backlinks'] = self._get_backlink_counts_for_media_files_only()
        df['modified_time'] = pd.to_datetime(
            [f.lstat().st_mtime if not pd.isna(f)
             else pd.NaT
             for f in df['abs_filepath'].tolist()],
            unit='s')
        return df

    def get_canvas_file_metadata(self) -> pd.DataFrame:
        """Get a structured dataset of metadata on the vault's
        canvas files.  This includes filepaths and counts of different
        link types.

        The df is indexed by canvas 'file' (i.e. nodes in the graph).
        These will appear in the index:
        1. Linked files that exist.
        2. Linked files that don't exist.
        3. Files that exist in the vault but haven't been linked.

        This dataset is available for however the vault object has
        been set up: it will have metadata on the canvas files whether
        or not you have configured canvas files to appear in the
        obsidiantools graph.  However, n_backlinks column will only be
        calculated if attachments=True in the connect() method.

        Files that haven't been created will only have info on the number
        of backlinks - other columns will have NaN.

        Returns:
            pd.DataFrame
        """
        ix_list = [*list(self._canvas_file_index.keys()),
                   *self._nonexistent_canvas_files]
        df = (pd.DataFrame(index=ix_list,
                           columns=METADATA_DF_COLS_GENERIC_TYPE)
              .rename_axis('file'))
        if not ix_list:
            return df
        else:
            df = df.pipe(self._create_canvas_file_metadata_columns)
            return df

    def _create_canvas_file_metadata_columns(self,
                                             df: pd.DataFrame) -> pd.DataFrame:
        """pipe func for mutating df"""
        df['rel_filepath'] = [self._canvas_file_index.get(f, np.nan)
                              for f in df.index.tolist()]
        df['abs_filepath'] = np.where(df['rel_filepath'].notna(),
                                      [self._dirpath / str(f)
                                       for f in df['rel_filepath'].tolist()],
                                      np.nan)
        df['file_exists'] = pd.Series(
            np.logical_not(df.index.isin(self._nonexistent_canvas_files)),
            index=df.index)
        if self._attachments:
            df['n_backlinks'] = (
                self._get_backlink_counts_for_canvas_files_only())
        else:
            df['n_backlinks'] = np.nan
        df['modified_time'] = pd.to_datetime(
            [f.lstat().st_mtime if not pd.isna(f)
             else pd.NaT
             for f in df['abs_filepath'].tolist()],
            unit='s')
        return df

    def get_all_file_metadata(self) -> pd.DataFrame:
        """Get a structured dataset of metadata on the vault's files, where
        they are supported by the Obsidian app.  This includes detail on
        notes (md files), canvas files and media files.

        The df is indexed by 'file' (i.e. nodes in the graph).
        These will appear in the index:
        1. Linked/embedded files that exist.
        2. Linked/embedded files that don't exist.
        3. Files that exist in the vault but haven't been linked/embedded.

        If attachments=False was set in the connect method, then only notes
        (md files) will appear in the dataset.
        Otherwise, notes, media files and canvas files will appear in the
        dataset.
        In both situations, n_backlinks = n_wikilinks + n_embedded_files.

        Files that haven't been created will only have info on the number
        of backlinks; other columns in the dataset will have NaN values.

        Returns:
            pd.DataFrame
        """
        df = (self.get_note_metadata()
              .rename(columns={'note_exists': 'file_exists'}))
        df['graph_category'] = np.where(
            df['file_exists'], 'note', 'nonexistent')
        if not self._attachments:
            warnings.warn('Only notes (md files) were used to build the graph.  Set attachments=True in the connect method to show all file metadata.')
        else:
            df_media = self.get_media_file_metadata()
            df_media['graph_category'] = np.where(
                df_media['file_exists'], 'attachment', 'nonexistent')
            df_canvas = self.get_canvas_file_metadata()
            df_canvas['graph_category'] = np.where(
                df_canvas['file_exists'], 'attachment', 'nonexistent')

            df = (pd.concat(
                [df, df_media, df_canvas])
                .rename_axis('file'))
        return df

    def _get_nonexistent_notes(self) -> list[str]:
        """Get notes that have backlinks but don't have md files.

        The comparison is done with sets but the result is returned
        as a list."""
        return list(set(self._backlinks_index.keys())
                    # anything remaining that isn't a file is a non-e note:
                    .difference(set(self._md_file_index))
                    .difference(set(self._media_file_index))
                    .difference(set(self._nonexistent_media_files))
                    .difference(set(self._canvas_file_index)))

    def _get_isolated_notes(self, *,
                            graph: nx.MultiDiGraph) -> list[str]:
        """Get notes that are not connected to any other notes in the vault,
        i.e. they have 0 wikilinks and 0 backlinks.

        These notes are retrieved from the graph."""
        return [fn for fn in nx.isolates(graph)
                if fn in self._md_file_index]
