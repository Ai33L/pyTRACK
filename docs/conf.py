import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'TRACK-pylib'
author = 'Abel Shibu'
copyright = '2026'

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
]

autosummary_generate = True

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = "furo"
html_theme_options = {
    "navigation_with_keys": True,
}
html_static_path = ['_static']
