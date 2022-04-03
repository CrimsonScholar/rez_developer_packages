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
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'rez_sphinx'
copyright = '2022, '
author = ''


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.intersphinx',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = 'en'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.


# -- rez-sphinx start --
# -- DO NOT TOUCH --
#
# These lines are needed for rez-sphinx to work
#
from rez_sphinx import api

locals().update(api.bootstrap(locals()))
#
# If you want to add extra user customizations, please feel free to add any
# of them BELOW this line.
#
# -- rez-sphinx end --

import textwrap

html_theme = "sphinx_rtd_theme"
extensions.extend(("sphinx.ext.napoleon", "sphinx.ext.todo"))

# TODO : Consider moving these to my own packages - or some kind of config
intersphinx_mapping.update(
    {
        "https://docs.python.org/3/": None,
        "https://nerdvegas.github.io/rez": None,
        "https://schema.readthedocs.io/en/latest": None,
    }
)

rst_epilog = textwrap.dedent(
    """\
    .. _Configuring Rez: https://github.com/nerdvegas/rez/wiki/Configuring-Rez#overview
    .. _GitHub Pages: https://pages.github.com
    .. _GitHub: https://github.com
    .. _Rez: https://github.com/nerdvegas/rez/wiki
    .. _Sphinx conf.py: https://www.sphinx-doc.org/en/master/usage/configuration.html
    .. _Sphinx: https://www.sphinx-doc.org/en/master
    .. _add_module_names: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-add_module_names
    .. _alabaster: https://alabaster.readthedocs.io/en/latest/
    .. _author: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-author
    .. _build_requires: https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#build_requires
    .. _copyright: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-copyright
    .. _early(): https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#early-binding-functions
    .. _extensions: https://www.sphinx-doc.org/en/master/usage/extensions/index.html#where-to-put-your-own-extensions
    .. _help: https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#help
    .. _index.rst: https://sphinx-tutorial.readthedocs.io/step-1
    .. _intersphinx: https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
    .. _intersphinx_mapping: https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
    .. _late(): https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#late-binding-functions
    .. _link rot: https://en.wikipedia.org/wiki/Link_rot
    .. _master_doc: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-master_doc
    .. _modules.rst: https://stackoverflow.com/questions/62822605/sphinx-modules-rst-warning-document-isnt-included-in-any-toctree
    .. _objects.inv: https://sphobjinv.readthedocs.io/en/latest/syntax.html
    .. _optionvars: https://github.com/nerdvegas/rez/wiki/Configuring-Rez#optionvars
    .. _package help: https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#help
    .. _package.py: https://github.com/nerdvegas/rez/wiki/Package-Commands
    .. _package_preprocess_function: https://github.com/nerdvegas/rez/wiki/Configuring-Rez#package_preprocess_function
    .. _package_preprocess_function: https://github.com/nerdvegas/rez/wiki/Configuring-Rez#package_preprocess_function
    .. _private_build_requires: https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#private_build_requires
    .. _project: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-project
    .. _project_copyright: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-project_copyright
    .. _readthedocs.io: https://docs.readthedocs.io/en/stable/
    .. _release: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-release
    .. _requires: https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#requires
    .. _rez tests attribute: https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#tests
    .. _rez-build: https://github.com/nerdvegas/rez/wiki/Getting-Started#building-your-first-package
    .. _rez-config: https://github.com/nerdvegas/rez/wiki/Command-Line-Tools#rez-config
    .. _rez-depends: https://github.com/nerdvegas/rez/wiki/Command-Line-Tools#rez-depends
    .. _rez-help: https://github.com/nerdvegas/rez/wiki/Command-Line-Tools#rez-help
    .. _rez-pip: https://github.com/nerdvegas/rez/wiki/Command-Line-Tools#rez-pip
    .. _rez-test: https://github.com/nerdvegas/rez/wiki/Command-Line-Tools#rez-test
    .. _rezconfig.py: https://github.com/nerdvegas/rez/blob/fa3fff6f0b7b4b53bbb9baa4357ab42117d06356/src/rez/rezconfig.py
    .. _sphinx theme: https://sphinx-themes.org/
    .. _sphinx-apidoc --private: https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html#cmdoption-sphinx-apidoc-P
    .. _sphinx-apidoc: https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html
    .. _sphinx-build: https://www.sphinx-doc.org/en/master/usage/quickstart.html#running-the-build
    .. _sphinx-quickstart: https://www.sphinx-doc.org/en/master/man/sphinx-quickstart.html
    .. _sphinx-rtd-theme: https://sphinx-rtd-theme.readthedocs.io/en/stable/
    .. _sphinx.ext.autodoc: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
    .. _sphinx.ext.coverage: https://www.sphinx-doc.org/en/master/usage/extensions/coverage.html
    .. _sphinx.ext.intersphinx: https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
    .. _sphinx.ext.viewcode: https://www.sphinx-doc.org/en/master/usage/extensions/viewcode.html
    .. _tests: https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#tests
    .. _toctree: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html
    .. _variants: https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#variants
    .. _version: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-version
    .. _yaml: https://pyyaml.org/wiki/PyYAMLDocumentation
    """
)


# TODO : Add this
    # plugin_path
    # .. package_definition_build_python_paths
