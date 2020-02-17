#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module to change parts of a Rez package."""

import copy

import parso
from parso.python import tree
from rez.vendor.version import version as version_
from rez_industry.core import convention, parso_utility
from rez_utilities import inspection


def _write_package_to_disk(package, version):
    """Update a Rez package on-disk with its new contents.

    Args:
        package (:class:`rez.packages_.DeveloperPackage`):
            Some package on-disk to write out.
        version (str):
            The new semantic version that will be written to-disk.

    """
    with open(package, "r") as handler:
        code = handler.read()

    graph = parso.parse(code)

    try:
        assignment = parso_utility.find_assignment_nodes("version", graph)[-1]
    except IndexError:
        assignment = None

    prefix = " "

    if assignment:
        prefix = assignment.children[0].prefix.strip("\n") or prefix

    node = tree.String('"{version}"'.format(version=version), (0, 0), prefix=prefix)
    graph = convention.insert_or_append(node, graph, assignment, "version")

    with open(package, "w") as handler:
        handler.write(graph.get_code())


def _bump_version(version, minor, absolute=False):
    """Bump the Rez package version minor.

    Args:
        version (:class:`rez.vendor.version.version.Version`):
            The major / minor / patch semantic data that will be bumped.
        minor (int):
            The new value to bump in `version`.
        absolute (bool, optional):
            If True, instead of adding to an existing version number,
            the given version information will be replaced with whatever
            number is given. If False, the value is added, instead.
            Default is False.

    Returns:
        :class:`rez.vendor.version.version.Version`:
            The modified `version` but with a new minor.

    """

    def _bump(version, position, value, absolute=False):
        version = copy.deepcopy(version)

        if position == "minor":
            if absolute:
                new_value = value
            else:
                new_value = int(str(version.minor)) + value

            new_token = version_.NumericToken(str(new_value))
            version.tokens[1] = new_token

            return version

        raise NotImplementedError("Need to support non-minor bumps.")

    positions = set()

    if minor:
        positions.add(("minor", minor))

    for position, value in positions:
        version = _bump(version, position, value, absolute=absolute)

    return version


def bump(package, minor=0, absolute=False):
    """Change the version of `package`.

    Reference:
        https://semver.org

    Args:
        package (:class:`rez.packages_.DeveloperPackage`):
            Some Rez file on-disk that can be changed and re-written.
        minor (int, optional):
            A value to add to the existing version of `package`.
            It can be positive or negative.
        absolute (bool, optional):
            If True, instead of adding to an existing version number,
            the given version information will be replaced with whatever
            number is given. If False, the value is added, instead.
            Default is False.

    Raises:
        ValueError:
            If `minor` is undefined when `absolute` is False or if
            `minor` is negative when `absolute` is True.

    Returns:
        :class:`rez.packages_.DeveloperPackage`: The copy of `package` but with a new version.

    """
    if not absolute and not minor:
        raise ValueError("Nothing to do. No value was given to `minor`.")

    if absolute and minor < 0:
        raise ValueError(
            'Minor "{minor}" cannot be less than zero when absolute is True.'.format(
                minor=minor
            )
        )

    version = package.version or ""

    if not version:
        raise RuntimeError(
            'No version exists so Package "{package}" could not be bumped.'
            "".format(package=package)
        )

    version = _bump_version(version, minor, absolute=absolute)

    _write_package_to_disk(package.filepath, version)
    root = inspection.get_package_root(package)

    return inspection.get_nearest_rez_package(root)
