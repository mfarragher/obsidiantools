import pytest
from pathlib import Path

from obsidiantools.md_utils import (_get_all_wikilinks_from_source_text,
                                    _get_all_embedded_files_from_source_text,
                                    _get_unique_wikilinks_from_source_text,
                                    _get_all_md_link_info_from_source_text,
                                    _get_unique_md_links_from_source_text,
                                    get_unique_md_links,
                                    _get_html_from_md_file,
                                    get_source_text_from_md_file,
                                    _transform_md_file_string_for_tag_parsing,
                                    get_wikilinks,
                                    get_embedded_files,
                                    get_front_matter,
                                    get_tags,
                                    _remove_wikilinks_from_source_text,
                                    _replace_wikilinks_with_their_text,
                                    _replace_md_links_with_their_text,
                                    get_readable_text_from_md_file)
from obsidiantools.html_processing import (_get_all_latex_from_html_content)


@pytest.fixture
def html_wikilinks_stub():
    html = r"""
    <pre># Intro</pre>
    This is a very basic string representation.

    ## Shopping list
    Here is a **[[Shopping list | shopping list]]**:
    - [[Bananas]]: also have these for [[Banana splits]]
    - [[Apples]]
    - [[Flour]]: not a [[Flower | flower]]

    Oh and did I say [[Bananas | BANANAS]]??
    There's no link for [Cherries].  Though there is for [[Durians]].

    ![[Egg.jpg]]

    ## Drinks
    - [[Apples|Freshly squeezed apple juice]]
    - [[Bananas|Banana smoothie]]
    - [[Protein shakes#Protein powder|Vanilla whey protein]]

    ![[Easter egg.png]]
    ![[Egg.jpg | 125]]
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


@pytest.fixture
def txt_wikilink_extraction_stub():
    with open('tests/general/wikilinks_extraction.md') as f:
        in_str = f.read()
    return in_str


@pytest.fixture
def txt_md_link_extraction_stub():
    with open('tests/general/md-links_extraction.md') as f:
        in_str = f.read()
    return in_str


def test_get_all_wikilinks_from_source_text(html_wikilinks_stub):
    actual_results = _get_all_wikilinks_from_source_text(html_wikilinks_stub)
    expected_results = ['Shopping list', 'Bananas', 'Banana splits',
                        'Apples',
                        'Flour', 'Flower',
                        'Bananas',
                        'Durians',
                        'Apples', 'Bananas', 'Protein shakes']

    assert actual_results == expected_results


def test_get_all_wikilinks_from_source_text_keep_aliases(html_wikilinks_stub):
    actual_results = _get_all_wikilinks_from_source_text(
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


def test_get_all_embedded_files_from_source_text(html_wikilinks_stub):
    actual_results = _get_all_embedded_files_from_source_text(
        html_wikilinks_stub)
    expected_results = ['Egg.jpg', 'Easter egg.png', 'Egg.jpg']

    assert actual_results == expected_results


def test_get_all_embedded_files_from_source_text_keep_aliases(
        html_wikilinks_stub):
    actual_results = _get_all_embedded_files_from_source_text(
        html_wikilinks_stub, remove_aliases=False)
    expected_results = ['Egg.jpg', 'Easter egg.png', 'Egg.jpg | 125']

    assert actual_results == expected_results


def test_get_unique_wikilinks_from_html_content(html_wikilinks_stub):
    actual_results = _get_unique_wikilinks_from_source_text(
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
    actual_links = _get_unique_wikilinks_from_source_text(html_wikilinks_stub)
    assert len(set(actual_links)) == len(actual_links)


def test_get_all_md_link_info(txt_md_links_stub):
    expected_links = [('The Times 03/Jan/2009 Chancellor on brink of second bailout for banks',
                       'https://www.thetimes.co.uk/article/chancellor-alistair-darling-on-brink-of-second-bailout-for-banks-n9l382mn62h'),
                      ("Chancellor Alistair Darling on brink of second bailout for banks",
                      'https://www.thetimes.co.uk/article/chancellor-alistair-darling-on-brink-of-second-bailout-for-banks-n9l382mn62h'),
                      ('ADA', 'https://cardano.org/')
                      ]
    actual_links = _get_all_md_link_info_from_source_text(txt_md_links_stub)

    assert actual_links == expected_links


def test_get_unique_md_links_has_order_preserved(txt_md_links_stub):
    expected_links = ['https://www.thetimes.co.uk/article/chancellor-alistair-darling-on-brink-of-second-bailout-for-banks-n9l382mn62h',
                      'https://cardano.org/']
    actual_links = _get_unique_md_links_from_source_text(txt_md_links_stub)

    assert actual_links == expected_links


def test_get_unique_md_links_has_unique_links(txt_md_links_stub):
    actual_links = _get_unique_md_links_from_source_text(txt_md_links_stub)
    assert len(set(actual_links)) == len(actual_links)


def test_pretend_wikilink_not_extracted_from_front_matter(txt_sussudio_stub):
    actual_links = _get_unique_wikilinks_from_source_text(txt_sussudio_stub)
    assert not set(['Polka Party!']).issubset(set(actual_links))


def test_sussudio_front_matter():
    expected_metadata = {'title': 'Sussudio',
                         'artist': 'Phil Collins',
                         'category': 'music',
                         'year': 1985,
                         'url': 'https://www.discogs.com/Phil-Collins-Sussudio/master/106239',
                         'references': [[['American Psycho (film)']], 'Polka Party!'],
                         'chart_peaks': [{'US': 1}, {'UK': 12}]}
    actual_metadata = get_front_matter(
        Path('.') / 'tests/vault-stub/Sussudio.md')
    assert actual_metadata == expected_metadata


def test_ne_fuit_front_matter():
    expected_metadata = {}
    actual_metadata = get_front_matter(
        Path('.') / 'tests/vault-stub/lipsum/Ne fuit.md')
    assert actual_metadata == expected_metadata


def test_front_matter_only_parsing():
    fm_only_files = Path('.').glob('tests/general/frontmatter-only*.md')
    for f in fm_only_files:
        actual_txt = get_source_text_from_md_file(f)
        expected_txt = '\n'
        assert actual_txt == expected_txt


def test_separators_not_front_matter_parsing():
    files = Path('.').glob('tests/general/not-frontmatter*.md')
    for f in files:
        actual_output = get_front_matter(f)
        expected_output = {}
        assert actual_output == expected_output


def test_handle_invalid_front_matter():
    files = Path('.').glob('tests/general/invalid-frontmatter*.md')
    for f in files:
        actual_output = get_front_matter(f)
        expected_output = {}
        assert actual_output == expected_output


def test_front_matter_parse_double_curly():
    fpath = Path('.') / 'tests/general/frontmatter_parse-double-curly.md'

    actual_txt = get_source_text_from_md_file(fpath)
    expected_txt = '\n'
    assert actual_txt == expected_txt


def test_hash_char_parsing_func():
    # '\#' in md file keeps # but stops text from being a tag
    in_str = r"\#hash #tag"
    out_str = _transform_md_file_string_for_tag_parsing(in_str)

    expected_str = r"hash #tag"
    assert out_str == expected_str


def test_sussudio_tags_with_nesting_not_shown():
    actual_tags = get_tags(
        Path('.') / 'tests/vault-stub/Sussudio.md')
    expected_tags = ['y1982', 'y_1982', 'y-1982',
                     'y1982', 'y2000']
    assert actual_tags == expected_tags


def test_sussudio_tags_with_nesting_shown():
    actual_tags = get_tags(
        Path('.') / 'tests/vault-stub/Sussudio.md', show_nested=True)
    expected_tags = ['y1982', 'y_1982', 'y-1982',
                     'y1982/sep', 'y2000/party-over/oops/out-of-time']
    assert actual_tags == expected_tags


def test_embedded_files_alias_scaling():
    actual_embedded_images = get_embedded_files(
        Path('.') / 'tests/general/embedded-images_in-table.md')
    expected_embedded_images = ['test-image_1_before.png',
                                'test-image_1_after.png',
                                'test-image_2_before.png',
                                'test-image_2_after.png']
    assert actual_embedded_images == expected_embedded_images


def test_wikilinks_code_block():
    actual_links = get_wikilinks(
        Path('.') / 'tests/general/wikilinks_exclude-code.md')
    expected_links = []
    assert actual_links == expected_links


def test_latex():
    html = _get_html_from_md_file(Path('.') / 'tests/general/latex.md')
    actual_latex_list = _get_all_latex_from_html_content(html)
    expected_latex_list = ['\\beta', '\\beta',
                           '\\hat{\\beta}_{GEE} \\xrightarrow{D} N(\\beta_{0}, \\Sigma(\\beta_{0}))',
                           '\\beta',
                           'U_{GEE}(\\beta, \\alpha, \\phi) = \\sum_{i=1}^{n} D_{i}^T~V_{i}(\\alpha; \\phi)^{-1} (y_{i} - \\mu_{i}) = 0 \\tag{1} \\label{eq1}',
                           '\\eqref{eq1}']
    assert actual_latex_list == expected_latex_list


def test_remove_wikilinks(txt_wikilink_extraction_stub):
    out_str = _remove_wikilinks_from_source_text(
        txt_wikilink_extraction_stub)

    expected_str = "\n" * 6
    assert out_str == expected_str


def test_wikilinks_as_readable_text(txt_wikilink_extraction_stub):
    out_str = _replace_wikilinks_with_their_text(
        txt_wikilink_extraction_stub)

    expected_str = "\n".join(["A", "B", "see", "dee", "ee", "A"]) + "\n"
    assert out_str == expected_str


def test_md_links_as_readable_text(txt_md_link_extraction_stub):
    out_str = _replace_md_links_with_their_text(
        txt_md_link_extraction_stub)

    expected_str = (
        """Obsidian.md homepage
Github homepage
https://obsidian.md
Github homepage
""")
    assert out_str == expected_str


def test_unique_md_links():
    actual_links = get_unique_md_links(
        Path('.') / 'tests/general/md-links_extraction.md')
    expected_links = ['http://obsidian.md', 'https://github.com']
    assert actual_links == expected_links


def test_readable_text_from_latex_md_stub_default_tags():
    actual_str = get_readable_text_from_md_file(
        Path('.') / 'tests/general/latex.md')
    expected_str = '# Note with LaTeX\n\n## GEE \n\nRegression coefficients estimated through GEE are asymptotically normal: \n\nThe underscore chars above need to be caught through MathJax - capture subscripts rather than emphasis in the parsing.\n\n## GEE estimation\n\nA few eqs more using deeper LaTeX functionality:\n\nEquations for GEE are solved for the regression parameters using: \n\nTaking the expectation of the equation system in ...\n'

    assert actual_str == expected_str


def test_readable_text_from_latex_md_stub_allow_no_tags():
    actual_str = get_readable_text_from_md_file(
        Path('.') / 'tests/general/latex.md', tags=[])
    expected_str = 'Note with LaTeX GEE Regression coefficients estimated through GEE are asymptotically normal: The underscore chars above need to be caught through MathJax - capture subscripts rather than emphasis in the parsing. GEE estimation A few eqs more using deeper LaTeX functionality: Equations for GEE are solved for the regression parameters using: Taking the expectation of the equation system in ...\n'
    assert actual_str == expected_str


def test_readable_text_strikethrough_is_deleted():
    actual_str = get_readable_text_from_md_file(
        Path('.') / 'tests/general/readable-text_all-deleted.md')
    expected_str = '\n'

    assert actual_str == expected_str


def test_readable_text_embedded_files_are_removed():
    actual_str = get_readable_text_from_md_file(
        Path('.') / 'tests/general/embedded-files_in-body.md')
    expected_str = '\n'

    assert actual_str == expected_str


def test_source_text_has_text_after_problematic_latex():
    expected_str = (
        """# Generalised estimating equations

**Generalised estimating equations (GEE)** are ...

## Formulation

Cras imperdiet enim felis, vitae placerat turpis egestas sed. Nulla maximus vel orci ullamcorper blandit.

## Estimation

Problematic equation for html2text: 

...

## Remaining content that isn't LaTeX

Pellentesque rhoncus posuere lacinia. Aenean erat metus, dignissim sed luctus sed, condimentum vitae tortor. Vestibulum tristique nisl id purus volutpat, auctor tempus odio semper. Praesent suscipit, ex id consequat malesuada, elit ex dapibus libero, et pellentesque ipsum arcu et tortor. Nunc sodales vel lectus ac semper.

### Another subheading

Text that shouldn't disappear.
""")

    actual_str = get_source_text_from_md_file(
        Path('.') / 'tests/general/source-text_handle-latex.md',
        remove_math=True)

    assert actual_str == expected_str
