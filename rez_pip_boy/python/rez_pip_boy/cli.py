#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main parser module which creates Rez pip packages."""

import argparse
import functools
import atexit
import shutil
import os
import shlex
import tempfile

from rez import pip
from rez.cli import pip as cli_pip
from rez_utilities import inspection

from .core import builder, exceptions, filer


# TODO : Consider letting the user define their own root path?
def _parse_arguments(text):
    """Get the ``rez-pip`` command arguments + the directory where installed files should go.

    Args:
        text (list[str]): User-provided arguments, split by spaces.

    Returns:
        :class:`argparse.Namespace`: The parsed arguments.

    """
    parser = argparse.ArgumentParser(
        description="A thin wrapper around ``rez-pip`` to transform an installed package back into a source package.",
    )

    parser.add_argument(
        "command",
        help='The raw rez-pip command. e.g. "--install black --python-version=3.6".',
    )

    parser.add_argument(
        "destination",
        help="The absolute folder path on-disk to place this source package (usually a sub-folder in a git repository).",
    )

    parser.add_argument(
        "--make-folders",
        action="store_true",
        help="When included, folders will be automatically created for you. "
        "Otherwise, if a found doesn't exist, the script exits.",
    )

    parser.add_argument(
        "--keep-temporary-files",
        action="store_true",
        help="When included, no files will be automatically cleaned up. "
        "You'll be responsible for deleting them.",
    )

    return parser.parse_args(text)


def _parse_rez_pip_arguments(text):
    """Process `text` as if it was sent to the `rez-pip` command and send the data back.

    Args:
        text (list[str]):
            User-provided arguments, split by spaces. These values
            should be whatever you'd normally pass to rez-pip.
            e.g. "--install black --python-version=3.7"

    Returns:
        :class:`argparse.Namespace`: All of the parsed arguments from `text`.

    """
    temporary_parser = argparse.ArgumentParser(
        description="A temporary parser to communicate with rez-pip's API.",
    )

    cli_pip.setup_parser(temporary_parser)

    return temporary_parser.parse_args(text)


def main(text):
    """Install the user's requested Python package as source Rez packages.

    Args:
        text (list[str]):
            User-provided arguments, split by spaces. These values
            should be whatever you'd normally pass to rez-pip as well as
            the folder where they'd like to put the generated packages.
            e.g. '"--install black --python-version=3.7" --destination /tmp/foo'.

    Raises:
        :class:`.MissingDestination`: If the given directory doesn't exist.

    """
    arguments = _parse_arguments(text)

    if not os.path.isdir(arguments.destination):
        if not arguments.make_folders:
            # TODO : Add unittest for this
            raise exceptions.MissingDestination(
                'Path "{arguments.destination}" is not a directory. Please create it and try again.'
                "".format(arguments=arguments)
            )

        os.makedirs(arguments.destination)

    prefix = tempfile.mkdtemp(prefix="rez_pip_boy_", suffix="_temporary_build_folder")

    if not arguments.keep_temporary_files:
        atexit.register(functools.partial(shutil.rmtree, prefix))

    # TODO : Remove --prefix from `parser`
    # TODO : Make sur that temporary files are cleaned up on-exit
    rez_pip_arguments = _parse_rez_pip_arguments(shlex.split(arguments.command))

    installed_variants, _ = pip.pip_install_package(
        rez_pip_arguments.PACKAGE,
        pip_version=rez_pip_arguments.pip_ver,
        python_version=rez_pip_arguments.py_ver,
        release=rez_pip_arguments.release,
        prefix=prefix,
        extra_args=rez_pip_arguments.extra,
    )

    for installed_variant in installed_variants:
        variant = installed_variant.install(arguments.destination, dry_run=True)

        if variant:
            # TODO : Replace with log
            print('Variant is already installed. Skipping')

            continue

        build_file_name = "rezbuild.py"
        build_command = "python {{root}}/{name}".format(name="rezbuild.py")
        destination_package = installed_variant.install(
            arguments.destination,
            overrides={"build_command": build_command},
        )
        filer.transfer(installed_variant)
        builder.add_build_command(destination_package, build_file_name)
