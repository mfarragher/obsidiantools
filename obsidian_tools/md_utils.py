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
            for p in glob(str(dir_path / '**/*.md'))]


def get_wiki_links(filepath):
    """Get wiki links (unique) from a md file.  This accounts for aliases,
    so the [[Lorem ipsum | L.I.]] will be represented as 'Lorem ipsum'.

    Args:
        filepath (pathlib Path): Path object representing the file from
            which info will be extracted.

    Returns:
        list
    """
    html_str = _get_plaintext_from_md_file(filepath)

    wikilinks = _get_unique_wiki_links(html_str, remove_aliases=True)
    return wikilinks


def _get_html_from_md_file(filepath):
    with open(filepath) as f:
        html = markdown.markdown(f.read())
    return html


def _get_plaintext_from_html(html):
    string = html2text.html2text(html)
    return string


def _get_plaintext_from_md_file(filepath):
    html = _get_html_from_md_file(filepath)
    return _get_plaintext_from_html(html)


def _get_all_wiki_links_from_html_content(html_str, *, remove_aliases=True):
    # basic regex that includes any aliases
    wikilink_regex = r'\[{2}([^\]\]]+)\]{2}'

    pattern = re.compile(wikilink_regex)

    link_matches_list = pattern.findall(html_str)
    if remove_aliases:
        link_matches_list = [i.split(" | ")[0]
                             for i in link_matches_list]
    return link_matches_list


def _get_unique_wiki_links(html_str, *, remove_aliases=True):
    wikilinks = _get_all_wiki_links_from_html_content(
        html_str, remove_aliases=remove_aliases)
    return list(set(wikilinks))
