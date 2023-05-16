# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from configparser import ConfigParser
from datetime import datetime

base_path = os.path.abspath("../..")
sys.path.insert(0, os.path.join(base_path, "src"))

setup_cfg = ConfigParser()
setup_cfg.read(os.path.join(base_path, "setup.cfg"))


# -- Project information -----------------------------------------------------
project = setup_cfg["metadata"]["name"]
copyright = "{}, {}".format(datetime.today().year, setup_cfg["metadata"]["author"])
author = setup_cfg["metadata"]["author"]

# The full version, including alpha/beta/rc tags
version = release = "v" + setup_cfg["metadata"]["version"]


# -- General configuration ---------------------------------------------------
pygments_style = "sphinx"

# warn about everything
nitpicky = True

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.todo",
    "sphinx.ext.githubpages",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
]

source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

linkcheck_ignore = [
    # ignore reference to just the HTTP schemas
    r"^http://$",
    r"^https://$",
    # ignore GH wiki since the check for anchors always fails
    r"https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-\(qBittorrent-4.1\)#",
    r"^http://localhost",
    r"^http://example.com",
]

# -- Options for HTML output -------------------------------------------------
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]

html_theme = "furo"

# sphinx-autoapi
# extensions.append('autoapi.extension')
# autoapi_type = 'python'
# autoapi_dirs = ['../../qbittorrentapi']
# autoapi_options = ['show-inheritance-diagram']
# autoapi_ignore = ['*decorators*', '*exceptions*']

# Add mappings
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "requests": ("https://requests.readthedocs.io/en/latest/", None),
}

suppress_warnings = [
    # Suppress builds warnings while building epub
    "epub.unknown_project_files",
]

# -- Options for spelling -------------------------------------------

# Spelling check needs an additional module that is not installed by default.
# Add it only if spelling check is requested so docs can be generated without it.
if "spelling" in sys.argv:
    extensions.append("sphinxcontrib.spelling")

# Spelling language.
spelling_lang = "en_US"

# Location of word list.
spelling_word_list_filename = "spelling_wordlist"

spelling_ignore_pypi_package_names = False
