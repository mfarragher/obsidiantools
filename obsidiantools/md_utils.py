import re
import yaml
from pathlib import Path
from glob import glob
import markdown
import frontmatter
from ._constants import (WIKILINK_REGEX,
                         TAG_MAIN_ONLY_REGEX, TAG_INCLUDE_NESTED_REGEX,
                         WIKILINK_AS_STRING_REGEX,
                         EMBEDDED_FILE_LINK_AS_STRING_REGEX,
                         INLINE_LINK_AFTER_HTML_PROC_REGEX,
                         INLINE_LINK_VIA_MD_ONLY_REGEX)
from ._io import (get_relpaths_from_dir,
                  get_relpaths_matching_subdirs)
from .html_processing import (_get_plaintext_from_html,
                              _remove_code, _remove_latex, _remove_del_text,
                              _remove_main_formatting,
                              _get_all_latex_from_html_content)


def get_md_relpaths_from_dir(dir_path: Path) -> list[Path]:
    """Get list of relative paths for markdown files in a given directory,
    including any subdirectories.

    Thus if the vault directory is the argument, then the function returns
    a list of all the md files found in the vault.

    Args:
        dir_path (pathlib Path): Path object representing the directory
            to search.

    Returns:
        list of Path objects
    """
    return get_relpaths_from_dir(dir_path, extension='md')


def get_md_relpaths_matching_subdirs(dir_path: Path, *,
                                     include_subdirs: list = None,
                                     include_root: bool = True) -> list[Path]:
    """Get list of relative paths for markdown files in a given directory,
    filtered to include specified subdirectories (with include_subdirs
    kwarg).  The default arguments align with get_md_relpaths_from_dir
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
        extension='md',
        include_subdirs=include_subdirs,
        include_root=include_root)


def get_wikilinks(filepath: Path) -> list[str]:
    """Get ALL wikilinks from a md file.
    The links' order of appearance in the file IS preserved in the output.

    This accounts for:
    - Aliases / alt text, so [[Lorem ipsum|L.I.]]
    will be represented as 'Lorem ipsum'.
    - Header text links, so [[Lorem ipsum#Dummy text]]
    will be represented as 'Lorem ipsum'.

    The links' order of appearance in the file IS preserved in the output.

    Args:
        filepath (pathlib Path): Path object representing the file from
            which info will be extracted.

    Returns:
        list of strings
    """
    src_txt = get_source_text_from_md_file(filepath, remove_code=True)

    wikilinks = _get_all_wikilinks_from_source_text(
        src_txt, remove_aliases=True)
    return wikilinks


def get_embedded_files(filepath: Path) -> list[str]:
    """Get ALL embedded files from a md file.
    The embedded files' order of appearance in the file IS preserved in the output.

    This accounts for:
    - Aliases / alt text, so [[Lorem ipsum|L.I.]]
    will be represented as 'Lorem ipsum'.

    The links' order of appearance in the file IS preserved in the output.

    Args:
        filepath (pathlib Path): Path object representing the file from
            which info will be extracted.

    Returns:
        list of strings
    """
    src_txt = get_source_text_from_md_file(filepath, remove_code=True)

    files = _get_all_embedded_files_from_source_text(
        src_txt, remove_aliases=True)
    return files


def get_unique_wikilinks(filepath: Path) -> list[str]:
    """Get UNIQUE wikilinks from a md file.
    The links' order of appearance in the file IS preserved in the output.

    This accounts for:
    - Aliases / alt text, so [[Lorem ipsum|L.I.]]
    will be represented as 'Lorem ipsum'.
    - Header text links, so [[Lorem ipsum#Dummy text]]
    will be represented as 'Lorem ipsum'.

    Args:
        filepath (pathlib Path): Path object representing the file from
            which info will be extracted.

    Returns:
        list of strings
    """
    src_txt = get_source_text_from_md_file(filepath, remove_code=True)

    wikilinks = _get_unique_wikilinks_from_source_text(src_txt, remove_aliases=True)
    return wikilinks


def get_md_links(filepath: Path) -> list[str]:
    """Get markdown links from a md file.
    The links' order of appearance in the file IS preserved in the output.

    This is to check for syntax of the format [...](...).
    The returned 'links' inside the () are not checked for validity or
    subtle differences (e.g. '/' vs no '/' at the end of a URL).

    Args:
        filepath (pathlib Path): Path object representing the file from
            which info will be extracted.

    Returns:
        list of strings
    """
    src_txt = get_source_text_from_md_file(filepath, remove_code=True)
    return _get_md_links_from_source_text(src_txt)


def _get_md_links_from_source_text(src_txt: str) -> list[str]:
    links = _get_all_md_link_info_from_source_text(src_txt)
    if links:  # return links only, not their text
        return [t[-1] for t in links]
    else:
        return links  # empty list


def get_unique_md_links(filepath: Path) -> list[str]:
    """Get markdown links (unique) from a md file.
    The links' order of appearance in the file IS preserved in the output.

    This is to check for syntax of the format [...](...).
    The returned 'links' inside the () are not checked for validity or
    subtle differences (e.g. '/' vs no '/' at the end of a URL).

    Args:
        filepath (pathlib Path): Path object representing the file from
            which info will be extracted.

    Returns:
        list of strings
    """
    src_txt = get_source_text_from_md_file(filepath, remove_code=True)

    links = _get_unique_md_links_from_source_text(src_txt)
    return links


def get_front_matter(filepath: Path) -> dict:
    """Get front matter from a md file.

    If no front matter is found for a file, the value will be {}.

    Args:
        filepath (pathlib Path): Path object representing the file from
            which info will be extracted.
    Returns:
        dict
    """
    front_matter, _ = _get_md_front_matter_and_content(filepath)
    return front_matter


def get_tags(filepath: Path, *, show_nested: bool = False) -> list[str]:
    """Get tags from a md file, based on the order they appear in the file.
    By default, only the highest level of any nested tags is shown in the
    output.

    If no tags are found for a file, the value will be [].

    Args:
        filepath (pathlib Path): Path object representing the file from
            which info will be extracted.
        show_nested (Boolean): show nested tags in the output.  Defaults to
            False (which would mean only the highest level of any nested tags
            are included in the output).
    Returns:
        list
    """
    # get text from source file, but remove any '\#' and code:
    src_txt = get_source_text_from_md_file(
        filepath, remove_code=True,
        str_transform_func=_transform_md_file_string_for_tag_parsing)
    # remove wikilinks so that '#' headers are not caught:
    src_txt = _remove_wikilinks_from_source_text(src_txt)
    tags = _get_tags_from_source_text(src_txt, show_nested=show_nested)
    return tags


def _get_md_front_matter_and_content(filepath: Path, *,
                                     str_transform_func=None) -> tuple[dict, str]:
    """parse md file into front matter and note content"""
    with open(filepath, encoding='utf-8') as f:
        try:
            file_string = f.read()
            if str_transform_func:
                file_string = str_transform_func(file_string)
            return frontmatter.parse(file_string)
        # for invalid YAML, return the whole file as content:
        except yaml.scanner.ScannerError as e:
            print(f"Front matter not populated for {filepath.name}: {repr(e)}")
            return {}, file_string
        except yaml.parser.ParserError as e:
            print(f"Front matter not populated for {filepath.name}: {repr(e)}")
            return {}, file_string
        # handle template {{}} chars in front matter:
        except yaml.constructor.ConstructorError:
            file_string_esc = file_string.translate(
                str.maketrans({"{": r"\{",
                               "}": r"\}"}))
            return frontmatter.parse(file_string_esc)
        # any others:
        except:
            return {}, file_string


def _get_html_from_md_file(filepath: Path, *,
                           str_transform_func=None) -> str:
    """md file -> html (without front matter).

    pymarkdown extensions are used and configured to reflect the Obsidian
    experience as much as possible.  For example, arithmatex is necessary
    to parse math, md_mermaid for mermaid diagram support, etc.
    """
    _, md_content = _get_md_front_matter_and_content(
        filepath,
        str_transform_func=str_transform_func)
    html = _get_html_from_md_content(md_content)
    return html


def _get_html_from_md_content(md_content: str) -> str:
    """md content -> html (without front matter)"""
    html = markdown.markdown(md_content, output_format='html',
                             extensions=['pymdownx.arithmatex',
                                         'pymdownx.superfences',
                                         'pymdownx.mark',
                                         'pymdownx.tilde',
                                         'pymdownx.saneheaders',
                                         'footnotes',
                                         'sane_lists',
                                         'tables'],
                             extension_configs={'pymdownx.tilde':
                                                {'subscript': False}})
    return html


def get_source_text_from_html(html: str, *,
                              remove_code: bool = False,
                              remove_math: bool = False) -> str:
    """html (without front matter) -> ASCII plaintext"""
    if remove_code:
        html = _remove_code(html)
    if remove_math:
        html = _remove_latex(html)
    return _get_plaintext_from_html(html)


def get_source_text_from_md_file(filepath: Path, *,
                                 remove_code: bool = False,
                                 remove_math: bool = False,
                                 str_transform_func=None) -> str:
    """md file -> html (without front matter) -> ASCII plaintext"""
    # strip out front matter (if any):
    html = _get_html_from_md_file(
        filepath,
        str_transform_func=str_transform_func)

    return get_source_text_from_html(html, remove_code=remove_code,
                                     remove_math=remove_math)


def get_readable_text_from_md_file(filepath: Path, *,
                                   tags: list[str] = None) -> str:
    """md file -> html -> plaintext with major formatting removed."""
    # strip out front matter (if any):
    html = _get_html_from_md_file(
        filepath)
    # wikilinks and md links as text:
    html = _replace_md_links_with_their_text(html)
    html = _replace_wikilinks_with_their_text(html)
    html = _remove_embedded_file_links_from_text(html)
    # remove code and remove major formatting on text:
    html = _remove_code(html)
    html = _remove_latex(html)
    html = _remove_del_text(html)
    if tags is not None:
        html = _remove_main_formatting(html, tags=tags)
    else:  # defaults
        html = _remove_main_formatting(html)

    return _get_plaintext_from_html(html)


def _get_all_wikilinks_and_embedded_files(src_txt: str) -> list[str]:
    # extract links
    pattern = re.compile(WIKILINK_REGEX)

    link_matches_list = pattern.findall(src_txt)
    return link_matches_list


def _remove_aliases_from_wikilink_regex_matches(link_matches_list: list[str]) -> list[str]:
    return [(i.replace('\\', '')
             .split("|")[0].rstrip()  # catch alias/alt-text
             .split('#', 1)[0])  # catch links to headers
            for i in link_matches_list]


def _get_all_wikilinks_from_source_text(src_txt: str, *,
                                        remove_aliases: bool = True) -> list[str]:
    matches_list = _get_all_wikilinks_and_embedded_files(src_txt)
    link_matches_list = [g[1] for g in matches_list
                         if g[0] == '']

    if remove_aliases:
        link_matches_list = _remove_aliases_from_wikilink_regex_matches(
            link_matches_list)

    # remove .md:
    link_matches_list = [name.removesuffix('.md')
                         for name in link_matches_list]
    return link_matches_list


def _get_all_embedded_files_from_source_text(src_txt: str, *,
                                             remove_aliases: bool = True) -> list[str]:
    matches_list = _get_all_wikilinks_and_embedded_files(src_txt)
    embedded_files_sublist = [g[1] for g in matches_list
                              if g[0] == '!']

    if remove_aliases:
        embedded_files_sublist = _remove_aliases_from_wikilink_regex_matches(
            embedded_files_sublist)
    return embedded_files_sublist


def _get_all_latex_from_md_file(filepath: Path) -> list[str]:
    return _get_all_latex_from_html_content(
        _get_html_from_md_file(filepath))


def _get_unique_wikilinks_from_source_text(src_txt: str, *,
                                           remove_aliases: bool = True) -> list[str]:
    wikilinks = _get_all_wikilinks_from_source_text(
        src_txt, remove_aliases=remove_aliases)
    return list(dict.fromkeys(wikilinks))


def _get_all_md_link_info_from_source_text(src_txt: str) -> list[tuple[str]]:
    links_regex = re.compile(INLINE_LINK_AFTER_HTML_PROC_REGEX)

    links_list_of_tuples = list(links_regex.findall(src_txt))
    return links_list_of_tuples


def _get_unique_md_links_from_source_text(src_txt: str) -> list[str]:
    links_detail = _get_all_md_link_info_from_source_text(
        src_txt)
    links_list = [link for _, link in links_detail]
    return list(dict.fromkeys(links_list))


def _remove_wikilinks_from_source_text(src_txt: str) -> str:
    return re.sub(WIKILINK_REGEX, '', src_txt)


def _transform_md_file_string_for_tag_parsing(txt: str) -> str:
    return txt.replace('\\#', '')


def _get_tags_from_source_text(src_txt: str, *,
                               show_nested: bool = False) -> list[str]:
    if not show_nested:
        pattern = re.compile(TAG_MAIN_ONLY_REGEX)
    else:
        pattern = re.compile(TAG_INCLUDE_NESTED_REGEX)
    tags_list = pattern.findall(src_txt)
    return tags_list


def _replace_wikilinks_with_their_text(src_txt: str) -> str:
    # get list of wikilinks as strings:
    links_list = _get_all_wikilinks_from_source_text(
        src_txt, remove_aliases=False)

    # get links in their text format:
    readable_text_list = [(i.replace('\\', '')
                           # get wikilinks w/o alias, otherwise alias:
                           .split("|")[-1]
                           .strip())
                          for i in links_list]

    # loop over txt content to replace "[[...]]" wikilinks w/ readable text:
    out_str = src_txt
    links_w_brackets_list = ["".join(["[[", i, "]]"]) for i in links_list]
    switch_dict = dict(zip(links_w_brackets_list, readable_text_list))

    for k, v in switch_dict.items():
        out_str = out_str.replace(k, v)
    return out_str


def _replace_md_links_with_their_text(src_txt: str) -> str:
    # get list of wikilinks as strings:
    matched_text_list = re.findall(WIKILINK_AS_STRING_REGEX, src_txt)
    # get the detail from groups:
    links_detail = re.findall(INLINE_LINK_VIA_MD_ONLY_REGEX, src_txt)

    # get links in their text format:
    readable_text_list = [text for text, _ in links_detail]

    # loop over txt content to replace md links w/ readable text:
    out_str = src_txt
    switch_dict = dict(zip(matched_text_list, readable_text_list))

    for k, v in switch_dict.items():
        out_str = out_str.replace(k, v)
    return out_str


def _remove_embedded_file_links_from_text(src_txt: str) -> str:
    # get list of embedded file links as strings:
    links_list = re.findall(EMBEDDED_FILE_LINK_AS_STRING_REGEX, src_txt)
    # add in the ![[...]] chars:
    links_list = ["".join(['![[', i, ']]']) for i in links_list]

    # remove from text:
    out_str = src_txt
    for i in links_list:
        out_str = out_str.replace(i, '')
    return out_str
