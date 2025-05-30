# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'NASEM Dairy Python'
copyright = '2025, Braeden Fieguth, Dave Innes'
author = 'Braeden Fieguth, Dave Innes'
release = '1.0.2'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_copybutton',
    'sphinx_design',
    'sphinx.ext.intersphinx',
    'sphinx_autodoc_typehints',
    'myst_parser'
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_title = "NASEM Dairy Documentation"
html_css_files = [
    "css/nasem.css",
]
html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']
html_context = {
    "github_user": "CNM-University-of-Guelph",
    "github_repo": "NASEM-Model-Python",
    "github_version": "main",
    "doc_path": "docs/source",
}

html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/CNM-University-of-Guelph/NASEM-Model-Python",
            "icon": "fa-brands fa-github",
        }
    ],
    "navbar_center": ["nasem_navbar.html"]
}
autodoc_preserve_defaults = True