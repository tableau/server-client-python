# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


# -- Project information -----------------------------------------------------
# Source - https://stackoverflow.com/a/75396624
# Posted by Jan, modified by community. See post 'Timeline' for change history
# Retrieved 2026-06-19, License - CC BY-SA 4.0

# conf.py

try:
    import tomllib
except ImportError:
    import tomli as tomllib

from pathlib import Path
import importlib.metadata

with open(Path(__file__).parent.parent / "pyproject.toml", "rb") as f:
    toml = tomllib.load(f)

# -- Project information -----------------------------------------------------

project = toml["project"]["name"]
release = importlib.metadata.version(project)
version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------
# -- General configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "autoapi.extension",
]

# -- sphinx-autoapi configuration --------------------------------------------
# Walk the tableauserverclient source tree and generate reference docs for
# every module. A top-level `.. automodule::` would only cover names
# re-exported from `tableauserverclient/__init__.py`, which misses all the
# endpoint classes (Favorites, Workbooks, VirtualConnections, ...) and the
# root helper modules (config, filesys_helpers, namespace, datetime_helpers,
# exponential_backoff). autoapi picks those up.
#
# NOTE: `autoapi_root` also drives the generated tree's on-disk location.
# It is referenced from `.gitignore` (docs/reference/); keep them in sync.
autoapi_dirs = ["../tableauserverclient"]
autoapi_root = "reference"
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
]
autoapi_ignore = ["*/bin/*", "*/_version.py"]
autoapi_add_toctree_entry = True
autoapi_keep_files = False

intersphinx_mapping = {
    "rtd": ("https://docs.readthedocs.io/en/stable/", None),
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []
