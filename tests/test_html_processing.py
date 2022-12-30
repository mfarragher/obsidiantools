from pathlib import Path

from obsidiantools.html_processing import (_remove_code,
                                           _remove_del_text,
                                           _remove_latex)
from obsidiantools.md_utils import _get_html_from_md_file

# NOTE: run the tests from the project dir.
WKD = Path().cwd()


def test_remove_code():
    fpath = Path('.') / 'tests/general/wikilinks_exclude-code.md'

    actual_html = _get_html_from_md_file(fpath)
    actual_proc_html = _remove_code(actual_html)
    actual_html_string = str(actual_proc_html)

    expected_html_string = """<html><body><h1>code-avoid-wikilink</h1>
<div class="highlight"><pre><span></span></pre></div>
<p></p>
<p>The snippets above are R code: they should not give a wikilink.</p></body></html>"""
    assert actual_html_string == expected_html_string


def test_remove_del_text():
    fpath = Path('.') / 'tests/general/readable-text_all-deleted.md'

    actual_html = _get_html_from_md_file(fpath)
    actual_proc_html = _remove_del_text(actual_html)
    actual_html_string = str(actual_proc_html)

    expected_html_string = """<html><body><p></p></body></html>"""
    assert actual_html_string == expected_html_string


def test_remove_latex_in_note_with_highly_formatted_text():
    fpath = Path('.') / 'tests/general/latex.md'

    actual_html = _get_html_from_md_file(fpath)
    actual_proc_html = _remove_latex(actual_html)
    actual_html_string = str(actual_proc_html)

    expected_html_string = """<html><body><h1>Note with LaTeX</h1>
<h2>GEE </h2>
<p>Regression coefficients  estimated through GEE are <strong>asymptotically normal</strong>:
</p>
<p><em>The underscore chars above need to be caught through MathJax - capture subscripts rather than emphasis in the <code>markdown</code> parsing.</em></p>
<h2>GEE estimation</h2>
<p><em>A few eqs more using deeper LaTeX functionality:</em></p>
<p>Equations for GEE are solved for the regression parameters  using:
</p>
<p>Taking the expectation of the equation system in  <em>...</em></p></body></html>"""
    assert actual_html_string == expected_html_string
