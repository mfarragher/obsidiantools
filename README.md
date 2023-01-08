[![PyPI version](https://badge.fury.io/py/obsidiantools.svg)](https://badge.fury.io/py/obsidiantools) [![PyPI version](https://img.shields.io/pypi/pyversions/obsidiantools.svg)](https://badge.fury.io/py/obsidiantools)
[![Licence](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://github.com/mfarragher/obsidiantools/blob/main/LICENSE) [![Documentation](https://img.shields.io/badge/docs-obsidiantools--demo-orange)](https://github.com/mfarragher/obsidiantools-demo) [![codecov](https://codecov.io/gh/mfarragher/obsidiantools/branch/main/graph/badge.svg)](https://codecov.io/gh/mfarragher/obsidiantools)

# obsidiantools 🪨⚒️
**obsidiantools** is a Python package for getting structured metadata about your [Obsidian.md notes](https://obsidian.md/) and analysing your vault.  Complement your Obsidian workflows by getting metrics and detail about all your notes in one place through the widely-used Python data stack.

It's incredibly easy to explore structured data on your vault through this fluent interface.  This is all the code you need to generate a `vault` object that stores all the data:

```python
import obsidiantools.api as otools

vault = otools.Vault(<VAULT_DIRECTORY>).connect().gather()
```

These are the basics of the method calls:
- `connect()`: connect your notes together in a graph structure and get metadata on links (e.g. wikilinks, backlinks, etc.)  There ais the option to support the inclusion of 'attachment' files in the graph.
- `gather()`: gather the plaintext content from your notes in one place.  This includes the 'source text' that represent how your notes are written.  There are arguments to support what text you want to remove, e.g. remove code.

See some of the **key features** below - all accessible from the `vault` object either through a method or an attribute.

The package is built to support the 'shortest path when possible' option for links.  This should cover the vast majority of vaults that people create.  See the [wiki](https://github.com/mfarragher/obsidiantools/wiki) for more info on what sort of wikilink syntax is not well-supported and how the graph may be slightly different to what you see in the Obsidian app.

## 💡 Key features
This is how **`obsidiantools`** can complement your workflows for note-taking:
- **Access a `networkx` graph of your vault** (`vault.graph`)
    - NetworkX is the main Python library for network analysis, enabling sophisticated analyses of your vault.
    - NetworkX also supports the ability to export your graph to other data formats.
    - When instantiating a `vault`, the analysis can also be filtered on specific subdirectories.
- **Get summary stats about your notes & files, e.g. number of backlinks and wikilinks, in a Pandas dataframe**
    - Get the dataframe via `vault.get_note_metadata()` (notes / md files), `vault.get_media_file_metadata()` (media files that can be embedded in notes) and `vault.get_canvas_file_metadata()` (canvas files).
- **Retrieve detail about your notes' links and metadata as built-in Python types**
    - The main indices of files are `md_file_index`, `media_file_index` and `canvas_file_index` (canvas files).
    - Check whether files included as links in the vault actually exist, via `vault` attributes like `nonexistent_notes`, `nonexistent_media_files` and `nonexistent_canvas_files`.
    - Check whether actual files are isolated in the graph ('orphans'), via `vault` attributes like `isolated_notes`, `isolated_media_files` and `isolated_canvas_files`.
    - You can access all the note & file links in one place, or you can load them for an individual note:
        - e.g. `vault.backlinks_index` for all backlinks in the vault
        - e.g. `vault.get_backlinks(<NOTE>)` for the backlinks of an individual note
    - **md note info:**
        - The various types of links:
            - Wikilinks (incl. header links, links with alt text)
            - Embedded files
            - Backlinks
            - Markdown links
        - Front matter via `vault.get_front_matter(<NOTE>)` or `vault.front_matter_index`
        - Tags via `vault.get_tags(<NOTE>)` or `vault.tags_index`.  Nested tags are supported.
        - LaTeX math via `vault.get_math(<NOTE>)` or `vault.math_index`
        - As long as `gather()` is called:
            - Get source text of note (via `vault.get_source_text(<NOTE>)`).  This tries to represent how a note's text appears in Obsidian's 'source mode'.
            - Get readable text of note (via `vault.get_readable_text(<NOTE>)`).  This tries to reduce note text to minimal markdown formatting, e.g. preserving paragraphs, headers and punctuation.  Only slight processing is needed for various forms of NLP analysis.
    - **canvas file info:**
        - The JSON content of each canvas file is stored as a Python dict in `vault.canvas_content_index`
        - Data to recreate the layout of content in a canvas file via the `vault.canvas_graph_detail_index` dict

Check out the functionality in the demo repo.  Launch the '15 minutes' demo in a virtual machine via Binder:

[![Documentation](https://img.shields.io/badge/docs-obsidiantools--demo-orange)](https://github.com/mfarragher/obsidiantools-demo) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/mfarragher/obsidiantools-demo/HEAD?filepath=obsidiantools%20in%2015%20minutes.ipynb)

There are other API features that try to mirror the Obsidian.md app, for your convenience when working with Python, but they are no substitute for the interactivity of the app!

The text from vault notes goes through this process: markdown → split out front matter from text → HTML → ASCII plaintext.

## ⏲️ Installation
`pip install obsidiantools`

Requires Python 3.9 or higher.

## 🖇️ Dependencies
- Main libraries:
    - `markdown`
    - `pymdown-extensions`
    - `html2text`
    - `pandas`
    - `numpy`
    - `networkx`
- Libraries for front matter and HTML:
    - `python-frontmatter`
    - `beautifulsoup4`
    - `lxml`
    - `bleach`

All of these libraries are needed so that the package can separate note text from front matter in a generalised approach.

## 🏗️ Tests
A small 'dummy vault' vault of lipsum notes is in `tests/vault-stub` (generated with help of the [lorem-markdownum](https://github.com/jaspervdj/lorem-markdownum) tool).  Sense-checking on the API functionality was also done on a personal vault of over 800 notes.

I am not sure how the parsing will work outside of Latin languages - if you have ideas on how that can be supported feel free to suggest a feature or pull request.

## ⚖️ Licence
Modified BSD (3-clause)
