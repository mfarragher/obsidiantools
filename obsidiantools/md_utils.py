import re
import yaml
from pathlib import Path
from glob import glob
import markdown
import frontmatter
from .html_processing import (_get_source_plaintext_from_html,
                              _remove_code, _remove_latex, _remove_del_text,
                              _remove_main_formatting,
                              _get_all_latex_from_html_content)

# wikilink & embedded file regex: regex that includes any aliases
# group 0 captures embedded link; group 1 is everything inside [[]]
WIKILINK_REGEX = r'(!)?\[{2}([^\]\]]+)\]{2}'
# md links regex: catch URLs or paths
INLINE_LINK_AFTER_HTML_PROC_REGEX = r'\[([^\]]+)\]\(<([^)]+)>\)'
INLINE_LINK_VIA_MD_ONLY_REGEX = r'\[([^\]]+)\]\(([^)]+)\)'


def get_md_relpaths_from_dir(dir_path):
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
    return [Path(p).relative_to(dir_path)
            for p in glob(f"{dir_path}/**/*.md", recursive=True)]


def get_md_relpaths_matching_subdirs(dir_path, *,
                                     include_subdirs=None, include_root=True):
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
    if include_subdirs:
        include_subdirs_final = [str(Path(i).as_posix())
                                 for i in include_subdirs]

    if not include_subdirs and include_root:
        return get_md_relpaths_from_dir(dir_path)
    elif not include_subdirs and not include_root:
        return [i for i in get_md_relpaths_from_dir(dir_path)
                if str(i.parent.as_posix()) != '.']
    else:
        if include_root:
            return [i for i in get_md_relpaths_from_dir(dir_path)
                    if str(i.parent.as_posix())
                    in include_subdirs_final + ['.']]
        else:
            return [i for i in get_md_relpaths_from_dir(dir_path)
                    if str(i.parent.as_posix())
                    in include_subdirs_final]


def get_wikilinks(filepath):
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
    src_txt = _get_source_text_from_md_file(filepath, remove_code=True)

    wikilinks = _get_all_wikilinks_from_source_text(
        src_txt, remove_aliases=True)
    return wikilinks


def get_embedded_files(filepath):
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
    src_txt = _get_source_text_from_md_file(filepath, remove_code=True)

    files = _get_all_embedded_files_from_source_text(
        src_txt, remove_aliases=True)
    return files


def get_unique_wikilinks(filepath):
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
    src_txt = _get_source_text_from_md_file(filepath, remove_code=True)

    wikilinks = _get_unique_wikilinks(src_txt, remove_aliases=True)
    return wikilinks


def get_md_links(filepath):
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
    src_txt = _get_source_text_from_md_file(filepath, remove_code=True)

    links = _get_all_md_link_info_from_source_text(src_txt)
    if links:  # return links only, not their text
        return [t[-1] for t in links]
    else:
        return links  # empty list


def get_unique_md_links(filepath):
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
    src_txt = _get_source_text_from_md_file(filepath, remove_code=True)

    links = _get_unique_md_links_from_source_text(src_txt)
    return links


def get_front_matter(filepath):
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


def get_tags(filepath):
    """Get tags from a md file, based on the order they appear in the file.
    Only top-level tags are extracted: nested tag detail is NOT supported.

    If no tags are found for a file, the value will be [].

    Args:
        filepath (pathlib Path): Path object representing the file from
            which info will be extracted.
    Returns:
        list
    """
    # get text from source file, but remove any '\#' and code:
    src_txt = _get_source_text_from_md_file(
        filepath, remove_code=True,
        str_transform_func=_transform_md_file_string_for_tag_parsing)
    # remove wikilinks so that '#' headers are not caught:
    src_txt = _remove_wikilinks_from_source_text(src_txt)
    tags = _get_tags_from_source_text(src_txt)
    return tags


def _get_md_front_matter_and_content(filepath, *, str_transform_func=None):
    """parse md file into front matter and note content"""
    with open(filepath, encoding='utf-8') as f:
        try:
            file_string = f.read()
            if str_transform_func:
                file_string = str_transform_func(file_string)
            return frontmatter.parse(file_string)
        # for invalid YAML, return the whole file as content:
        except yaml.scanner.ScannerError:
            return {}, file_string
        # handle template {{}} chars in front matter:
        except yaml.constructor.ConstructorError:
            file_string_esc = file_string.translate(
                str.maketrans({"{": r"\{",
                               "}": r"\}"}))
            return frontmatter.parse(file_string_esc)


def _get_html_from_md_file(filepath, *, str_transform_func=None):
    """md file -> html (without front matter).

    pymarkdown extensions are used and configured to reflect the Obsidian
    experience as much as possible.  For example, arithmatex is necessary
    to parse math, md_mermaid for mermaid diagram support, etc.
    """
    _, content = _get_md_front_matter_and_content(
        filepath,
        str_transform_func=str_transform_func)
    html = markdown.markdown(content, output_format='html',
                             extensions=['pymdownx.arithmatex',
                                         'pymdownx.mark',
                                         'pymdownx.tilde',
                                         'pymdownx.saneheaders',
                                         'footnotes',
                                         'sane_lists',
                                         'tables'],
                             extension_configs={'pymdownx.tilde':
                                                {'subscript': False}})
    return html


def _get_source_text_from_md_file(filepath, *,
                                  remove_code=False, str_transform_func=None):
    """md file -> html (without front matter) -> ASCII plaintext"""
    # strip out front matter (if any):
    html = _get_html_from_md_file(
        filepath,
        str_transform_func=str_transform_func)
    if remove_code:
        html = _remove_code(html)
    return _get_source_plaintext_from_html(html)


def _get_readable_text_from_md_file(filepath, *, tags=None):
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

    return _get_source_plaintext_from_html(html)


def _get_all_wikilinks_and_embedded_files(src_txt):
    # extract links
    pattern = re.compile(WIKILINK_REGEX)

    link_matches_list = pattern.findall(src_txt)
    return link_matches_list


def _remove_aliases_from_wikilink_regex_matches(link_matches_list):
    return [(i.replace('\\', '')
             .split("|")[0].rstrip()  # catch alias/alt-text
             .split('#', 1)[0])  # catch links to headers
            for i in link_matches_list]


def _get_all_wikilinks_from_source_text(src_txt, *, remove_aliases=True):
    matches_list = _get_all_wikilinks_and_embedded_files(src_txt)
    link_matches_list = [g[1] for g in matches_list
                         if g[0] == '']

    if remove_aliases:
        link_matches_list = _remove_aliases_from_wikilink_regex_matches(
            link_matches_list)
    return link_matches_list


def _get_all_embedded_files_from_source_text(src_txt, *,
                                             remove_aliases=True):
    matches_list = _get_all_wikilinks_and_embedded_files(src_txt)
    embedded_files_sublist = [g[1] for g in matches_list
                              if g[0] == '!']

    if remove_aliases:
        embedded_files_sublist = _remove_aliases_from_wikilink_regex_matches(
            embedded_files_sublist)
    return embedded_files_sublist


def _get_all_latex_from_md_file(filepath):
    return _get_all_latex_from_html_content(
        _get_html_from_md_file(filepath))


def _get_unique_wikilinks(src_txt, *, remove_aliases=True):
    wikilinks = _get_all_wikilinks_from_source_text(
        src_txt, remove_aliases=remove_aliases)
    return list(dict.fromkeys(wikilinks))


def _get_all_md_link_info_from_source_text(src_txt):
    links_regex = re.compile(INLINE_LINK_AFTER_HTML_PROC_REGEX)

    links_list_of_tuples = list(links_regex.findall(src_txt))
    return links_list_of_tuples


def _get_unique_md_links_from_source_text(src_txt):
    links_detail = _get_all_md_link_info_from_source_text(
        src_txt)
    links_list = [link for _, link in links_detail]
    return list(dict.fromkeys(links_list))


def _remove_wikilinks_from_source_text(src_txt):
    return re.sub(WIKILINK_REGEX, '', src_txt)


def _transform_md_file_string_for_tag_parsing(txt):
    return txt.replace('\\#', '')


def _get_tags_from_source_text(src_txt):
    tags_regex = r'(?<!\()#{1}([A-z]+[0-9_\-]*[A-Z0-9]?)\/?'
    pattern = re.compile(tags_regex)
    tags_list = pattern.findall(src_txt)
    return tags_list


def _replace_wikilinks_with_their_text(src_txt):
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


def _replace_md_links_with_their_text(src_txt):
    # get list of wikilinks as strings:
    matched_text_list = re.findall(r'\[[^\]]+\]\([^)]+\)', src_txt)
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


def _remove_embedded_file_links_from_text(src_txt):
    # get list of embedded file links as strings:
    links_list = re.findall(r'!?\[{2}([^\]\]]+)\]{2}', src_txt)
    # add in the ![[...]] chars:
    links_list = ["".join(['![[', i, ']]']) for i in links_list]

    # remove from text:
    out_str = src_txt
    for i in links_list:
        out_str = out_str.replace(i, '')
    return out_str
