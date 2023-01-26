"""Configuration file for the Sphinx documentation builder."""

# --- Project information --- #

project = "Wet Synthesis"
copyright = (
    "2023, Multiphase Systems and Chemical Engineering research group,"
    "Politecnico di Torino"
)
author = (
    "Multiphase Systems and Chemical Engineering research group,"
    "Politecnico di Torino"
)

# --- General configuration --- #

extensions = [
    "myst_parser",  # Markdown support
    "sphinx.ext.autodoc",  # API reference
    "sphinx.ext.napoleon",  # Google and NumPy style docstrings support
    "sphinx.ext.viewcode",  # Link to source in API reference
    "sphinx_copybutton",  # Copy button for code blocks
    "nbsphinx",  # Jupyter notebook support
    "IPython.sphinxext.ipython_console_highlighting",  # Syntax highlighting
    "sphinx.ext.autosectionlabel",  # Auto-generate section labels.
    "sphinx_panels",  # Show panels in a grid layout or as drop-downs
]

master_doc = "index"

myst_heading_anchors = 5

suppress_warnings = ["autosectionlabel.*"]
exclude_patterns = ["**.ipynb_checkpoints"]
nbsphinx_allow_errors = False


# --- HTML output options --- #
html_theme = "sphinx_book_theme"
html_favicon = "static/favicon.png"  # Noto Sans open book emoji
html_logo = "static/logo.png"
html_theme_options = {
    "github_url": "https://github.com/simphony/simdome_wet_synthesis",
    "repository_url": "https://github.com/simphony/simdome_wet_synthesis",
    "use_repository_button": True,
    "repository_branch": "main",
    "path_to_docs": "docs",
    "logo_only": True,
    "show_navbar_depth": 1,
}


html_static_path = ["static"]
html_css_files = ["custom.css"]
