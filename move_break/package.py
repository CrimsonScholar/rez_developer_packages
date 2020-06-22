# -*- coding: utf-8 -*-

name = "move_break"

version = "3.1.0"

description = "Change, replace, and move Python imports"

authors = ["Colin Kennedy (ColinKennedy)"]

private_build_requires = ["rez_build_helper-1+<2"]

requires = [
    "parso-0.5+<1",
    "parso_helper-1+<2",
    "python-2",
    "rez_python_compatibility-2+<3",
    "six-1.12+<2",
]

tests = {
    "black_diff": {
        "command": "rez-env black -- black --diff --check package.py python tests"
    },
    "black": {
        "command": "rez-env black -- black package.py python tests",
        "run_on": "explicit",
    },
    "coverage": {
        "command": "coverage run --parallel-mode --include=python/* -m unittest discover && coverage combine --append && coverage html",
        "requires": ["coverage"],
        "run_on": "explicit",
    },
    "isort": {
        "command": "isort --recursive package.py python tests",
        "requires": ["isort"],
        "run_on": "explicit",
    },
    "isort_check": {
        "command": "isort --check-only --diff --recursive package.py python tests",
        "requires": ["isort"],
    },
    "pydocstyle": {
        # Need to disable D202 for now, until a new pydocstyle version is released
        # Reference: https://github.com/psf/black/issues/1159
        #
        "command": "pydocstyle --ignore=D213,D202,D203,D406,D407 python tests/*",
        "requires": ["pydocstyle-3"],
    },
    "pylint": {
        "command": "pylint --disable=bad-continuation python/move_break tests",
        "requires": ["pylint-1.9+<2"],
    },
    "unittest": "python -m unittest discover",
}

build_command = "python -m rez_build_helper --items python"

uuid = "d2d65025-6000-425e-9f8e-5db2b53ee571"


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
