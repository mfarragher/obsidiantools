[![PyPI version](https://badge.fury.io/py/obsidiantools.svg)](https://badge.fury.io/py/obsidiantools) [![PyPI version](https://img.shields.io/pypi/pyversions/obsidiantools.svg)](https://badge.fury.io/py/obsidiantools)
[![Licence](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://github.com/mfarragher/obsidiantools/blob/main/LICENSE) [![Documentation](https://img.shields.io/badge/docs-obsidiantools--demo-orange)](https://github.com/mfarragher/obsidiantools-demo) [![codecov](https://codecov.io/gh/mfarragher/obsidiantools/branch/main/graph/badge.svg)](https://codecov.io/gh/mfarragher/obsidiantools)

# obsidiantools 🪨⚒️
**obsidiantools** is a Python package for getting structured metadata about your [Obsidian.md notes](https://obsidian.md/) and analysing your vault.  Complement your Obsidian workflows by getting metrics and detail about all your notes in one place through the widely-used Python data stack.

It's incredibly easy to explore structured data on your vault through this fluent interface.  This is all the code you need to generate a `vault` object that stores the key data:

```python
import obsidiantools.api as otools

vault = otools.Vault(<VAULT_DIRECTORY>).connect()
```

See some of the **key features** below - all accessible from the `vault` object either through a method or an attribute.

As this package relies upon note (file)names, it is only recommended for use on vaults where wikilinks are not formatted as paths and where note names are unique.  This should cover the vast majority of vaults that people create.

## 💡 Key features
This is how **`obsidiantools`** can complement your workflows for note-taking:
- **Access a `networkx` graph of your vault** (`vault.graph`)
    - NetworkX is the main Python library for network analysis, enabling sophisticated analyses of your vault.
    - NetworkX also supports the ability to export your graph to other data formats.
- **Get summary stats about your notes, e.g. number of backlinks and wikilinks, in a Pandas dataframe**
    - Get the dataframe via `vault.get_note_metadata()`
- **Retrieve detail about your notes' links and metadata as built-in Python types**
    - The various types of links:
        - Wikilinks (incl. header links, links with alt text)
        - Embedded files
        - Backlinks
        - Markdown links
    - You can access all the links in one place, or you can load them for an individual note:
        - e.g. `vault.backlinks_index` for all backlinks in the vault
        - e.g. `vault.get_backlinks(<NOTE>)` for the backlinks of an individual note
    - Front matter via `vault.get_front_matter(<NOTE>)` or `vault.front_matter_index`
    - Check which notes are isolated (`vault.isolated_notes`)
    - Check which notes do not exist as files yet (`vault.nonexistent_notes`)

Check out the functionality in the demo repo.  Launch the '10 minutes' demo in a virtual machine via Binder:

[![Documentation](https://img.shields.io/badge/docs-obsidiantools--demo-orange)](https://github.com/mfarragher/obsidiantools-demo) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/mfarragher/obsidiantools-demo/HEAD?filepath=obsidiantools%20in%2010%20minutes.ipynb)

There are other API features that try to mirror the Obsidian.md app, for your convenience when working with Python, but they are no substitute for the interactivity of the app!

The text from vault notes goes through this process: markdown → HTML → process front matter → ASCII plaintext.  The functions for text processing are in the `md_utils` module so they can be used to get text, e.g. for use in NLP analysis.

## ⏲️ Installation
``pip install obsidiantools``

Developed for Python 3.9 but may still work on lower versions.

As of Sep 2021, NetworkX requires Python 3.7 or higher (similar for Pandas too) so that is recommended as a minimum.

## 🖇️ Dependencies
- Main libraries:
    - markdown
    - html2text
    - pandas
    - numpy
    - networkx
- Libraries for parsing front matter:
    - python-frontmatter
    - beautifulsoup4
    - lxml

All of these libraries are needed so that the package can separate note text from front matter in a generalised approach.

## 🏗️ Tests
A small 'dummy vault' vault of lipsum notes is in `tests/vault-stub` (generated with help of the [lorem-markdownum](https://github.com/jaspervdj/lorem-markdownum) tool).  Sense-checking on the API functionality was also done on a personal vault of up to 100 notes.

I am not sure how the parsing will work outside of Latin languages - if you have ideas on how that can be supported feel free to suggest a feature or pull request.

## ⚖️ Licence
Modified BSD (3-clause)
