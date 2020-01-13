#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module with persistent class data that carries over from issue checker to issue checker."""

import collections


class Context(collections.MutableMapping):
    """A data object which carries over from checker plugin to checker plugin.

    It's mostly used to keep track of the state of plugins but also can be used
    to do expensive queries and cache the data that's returned. That data
    can then be passed to each checker plugin to use.

    """

    def __init__(self, package, processed_packages=None, vimgrep=False, verbose=False):
        """Keep track of the current Rez package and the user's settings.

        Args:
            package (:class:`rez.packages_.DeveloperPackage`):
                The current Rez package that is being checked.
            processed_packages (list[:class:`rez.packages_.DeveloperPackage`], optional):
                Other packages that have already been processed.
                Default is None.
            vimgrep (bool, optional): Some user input to track
                that specifies if they want row/column data printed.
            verbose (bool, optional): Some user input to track
                that specifies if they want summary information or
                everything to be printed.

        """
        self._data = {
            "package": package,
            "runtime_context": {"processed_packages": processed_packages},
            "user_settings": {"verbose": verbose, "vimgrep": vimgrep},
        }

    def get_data(self):
        """dict[str, object]: The arbitrary user data this instance stored."""
        return dict(self._data)

    def __delitem__(self, key):
        del self._data[key]

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __setitem__(self, key, value):
        self._data[key] = value
