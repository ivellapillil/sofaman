# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'SofaMan'
copyright = '2025, Indukumar Vellapillil-Hari'
author = 'Indukumar Vellapillil-Hari'
release = '0.1'

extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary'
]

templates_path = ['_templates']
exclude_patterns = []


html_theme = 'sphinx_book_theme'
html_static_path = ['_static']
