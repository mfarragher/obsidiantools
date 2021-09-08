import pytest


from obsidian_tools.md_utils import (_get_all_wiki_links_from_html_content,
                                     _get_unique_wiki_links,
                                     _get_plaintext_from_html)


@pytest.fixture
def html_stub():
    text = r"""
    <pre><code># Intro
    This is a very basic string representation.

    ## Shopping list
    Here is a **[[Shopping list | shopping list]]**:
    - [[Bananas]]: also have these for [[Banana splits]]
    - [[Apples]]
    - [[Flour]]: not a [[Flower | flower]]

    Oh and did I say [[Bananas | BANANAS]]??
    There's no link for [Cherries].  Though there is for [[Durians]].
    """
    return text


def test_get_all_wiki_links_from_html_content(html_stub):
    actual_results = _get_all_wiki_links_from_html_content(html_stub)
    expected_results = ['Shopping list', 'Bananas', 'Banana splits',
                        'Apples',
                        'Flour', 'Flower',
                        'Bananas',
                        'Durians']

    assert actual_results == expected_results


def test_get_all_wiki_links_from_html_content_keep_aliases(html_stub):
    actual_results = _get_all_wiki_links_from_html_content(
        html_stub, remove_aliases=False)
    expected_results = ['Shopping list | shopping list',
                        'Bananas', 'Banana splits',
                        'Apples',
                        'Flour', 'Flower | flower',
                        'Bananas | BANANAS',
                        'Durians']

    assert actual_results == expected_results


def test_get_unique_wiki_links_from_html_content(html_stub):
    actual_results = _get_unique_wiki_links(
        html_stub, remove_aliases=True)
    expected_results = ['Shopping list',
                        'Bananas', 'Banana splits',
                        'Apples',
                        'Flour', 'Flower',
                        'Durians']

    assert set(actual_results) == set(expected_results)
    assert isinstance(expected_results, list)
