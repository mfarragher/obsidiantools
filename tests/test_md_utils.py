import pytest


from obsidiantools.md_utils import (_get_all_wikilinks_from_html_content,
                                    _get_unique_wikilinks,
                                    _get_all_md_link_info_from_ascii_plaintext,
                                    _get_unique_md_links_from_ascii_plaintext,
                                    _get_html_from_md_file,
                                    _get_front_matter_metadata_from_md_file)


@pytest.fixture
def html_wikilinks_stub():
    html = r"""
    <pre><code># Intro
    This is a very basic string representation.

    ## Shopping list
    Here is a **[[Shopping list | shopping list]]**:
    - [[Bananas]]: also have these for [[Banana splits]]
    - [[Apples]]
    - [[Flour]]: not a [[Flower | flower]]

    Oh and did I say [[Bananas | BANANAS]]??
    There's no link for [Cherries].  Though there is for [[Durians]].

    ## Drinks
    - [[Apples|Freshly squeezed apple juice]]
    - [[Bananas|Banana smoothie]]
    - [[Protein shakes#Protein powder|Vanilla whey protein]]
    """
    return html


@pytest.fixture
def txt_md_links_stub():
    text = r"""
    * [The Times 03/Jan/2009 Chancellor on brink of second bailout for banks](<https://www.thetimes.co.uk/article/chancellor-alistair-darling-on-brink-of-second-bailout-for-banks-n9l382mn62h>)
    * [Chancellor Alistair Darling on brink of second bailout for banks](<https://www.thetimes.co.uk/article/chancellor-alistair-darling-on-brink-of-second-bailout-for-banks-n9l382mn62h>)
    * [This is a statement inside square brackets]
    * (This is a statement inside parentheses)
    * (<https://www.markdownguide.org/basic-syntax/>)[Getting the bracket types in wrong order]
    * [Markdown basic syntax - <> not in the link](https://www.markdownguide.org/basic-syntax/)
    * []()
    * [()]
    * ([])
    * [([)
    * ([)]

    [ADA](<https://cardano.org/>)
    """
    return text


@pytest.fixture
def txt_sussudio_stub():
    text = _get_html_from_md_file('tests/vault-stub/Sussudio.md')
    return text


def test_get_all_wikilinks_from_html_content(html_wikilinks_stub):
    actual_results = _get_all_wikilinks_from_html_content(html_wikilinks_stub)
    expected_results = ['Shopping list', 'Bananas', 'Banana splits',
                        'Apples',
                        'Flour', 'Flower',
                        'Bananas',
                        'Durians',
                        'Apples', 'Bananas', 'Protein shakes']

    assert actual_results == expected_results


def test_get_all_wikilinks_from_html_content_keep_aliases(html_wikilinks_stub):
    actual_results = _get_all_wikilinks_from_html_content(
        html_wikilinks_stub, remove_aliases=False)
    expected_results = ['Shopping list | shopping list',
                        'Bananas', 'Banana splits',
                        'Apples',
                        'Flour', 'Flower | flower',
                        'Bananas | BANANAS',
                        'Durians',
                        'Apples|Freshly squeezed apple juice',
                        'Bananas|Banana smoothie',
                        'Protein shakes#Protein powder|Vanilla whey protein']

    assert actual_results == expected_results


def test_get_unique_wikilinks_from_html_content(html_wikilinks_stub):
    actual_results = _get_unique_wikilinks(
        html_wikilinks_stub, remove_aliases=True)
    expected_results = ['Shopping list',
                        'Bananas', 'Banana splits',
                        'Apples',
                        'Flour', 'Flower',
                        'Durians',
                        'Protein shakes']

    assert actual_results == expected_results
    assert isinstance(expected_results, list)


def test_get_unique_wikilinks_from_html_content_has_unique_links(html_wikilinks_stub):
    actual_links = _get_unique_wikilinks(html_wikilinks_stub)
    assert len(set(actual_links)) == len(actual_links)


def test_get_all_md_link_info(txt_md_links_stub):
    expected_links = [('The Times 03/Jan/2009 Chancellor on brink of second bailout for banks',
                       'https://www.thetimes.co.uk/article/chancellor-alistair-darling-on-brink-of-second-bailout-for-banks-n9l382mn62h'),
                      ("Chancellor Alistair Darling on brink of second bailout for banks",
                      'https://www.thetimes.co.uk/article/chancellor-alistair-darling-on-brink-of-second-bailout-for-banks-n9l382mn62h'),
                      ('ADA', 'https://cardano.org/')
                      ]
    actual_links = _get_all_md_link_info_from_ascii_plaintext(txt_md_links_stub)

    assert actual_links == expected_links


def test_get_unique_md_links_has_order_preserved(txt_md_links_stub):
    expected_links = ['https://www.thetimes.co.uk/article/chancellor-alistair-darling-on-brink-of-second-bailout-for-banks-n9l382mn62h',
                      'https://cardano.org/']
    actual_links = _get_unique_md_links_from_ascii_plaintext(txt_md_links_stub)

    assert actual_links == expected_links


def test_get_unique_md_links_has_unique_links(txt_md_links_stub):
    actual_links = _get_unique_md_links_from_ascii_plaintext(txt_md_links_stub)
    assert len(set(actual_links)) == len(actual_links)


def test_pretend_wikilink_not_extracted_from_front_matter(txt_sussudio_stub):
    actual_links = _get_unique_wikilinks(txt_sussudio_stub)
    assert not set(['American Psycho (film)']).issubset(set(actual_links))


def test_sussudio_front_matter():
    expected_metadata = {'title': 'Sussudio',
                         'artist': 'Phil Collins',
                         'category': 'music',
                         'year': 1985,
                         'url': 'https://www.discogs.com/Phil-Collins-Sussudio/master/106239',
                         'references': [[['American Psycho (film)']], 'Polka Party!'],
                         'chart_peaks': [{'US': 1}, {'UK': 12}]}
    actual_metadata = _get_front_matter_metadata_from_md_file(
        'tests/vault-stub/Sussudio.md')
    assert actual_metadata == expected_metadata


def test_ne_fuit_front_matter():
    expected_metadata = {}
    actual_metadata = _get_front_matter_metadata_from_md_file(
        'tests/vault-stub/lipsum/Ne fuit.md')
    assert actual_metadata == expected_metadata
