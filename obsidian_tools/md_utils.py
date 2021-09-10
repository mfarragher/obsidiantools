import re
from pathlib import Path
from glob import glob
import markdown
import html2text


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


def _get_html_from_md_file(filepath):
    """md -> html, via markdown lib."""
    with open(filepath) as f:
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
    html = _get_html_from_md_file(filepath)
    return _get_ascii_plaintext_from_html(html)


def _get_all_wikilinks_from_html_content(html_str, *, remove_aliases=True):
    # basic regex that includes any aliases
    wikilink_regex = r'\[{2}([^\]\]]+)\]{2}'

    pattern = re.compile(wikilink_regex)

    link_matches_list = pattern.findall(html_str)
    if remove_aliases:
        link_matches_list = [(i.split("|")[0].rstrip()  # catch alias/alt-text
                              .split('#', 1)[0])  # catch links to headers
                             for i in link_matches_list]
    return link_matches_list


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
