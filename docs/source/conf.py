import os
import sys
sys.path.insert(0, os.path.abspath('../..'))
from recommonmark.parser import CommonMarkParser

# ... (other existing configurations)

# Add Markdown support
source_parsers = {
    '.md': CommonMarkParser,
}
source_suffix = ['.rst', '.md']

# Add any Sphinx extension module names here, as strings
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'recommonmark',
]

# The theme to use for HTML and HTML Help pages.
html_theme = 'sphinx_rtd_theme'

# ... (other existing configurations)