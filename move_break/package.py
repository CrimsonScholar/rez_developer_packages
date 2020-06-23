# -*- coding: utf-8 -*-

name = "move_break"

version = "3.2.0"

description = "Change, replace, and move Python imports"

authors = ["Colin Kennedy (ColinKennedy)"]

private_build_requires = ["rez_build_helper-1+<2"]

requires = [
    "parso-0.5+<1",
    "parso_helper-1+<2",
    "rez_python_compatibility-2+<3",
    "six-1.12+<2",
]

variants = [["python-2.7"], ["python-3.6"]]

tests = {
    "black_diff": {
        "command": "black --diff --check package.py python tests",
        "requires": ["black-19.10+<20"],
    },
    "black": {
        "command": "black package.py python tests",
        "requires": ["black-19.10+<20"],
        "run_on": "explicit",
    },
    "coverage": {
        "command": "coverage run --parallel-mode --include=python/* -m unittest discover && coverage combine --append && coverage html",
        "requires": ["coverage"],
        "run_on": "explicit",
    },
    "isort": {
        "command": "isort --recursive package.py python tests",
        "requires": ["isort-4.3+<5"],
        "run_on": "explicit",
    },
    "isort_check": {
        "command": "isort --check-only --diff --recursive package.py python tests",
        "requires": ["isort-4.3+<5"],
    },
    "pydocstyle": {
        # Need to disable D202 for now, until a new pydocstyle version is released
        # Reference: https://github.com/psf/black/issues/1159
        #
        "command": "pydocstyle --ignore=D213,D202,D203,D406,D407 python tests/*",
        "requires": ["pydocstyle-3+<5"],
    },
    "pylint": {
        "command": "pylint --disable=bad-continuation python/move_break tests",
        "requires": ["pylint-1.9+<2"],
    },
    "unittest_python_2": {
        "command": "python -m unittest discover",
        "on_variants": {"type": "requires", "value": ["python-2.7"],},
    },
    "unittest_python_3": {
        "command": "python -m unittest discover",
        "on_variants": {"type": "requires", "value": ["python-3.6"],},
    },
}

build_command = "python -m rez_build_helper --items python"

uuid = "d2d65025-6000-425e-9f8e-5db2b53ee571"


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
