"""Automatically add :ref:`rez_sphinx tags <rez_sphinx tag>` to built packages."""

import functools
import io
import os

import six

from ..preferences import preference, preference_init
from . import configuration, constant, sphinx_helper

_DEFAULT_LABEL = "Home Page"
_REZ_HELP_KEY = "help"
_SEEN = set()


def _already_processed(path):
    """Check if ``path`` has already been preprocessed before.

    This function exists to prevent a cyclic loop which may be a bug. See
    reference for details.

    Reference:
        https://github.com/nerdvegas/rez/issues/1239#issuecomment-1061390415

    Args:
        path (str): The directory to a path on-disk pointing to a Rez package.

    Returns:
        bool: If ``path`` was already processed, return True.

    """
    if path in _SEEN:
        return True

    _SEEN.add(path)

    return False


def _expand_help(help_):
    """Convert ``help_`` into a list of lists.

    Args:
        help_ (list[str] or str or NoneType): The found Rez package help, if any.

    Returns:
        list[list[str, str]]: Each found label + documentation entry, if any.

    """
    if not help_:
        return []

    if not isinstance(help_, six.string_types):
        return help_

    return [[_DEFAULT_LABEL, help_]]


def _find_help_labels(root):
    """Auto-find all `package help`_ links, using :ref:`rez_sphinx`.

    It works by querying all Sphinx .rst files at ``root`` (or whatever your
    source extension is), checks each file to a known :ref:`rez_sphinx tag`,
    and then adds those entries directly into the users's `package help`_
    just before it is built.

    Args:
        root (str):
            The root documentation source directory. It should directly contain
            a `Sphinx conf.py`_.

    Returns:
        list[list[str, str]]:
            Each found label + destination entry, if any. If no destination is
            defined, a destination is auto-assigned directly to the
            documentation file.

    """
    tags = []

    # TODO : Consider making this a non-hard-coded value
    extension = ".html"

    for path in _iter_sphinx_source_files(root):
        fallback_name = os.path.splitext(os.path.relpath(path, root))[0]
        fallback_destination = fallback_name + extension

        for label, destination in _get_rez_sphinx_tags(path):
            if not destination:
                destination = fallback_destination
            else:
                destination = sphinx_helper.htmlize_ref(
                    fallback_destination, destination
                )

            entry = [label, os.path.join(constant.ROOT_REPLACEMENT, destination)]

            if entry not in tags:
                tags.append(entry)

    return tags


def _get_rez_sphinx_tags(path):
    """Grab all tags within ``path``.

    Args:
        path (str): The Sphinx ReST file to load and directly parse.

    Returns:
        list[list[str, str]]: Each hard-coded label + "destination", if any.

    """
    with io.open(path, "r", encoding="utf-8") as handler:
        data = handler.read()

    return preference_init.find_tags(data.split("\n"))


def _iter_sphinx_source_files(root):
    """Find every Sphinx ReST file within ``root``.

    Args:
        root (str):
            The root documentation source directory. It should directly contain
            a `Sphinx conf.py`_.

    Yields:
        str: The absolute path to every Sphinx ReST file, if any.

    """
    sphinx = configuration.ConfPy.from_directory(root)
    extension = sphinx.get_source_extension()

    for current_root, _, files in os.walk(root):
        for name in files:
            if name.endswith(extension):
                yield os.path.join(current_root, name)


def _sort(sort_method, original_help, full_help):
    """Sort ``full_help`` based on the other parameters.

    Args:
        sort_method (callable[list[list[str, str]], str]):
            A function that takes ``original_help`` plus some sort term
            to determine where the sort term should be placed.
        original_help (list[list[str, str]]):
            The user's original `package help`_ data, if any.
        full_help (iter[list[str, str]]):
            The user's original `package help`_ data, plus any auto-found
            data, if any.

    Returns:
        list[list[str, str]]: The final, sorted `package help`_.

    """
    sorter = functools.partial(sort_method, original_help)

    return sorted(full_help, key=sorter)


def package_preprocess_function(this, data):  # pylint: disable=unused-argument
    """Replace the `package help`_ in ``data`` with auto-found Sphinx documentation.

    If no :ref:`rez_sphinx tags <rez_sphinx tag>` are found, this function will
    exit early and do nothing.

    Args:
        this (rez.packages.Package):
            The installed (built) Rez package. This package is mostly read-only.
        data (dict[str, object]):
            The contents of ``this``. Changing this instance will have an
            effect on the Rez package which is written to-disk.

    """
    package_source_root = os.getcwd()

    if _already_processed(package_source_root):
        return

    help_ = _expand_help(data.get(_REZ_HELP_KEY))

    source_path = sphinx_helper.find_configuration_path(package_source_root)

    if not source_path:
        return

    source_root = os.path.dirname(source_path)
    new_labels = _find_help_labels(source_root)

    # TODO : Make sure we incorporate user preference here. e.g. if no all
    # duplicates, only add if we prefer auto-generated.
    #
    new_labels.append([constant.REZ_SPHINX_OBJECTS_INV, constant.ROOT_REPLACEMENT])

    original_help = help_
    sort_method = preference.get_sort_method()

    try:
        filter_method = preference.get_filter_method()
    except EnvironmentError:
        full_help = help_ + new_labels
        full_help = _sort(sort_method, original_help, full_help)
    else:
        filtered_original, filtered_labels = filter_method(original_help, new_labels)
        full_help = _sort(
            sort_method, filtered_original, filtered_original + filtered_labels
        )

    data[_REZ_HELP_KEY] = full_help
