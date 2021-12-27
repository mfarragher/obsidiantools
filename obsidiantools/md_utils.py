import re
import yaml
from pathlib import Path
from glob import glob
from bs4 import BeautifulSoup
import markdown
import html2text
import frontmatter

# basic wikilink regex that includes any aliases
WIKILINK_REGEX = r'(!)?\[{2}([^\]\]]+)\]{2}'


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
            for p in glob(str(dir_path / '**/*.md'), recursive=True)]


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
    if not include_subdirs and include_root:
        return get_md_relpaths_from_dir(dir_path)
    elif not include_subdirs and not include_root:
        return [i for i in get_md_relpaths_from_dir(dir_path)
                if str(i.parent) != '.']
    else:
        if include_root:
            return [i for i in get_md_relpaths_from_dir(dir_path)
                    if str(i.parent) in include_subdirs + ['.']]
        else:
            return [i for i in get_md_relpaths_from_dir(dir_path)
                    if str(i.parent) in include_subdirs]


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
    plaintext = _get_ascii_plaintext_from_md_file(filepath, remove_code=True)

    wikilinks = _get_all_wikilinks_from_html_content(
        plaintext, remove_aliases=True)
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
    plaintext = _get_ascii_plaintext_from_md_file(filepath, remove_code=True)

    files = _get_all_embedded_files_from_html_content(
        plaintext, remove_aliases=True)
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
    plaintext = _get_ascii_plaintext_from_md_file(filepath, remove_code=True)

    wikilinks = _get_unique_wikilinks(plaintext, remove_aliases=True)
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
    text_str = _get_ascii_plaintext_from_md_file(filepath, remove_code=True)

    links = _get_all_md_link_info_from_ascii_plaintext(text_str)
    if links:  # links only, not their text
        return [t[-1] for t in links]
    else:
        return links


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
    text_str = _get_ascii_plaintext_from_md_file(filepath, remove_code=True)

    links = _get_unique_md_links_from_ascii_plaintext(text_str)
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
    text_str = _get_ascii_plaintext_from_md_file(filepath, remove_code=True)
    text_str = _remove_wikilinks_from_ascii_plaintext(text_str)
    tags = _get_tags_from_ascii_plaintext(text_str)
    return tags


def _get_html2text_obj_with_config():
    """Get HTML2Text object with config set."""
    txt_maker = html2text.HTML2Text()

    # some settings to avoid newline problems with links
    txt_maker.ignore_links = False
    txt_maker.body_width = 0
    txt_maker.protect_links = True
    txt_maker.wrap_links = False
    # remove md formatting chars
    txt_maker.ignore_emphasis = True
    return txt_maker


def _get_md_front_matter_and_content(filepath):
    """parse md file into front matter and note content"""
    with open(filepath) as f:
        try:
            front_matter, content = frontmatter.parse(f.read())
        except yaml.scanner.ScannerError:
            # for invalid YAML, return the whole file as content:
            return {}, frontmatter.parse(f.read())
    return (front_matter, content)


def _get_html_from_md_file(filepath):
    """md file -> html (without front matter)"""
    _, content = _get_md_front_matter_and_content(filepath)
    return markdown.markdown(content, output_format='html')


def _get_ascii_plaintext_from_html(html):
    """html -> ASCII plaintext, via HTML2Text."""
    txt_maker = _get_html2text_obj_with_config()
    doc = txt_maker.handle(html)
    return doc


def _get_ascii_plaintext_from_md_file(filepath, *, remove_code=False):
    """md file -> html -> ASCII plaintext"""
    # strip out front matter (if any):
    html = _get_html_from_md_file(filepath)
    if remove_code:
        html = _remove_code(html)
    return _get_ascii_plaintext_from_html(html)


def _remove_code(html):
    # exclude 'code' tags from link output:
    soup = BeautifulSoup(html, 'lxml')
    for s in soup.select('code'):
        s.extract()
    html_str = str(soup)
    return html_str


def _get_all_wikilinks_and_embedded_files(html):
    # extract links
    pattern = re.compile(WIKILINK_REGEX)

    link_matches_list = pattern.findall(html)
    return link_matches_list


def _remove_aliases_from_wikilink_regex_matches(link_matches_list):
    return [(i.replace('\\', '')
             .split("|")[0].rstrip()  # catch alias/alt-text
             .split('#', 1)[0])  # catch links to headers
            for i in link_matches_list]


def _get_all_wikilinks_from_html_content(html_str, *, remove_aliases=True):
    matches_list = _get_all_wikilinks_and_embedded_files(html_str)
    link_matches_list = [g[1] for g in matches_list
                         if g[0] == '']

    if remove_aliases:
        link_matches_list = _remove_aliases_from_wikilink_regex_matches(
            link_matches_list)
    return link_matches_list


def _get_all_embedded_files_from_html_content(html_str, *,
                                              remove_aliases=True):
    matches_list = _get_all_wikilinks_and_embedded_files(html_str)
    embedded_files_sublist = [g[1] for g in matches_list
                              if g[0] == '!']

    if remove_aliases:
        embedded_files_sublist = _remove_aliases_from_wikilink_regex_matches(
            embedded_files_sublist)
    return embedded_files_sublist


def _get_unique_wikilinks(html_str, *, remove_aliases=True):
    wikilinks = _get_all_wikilinks_from_html_content(
        html_str, remove_aliases=remove_aliases)
    return list(dict.fromkeys(wikilinks))


def _get_all_md_link_info_from_ascii_plaintext(plaintext):
    # basic regex e.g. catch URLs or paths
    inline_link_regex = re.compile(r'\[([^\]]+)\]\(<([^)]+)>\)')

    links_list_of_tuples = list(inline_link_regex.findall(plaintext))
    return links_list_of_tuples


def _get_unique_md_links_from_ascii_plaintext(plaintext):
    links_detail = _get_all_md_link_info_from_ascii_plaintext(
        plaintext)
    links_list = [link for _, link in links_detail]
    return list(dict.fromkeys(links_list))


def _remove_wikilinks_from_ascii_plaintext(plaintext):
    return re.sub(r'[\[]{2}.*[\]]{2}', '', plaintext)


def _get_tags_from_ascii_plaintext(plaintext):
    tags_regex = r'(?<!\()#{1}([A-z]+[0-9_\-]*[A-Z0-9]?)\/?'
    pattern = re.compile(tags_regex)
    tags_list = pattern.findall(plaintext)
    return tags_list
