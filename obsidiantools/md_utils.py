import re
from pathlib import Path
from glob import glob
from bs4 import BeautifulSoup
import markdown
import html2text
import frontmatter


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
    plaintext = _get_ascii_plaintext_from_md_file(filepath)

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
    plaintext = _get_ascii_plaintext_from_md_file(filepath)

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
    plaintext = _get_ascii_plaintext_from_md_file(filepath)

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
    text_str = _get_ascii_plaintext_from_md_file(filepath)

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
    text_str = _get_ascii_plaintext_from_md_file(filepath)

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
    return frontmatter.load(filepath).metadata


def _get_html_from_md_file(filepath, remove_front_matter=False):
    """md -> html, via markdown lib."""
    with open(filepath) as f:
        md = f.read()
        if remove_front_matter:
            md = _remove_front_matter_md(md)
        html = markdown.markdown(f.read(), output_format='html')
    return html


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


def _get_ascii_plaintext_from_html(html):
    """html -> ASCII plaintext, via HTML2Text."""
    txt_maker = _get_html2text_obj_with_config()
    doc = txt_maker.handle(html)
    return doc


def _get_ascii_plaintext_from_md_file(filepath):
    """md file -> html -> ASCII plaintext"""
    # strip out front matter (if any):
    html = _get_html_from_md_file(filepath, remove_front_matter=True)
    return _get_ascii_plaintext_from_html(html)


def _remove_front_matter_md(md):
    """Remove front matter from a markdown string."""
    # remove front matter:
    front_matter_regex = r'^---\n(.*?)\n---\n'
    md = re.sub(front_matter_regex, '', md, flags=re.DOTALL)
    return md

def _remove_front_matter(html):
    soup = BeautifulSoup(html, 'lxml')

    hr_content = soup.hr

    if hr_content:
        # wipe out content from first hr (the front matter)
        for fm_detail in hr_content.find_next('p'):
            fm_detail.extract()
        # then wipe all hr elements
        for fm in soup.find_all('hr'):
            fm.decompose()
        return str(soup)
    else:
        return html


def _get_all_wikilinks_and_embedded_files(html_str):
    # basic regex that includes any aliases
    wikilink_regex = r'(!)?\[{2}([^\]\]]+)\]{2}'

    pattern = re.compile(wikilink_regex)

    link_matches_list = pattern.findall(html_str)
    return link_matches_list


def _remove_aliases_from_wikilink_regex_matches(link_matches_list):
    return [(i.split("|")[0].rstrip()  # catch alias/alt-text
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
