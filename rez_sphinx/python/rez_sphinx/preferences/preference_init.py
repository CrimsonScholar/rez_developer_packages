"""Some Sphinx files may be generated during :ref:`rez_sphinx init`.

This module is in charge of describing those files. e.g. what the file name is,
its file content, how will Rez / Sphinx refer to that file, etc.

This module is a companion module for :mod:`.preference`.

"""

import os
import textwrap

import schema

from ..core import schema_helper

_BASE_TEXT = textwrap.dedent(
    """\
    This auto-generated file is meant to be written by the developer. Please
    provide anything that could be useful to the reader such as:

    - General Overview
    - A description of who the intended audience is (developers, artists, etc)
    - Tutorials
    - "Cookbook" style tutorials
    - Table Of Contents (toctree) to other Sphinx pages
    """
)
_DEFAULT_TEXT_TEMPLATE = textwrap.dedent(
    """\
    {title}
    {title_suffix}

    {output}"""
)
_TAG_TEMPLATE = textwrap.dedent(
    """\
    ..
        rez_sphinx_help:{title}"""
)


class Entry(object):
    """A description for Sphinx files to generate during :ref:`rez_sphinx init`."""

    def __init__(self, data):
        """Store ``data`` for reference, later.

        Args:
            data (dict[str, object]): All content which describes the current instance.

        """
        super(Entry, self).__init__()

        self._data = data

    @classmethod
    def validate_data(cls, data):
        """Check if ``data`` is valid and, if so, create a new instance.

        Args:
            data (dict[str, object]): All content which describes the current instance.

        Returns:
            :class:`Entry`: The created instance.

        """
        data = _FILE_ENTRY.validate(data)

        return cls(data)

    def _is_tag_enabled(self):
        """If True, add an tag for Rez to generate a :ref:`help` for later, on-build.

        References:
            :ref:`rez_sphinx auto-help`.

        Returns:
            bool:
                If True, this instance is auto-registered by Rez, pre-build. If
                False, this document is still added to Sphinx but it is not
                auto-discovered by Rez nor appended to the user's package
                :ref:`help` attribute during :ref:`rez-build`.

        """
        return self._data.get("add_tag") or True

    def _get_file_name(self):
        """str: Get the "on-disk save name" for this instance (no file extension)."""
        return self._data["file_name"]

    def _get_sphinx_title(self):
        """str: A human-friendly phrase to describe this instance, in documentation."""
        return self._data.get("sphinx_title") or _make_title(self._get_file_name())

    def check_pre_build(self):
        """If True, make sure users have manually filled out the documentation.

        In short, check if the found documentation on-disk matches
        :meth:`Entry.get_default_text`. If it's the same then we know that the
        user hasn't updated the documentation yet.

        Returns:
            bool: If True, run the check prior to Sphinx builds. If False, don't.

        """
        # TODO : Add a unittest for this functionality
        return self._data.get("check_pre_build") or True

    def get_default_text(self):
        """str: The generated Sphinx documentation text body."""
        output = self._data["base_text"]
        title = self._get_sphinx_title()

        if self._is_tag_enabled():
            # TODO : Maybe it'd be cool to add a directive to Sphinx called
            # "rez_sphinx_help" and then somehow query those smartly. Or just do a
            # raw text parse. Either way is probably fine.
            #
            # Reference: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html
            #
            output = _TAG_TEMPLATE.format(title=title) + "\n\n" + output

        return _DEFAULT_TEXT_TEMPLATE.format(
            title=title,
            title_suffix="=" * len(title),
            output=output,
        )

    def get_toctree_line(self):
        """str: The text to add into a Sphinx toctree which refers to this instance."""
        path = self.get_relative_path()
        normalized = os.path.normcase(path)
        name = os.path.splitext(normalized)[0]

        return name.replace("\\", "/")  # Sphinx uses forward slashes in toctrees

    def get_full_file_name(self):
        """str: Get the file name.extension for this instance."""
        # TODO : Get this .rst from the user's configuration settings
        return self._get_file_name() + ".rst"

    def get_relative_path(self):
        """str: Get the path, relative to the documentation root, for this file."""
        return self._data.get("relative_path") or self.get_full_file_name()

    def __repr__(self):
        """str: Create a representation of this instance."""
        return "{self.__class__.__name__}({self._data!r})".format(self=self)


_FILE_ENTRY = schema.Schema(
    {
        "base_text": schema_helper.NON_NULL_STR,
        "file_name": schema_helper.NON_NULL_STR,
        schema.Optional("add_tag", default=True): bool,
        schema.Optional("check_pre_build", default=True): bool,
        schema.Optional("relative_path"): schema_helper.NON_NULL_STR,
        schema.Optional("sphinx_title"): schema_helper.NON_NULL_STR,
    }
)
FILE_ENTRY = schema.Use(Entry.validate_data)
DEFAULT_ENTRIES = (
    Entry.validate_data(
        {
            "base_text": _BASE_TEXT,
            "file_name": "developer_documentation",
            "sphinx_title": "Developer Documentation",
        }
    ),
    Entry.validate_data(
        {
            "base_text": _BASE_TEXT,
            "file_name": "user_documentation",
            "sphinx_title": "User Documentation",
        }
    ),
)


def _make_title(text):
    """Convert some file name into a Human-friendly documentation phrase.

    Args:
        text (str): Some disk file name to convert. e.g. "some_file".

    Returns:
        str: The converted phrase. e.g. "Some File".

    """
    return text.replace("_", " ").title()
