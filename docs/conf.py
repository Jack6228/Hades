# Point to the source code directory
import os, sys, datetime
sys.path.insert(0, os.path.abspath('../src'))

year = str(datetime.datetime.now().year)
project = 'Hades'
copyright = f'{year}, Jack Lee Smith et al'
author = 'Jack Lee Smith'
release = '0.9.1'

# General Configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_design',
    'sphinxcontrib.bibtex',
]

# Numerical Figure Numbering
numfig = True
numfig_format = {
    'figure': 'Figure %s:',
    # 'table': 'Table %s:',
    # 'code-block': 'Listing %s:',
}

autosummary_generate = False
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# References
bibtex_bibfiles = ['_static/refs.bib']
# Only show references that were actually cited
bibtex_default_style = 'plain'
bibtex_reference_style = 'author_year'
suppress_warnings = [
    "bibtex.duplicate_label",
    "bibtex.duplicate_citation",
]

# HTML Output Options
html_theme = 'sphinx_rtd_theme'         # Clean, modern look
html_logo = 'assets/LogoWide.png'       # Path to your logo file
html_theme_options = {
    'logo_only': True,                  # Logo only, no text
}
html_static_path = ['_static']
html_css_files = ['hades_style.css']
html_favicon = 'assets/logo.ico'  # Path to your favicon file
