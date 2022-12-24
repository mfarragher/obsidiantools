import setuptools

with open("README.md", "r", encoding="utf8") as f:
    LONG_DESCRIPTION = f.read()

PROJECT_URLS = {"Source": "https://github.com/mfarragher/obsidiantools"}
INSTALL_REQUIRES = [
    "markdown",
    "pymdown-extensions",
    "html2text",
    "pandas",
    "numpy",
    "networkx",
    "python-frontmatter",
    "beautifulsoup4",
    "bleach",
    "lxml"]

CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Education",
    "Intended Audience :: Science/Research",
    "Topic :: Text Processing :: Markup :: Markdown",
    "Topic :: Office/Business",
    "Topic :: Education",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.9",
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
]

setuptools.setup(
    name="obsidiantools",
    version="0.9.0",
    author="Mark Farragher",
    description="Obsidian Tools - a Python interface for Obsidian.md vaults",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    keywords=["obsidian", "obsidian.md", "knowledge",
              "note-taking", "notes",
              "knowledge management",
              "connected notes"],
    url="https://github.com/mfarragher/obsidiantools",
    project_urls=PROJECT_URLS,
    packages=setuptools.find_packages(exclude=("tests")),
    python_requires=">=3.9",
    install_requires=INSTALL_REQUIRES,
    license="BSD",
    classifiers=CLASSIFIERS
)
