name = "rez_sphinx"

version = "1.0.0"

description = "Automate the initialization and building of Sphinx documentation."

help = [["README", "README.md"]]

private_build_requires = ["rez_build_helper-1+<2"]

@late()
def requires():
    from rez.config import config

    output = [
        "PyYAML-5.4+<7",
        "Sphinx-1.8+<4",
        "python-2.7+<3.8",
        "rez-2.42+<3",
        "rez_bump-1.5+<2",
        "rez_industry-3.1+<4",  # TODO : Kill this awful dependency later
        "rez_python_compatibility-2.8+<3",
        "rez_utilities-2.6+<3",
        "schema-0.7+<1",
        "six-1.15+<2",
    ]

    for request in config.optionvars.get("rez_sphinx", dict()).get("extra_requires", []):
        if request in output:
            continue

        output.append(request)

    return output


variants = [["python-2", "backports.functools_lru_cache-1.6+<2"], ["python-3"]]

build_command = "python -m rez_build_helper --items bin python"

tests = {
    "black": {
        "command": "black python tests",
        "requires": ["black-22+<23"],
        "run_on": "explicit",
    },
    "black_diff": {
        "command": "black --diff --check python tests",
        "requires": ["black-22+<23"],
    },
    "build_documentation": "rez_sphinx build",
    "isort": {
        "command": "isort python tests",
        "requires": ["isort-5.9+<6"],
        "run_on": "explicit",
    },
    "isort_check": {
        "command": "isort --check-only --diff --recursive python tests",
        "requires": ["isort-5.9+<6"],
    },
    "pydocstyle": {
        # Need to disable D417 for now, until a new pydocstyle version is released
        #
        # Reference: https://github.com/PyCQA/pydocstyle/blob/master/docs/release_notes.rst
        #
        "command": "pydocstyle --ignore=D213,D203,D406,D407,D417 python tests/*",
        "requires": ["pydocstyle-6.1+<7"],
    },
    # TODO : Add configuration files for these changes. And isort and pydocstyle
    "pylint": {
        "command": "pylint --disable=use-dict-literal,use-list-literal,bad-continuation python/rez_sphinx tests",
        "requires": ["pylint-2.12+<3"],
    },
    "unittest_python_2": {
        "command": "python -m unittest discover",
        "requires": ["python-2"],
    },
    "unittest_python_3": {
        "command": "python -m unittest discover",
        "requires": ["python-3"],
    },
}

uuid = "bea3e936-644e-4e82-b0f1-4bec37db58cc"


def commands():
    import os

    env.PATH.append(os.path.join(root, "bin"))
    env.PYTHONPATH.append(os.path.join(root, "python"))
