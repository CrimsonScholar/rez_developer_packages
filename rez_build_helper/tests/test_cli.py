#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Make sure :mod:`rez_build_helper` works as expected."""

import atexit
import functools
import os
import shutil
import tempfile
import textwrap
import unittest

from rez_build_helper import filer
from python_compatibility.testing import common
from rez_utilities import creator, finder


class Cli(unittest.TestCase):
    """Make sure the basic CLI functions work as-expected."""

    def test_empty(self):
        """Build even if the package just contains just a package.py file."""
        directory = tempfile.mkdtemp(prefix="rez_build_helper_Cli_test_empty_")
        atexit.register(functools.partial(shutil.rmtree, directory))

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper"

                    def commands():
                        pass
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(prefix="rez_build_helper_Cli_test_copy_install_folder_")
        atexit.register(functools.partial(shutil.rmtree, destination))

        creator.build(package, destination, quiet=True)
        install_location = os.path.join(destination, "some_package", "1.0.0")

        self.assertTrue(os.path.isfile(os.path.join(install_location, "package.py")))

    def test_copy(self):
        """Copy folder(s) for the build Rez package."""
        directory = tempfile.mkdtemp(prefix="rez_build_helper_Cli_test_copy_")
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {"python": {
                "some_thing": {
                    "__init__.py": None,
                    "some_module.py": None,
                    "inner_folder": {
                        "__init__.py": None,
                        "inner_module.py": None,
                    }
                }
            }},
            directory,
        )

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper --items python"

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python"))
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(prefix="rez_build_helper_Cli_test_copy_install_folder_")
        atexit.register(functools.partial(shutil.rmtree, destination))

        creator.build(package, destination, quiet=True)
        install_location = os.path.join(destination, "some_package", "1.0.0")

        self.assertTrue(os.path.isdir(os.path.join(install_location, "python")))
        self.assertFalse(os.path.islink(os.path.join(install_location, "python")))
        self.assertTrue(os.path.isdir(os.path.join(install_location, "python", "some_thing")))
        self.assertTrue(os.path.isdir(os.path.join(install_location, "python", "some_thing", "inner_folder")))
        self.assertTrue(os.path.isfile(os.path.join(install_location, "python", "some_thing", "__init__.py")))
        self.assertTrue(os.path.isfile(os.path.join(install_location, "python", "some_thing", "some_module.py")))
        self.assertTrue(os.path.isfile(os.path.join(install_location, "python", "some_thing", "inner_folder", "__init__.py")))
        self.assertTrue(os.path.isfile(os.path.join(install_location, "python", "some_thing", "inner_folder", "inner_module.py")))

    def test_symlink(self):
        """Create symlinks for each specified folder."""
        directory = tempfile.mkdtemp(prefix="rez_build_helper_Cli_test_symlink_")
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {"python": {
                "some_thing": {
                    "__init__.py": None,
                    "some_module.py": None,
                    "inner_folder": {
                        "__init__.py": None,
                        "inner_module.py": None,
                    }
                }
            }},
            directory,
        )

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper --items python --symlink"

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python"))
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(prefix="rez_build_helper_Cli_test_symlink_install_folder_")
        atexit.register(functools.partial(shutil.rmtree, destination))

        creator.build(package, destination, quiet=True)
        install_location = os.path.join(destination, "some_package", "1.0.0")

        self.assertTrue(os.path.isdir(os.path.join(install_location, "python")))
        self.assertTrue(os.path.islink(os.path.join(install_location, "python")))
        self.assertTrue(os.path.isdir(os.path.join(install_location, "python", "some_thing")))
        self.assertTrue(os.path.isdir(os.path.join(install_location, "python", "some_thing", "inner_folder")))
        self.assertTrue(os.path.isfile(os.path.join(install_location, "python", "some_thing", "__init__.py")))
        self.assertTrue(os.path.isfile(os.path.join(install_location, "python", "some_thing", "some_module.py")))
        self.assertTrue(os.path.isfile(os.path.join(install_location, "python", "some_thing", "inner_folder", "__init__.py")))
        self.assertTrue(os.path.isfile(os.path.join(install_location, "python", "some_thing", "inner_folder", "inner_module.py")))


class Egg(unittest.TestCase):
    """Make sure .egg generation and symlinking works as expected."""

    def test_single(self):
        """Create a collapsed .egg file for a Python folder."""
        directory = tempfile.mkdtemp(prefix="rez_build_helper_Egg_test_single_")
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {"python": {
                "some_thing": {
                    "__init__.py": None,
                    "some_module.py": None,
                    "inner_folder": {
                        "__init__.py": None,
                        "inner_module.py": None,
                    }
                }
            }},
            directory,
        )

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper --egg python"

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python.egg"))
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(prefix="rez_build_helper_Egg_test_single_install_folder_")
        atexit.register(functools.partial(shutil.rmtree, destination))

        creator.build(package, destination, quiet=True)
        install_location = os.path.join(destination, "some_package", "1.0.0")

        self.assertTrue(os.path.isfile(os.path.join(install_location, "python.egg")))
        self.assertFalse(os.path.islink(os.path.join(install_location, "python.egg")))
        self.assertFalse(os.path.isdir(os.path.join(install_location, "python")))
        self.assertFalse(os.path.isdir(os.path.join(install_location, "python", "some_thing")))
        self.assertFalse(os.path.isdir(os.path.join(install_location, "python", "some_thing", "inner_folder")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "python", "some_thing", "__init__.py")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "python", "some_thing", "some_module.py")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "python", "some_thing", "inner_folder", "__init__.py")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "python", "some_thing", "inner_folder", "inner_module.py")))

    def test_single_symlink(self):
        """Create a symlink for (what would have normally been) an .egg file."""
        directory = tempfile.mkdtemp(prefix="rez_build_helper_Egg_test_single_")
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {"python": {
                "some_thing": {
                    "__init__.py": None,
                    "some_module.py": None,
                    "inner_folder": {
                        "__init__.py": None,
                        "inner_module.py": None,
                    }
                }
            }},
            directory,
        )

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper --egg python --symlink"

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python.egg"))
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(prefix="rez_build_helper_Egg_test_single_install_folder_")
        atexit.register(functools.partial(shutil.rmtree, destination))

        creator.build(package, destination, quiet=True)
        install_location = os.path.join(destination, "some_package", "1.0.0")

        self.assertTrue(os.path.islink(os.path.join(install_location, "python.egg")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "python.egg")))
        self.assertFalse(os.path.isdir(os.path.join(install_location, "python")))
        self.assertFalse(os.path.isdir(os.path.join(install_location, "python", "some_thing")))
        self.assertFalse(os.path.isdir(os.path.join(install_location, "python", "some_thing", "inner_folder")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "python", "some_thing", "__init__.py")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "python", "some_thing", "some_module.py")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "python", "some_thing", "inner_folder", "__init__.py")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "python", "some_thing", "inner_folder", "inner_module.py")))

    def test_multiple(self):
        """Create more than one collapsed egg files for a Python folder."""
        directory = tempfile.mkdtemp(prefix="rez_build_helper_Egg_test_multiple_")
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {"python": {
                "some_thing": {
                    "__init__.py": None,
                    "some_module.py": None,
                    "inner_folder": {
                        "__init__.py": None,
                        "inner_module.py": None,
                    }
                }
            },
            "another": {
                "stuff": {
                    "__init__.py": None,
                    "some_module.py": None,
                    "inner_folder": {
                        "__init__.py": None,
                        "inner_module.py": None,
                    }
                }
            }
             },
            directory,
        )

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper --egg python another"

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python.egg"))
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(prefix="rez_build_helper_Egg_test_single_install_folder_")
        atexit.register(functools.partial(shutil.rmtree, destination))

        creator.build(package, destination, quiet=True)
        install_location = os.path.join(destination, "some_package", "1.0.0")

        self.assertFalse(os.path.islink(os.path.join(install_location, "python.egg")))
        self.assertTrue(os.path.isfile(os.path.join(install_location, "python.egg")))
        self.assertFalse(os.path.isdir(os.path.join(install_location, "python")))
        self.assertFalse(os.path.isdir(os.path.join(install_location, "python", "some_thing")))
        self.assertFalse(os.path.isdir(os.path.join(install_location, "python", "some_thing", "inner_folder")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "python", "some_thing", "__init__.py")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "python", "some_thing", "some_module.py")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "python", "some_thing", "inner_folder", "__init__.py")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "python", "some_thing", "inner_folder", "inner_module.py")))

        self.assertFalse(os.path.islink(os.path.join(install_location, "another.egg")))
        self.assertTrue(os.path.isfile(os.path.join(install_location, "another.egg")))
        self.assertFalse(os.path.isdir(os.path.join(install_location, "another")))
        self.assertFalse(os.path.isdir(os.path.join(install_location, "another", "stuff")))
        self.assertFalse(os.path.isdir(os.path.join(install_location, "another", "stuff", "inner_folder")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "another", "stuff", "__init__.py")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "another", "stuff", "some_module.py")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "another", "stuff", "inner_folder", "__init__.py")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "another", "stuff", "inner_folder", "inner_module.py")))

    def test_multiple_symlink(self):
        """Create symlinks to represent egg files for Python folders."""
        directory = tempfile.mkdtemp(prefix="rez_build_helper_Egg_test_multiple_")
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {"python": {
                "some_thing": {
                    "__init__.py": None,
                    "some_module.py": None,
                    "inner_folder": {
                        "__init__.py": None,
                        "inner_module.py": None,
                    }
                }
            },
            "another": {
                "stuff": {
                    "__init__.py": None,
                    "some_module.py": None,
                    "inner_folder": {
                        "__init__.py": None,
                        "inner_module.py": None,
                    }
                }
            }
             },
            directory,
        )

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper --egg python another --symlink"

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python.egg"))
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(prefix="rez_build_helper_Egg_test_single_install_folder_")
        atexit.register(functools.partial(shutil.rmtree, destination))

        creator.build(package, destination, quiet=True)
        install_location = os.path.join(destination, "some_package", "1.0.0")

        self.assertTrue(os.path.islink(os.path.join(install_location, "python.egg")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "python.egg")))
        self.assertFalse(os.path.isdir(os.path.join(install_location, "python")))
        self.assertFalse(os.path.isdir(os.path.join(install_location, "python", "some_thing")))
        self.assertFalse(os.path.isdir(os.path.join(install_location, "python", "some_thing", "inner_folder")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "python", "some_thing", "__init__.py")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "python", "some_thing", "some_module.py")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "python", "some_thing", "inner_folder", "__init__.py")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "python", "some_thing", "inner_folder", "inner_module.py")))

        self.assertTrue(os.path.islink(os.path.join(install_location, "another.egg")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "another.egg")))
        self.assertFalse(os.path.isdir(os.path.join(install_location, "another")))
        self.assertFalse(os.path.isdir(os.path.join(install_location, "another", "stuff")))
        self.assertFalse(os.path.isdir(os.path.join(install_location, "another", "stuff", "inner_folder")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "another", "stuff", "__init__.py")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "another", "stuff", "some_module.py")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "another", "stuff", "inner_folder", "__init__.py")))
        self.assertFalse(os.path.isfile(os.path.join(install_location, "another", "stuff", "inner_folder", "inner_module.py")))

    def test_invalid(self):
        """Disallow non-root folders for .egg generation."""
        pass
