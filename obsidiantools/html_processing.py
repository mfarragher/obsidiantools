import html2text
import bleach
from bs4 import BeautifulSoup


def _get_html2text_obj_with_config():
    """Get HTML2Text object with config set."""
    txt_maker = html2text.HTML2Text()

    # some settings to avoid newline problems with links
    txt_maker.ignore_links = False
    txt_maker.body_width = 0
    txt_maker.protect_links = True
    txt_maker.wrap_links = False
    return txt_maker


def _get_source_plaintext_from_html(html):
    """html -> ASCII plaintext, via HTML2Text."""
    txt_maker = _get_html2text_obj_with_config()
    doc = txt_maker.handle(html)
    return doc


def _remove_code(html):
    # exclude 'code' tags from link output:
    soup = BeautifulSoup(html, 'lxml')
    for s in soup.select('code'):
        s.extract()
    html_str = str(soup)
    return html_str


def _remove_del_text(html):
    soup = BeautifulSoup(html, 'lxml')
    for s in soup.select('del'):
        s.extract()
    html_str = str(soup)
    return html_str


def _remove_main_formatting(html, *,
                            tags=['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
    return bleach.clean(html, tags=tags, strip=True)


def _remove_latex(html):
    soup = BeautifulSoup(html, 'lxml')
    for s in soup.select('span', {'class': 'MathJax_Preview'}):
        s.extract()
    html_str = str(soup)
    return html_str


def _get_all_latex_from_html_content(html):
    soup = BeautifulSoup(html, 'html.parser')

    s_content = soup.find_all('span', {'class': 'MathJax_Preview'},
                              text=True)
    latex_found_list = [i.text for i in s_content]
    return latex_found_list
