"""The entry point for :ref:`rez_sphinx` on the terminal."""

import argparse
import logging
import operator
import os
import shlex

from rez.config import config as config_
from rez.cli import _complete_util
from rez_utilities import finder

from .commands import builder, initer
from .core.suggest import build_display, search_mode, suggestion_mode
from .core import api_builder, exception, path_control, print_format
from .preferences import preference

_LOGGER = logging.getLogger(__name__)


def _add_directory_argument(parser):
    """Make ``parser`` include a positional argument pointing to a file path on-disk.

    Args:
        parser (:class:`argparse.ArgumentParser`): The instance to modify.

    """
    parser.add_argument(
        "directory",
        nargs="?",
        default=os.getcwd(),
        help="The folder to search for a Rez package. "
        "Defaults to the current working directory.",
    )


def _add_remainder_argument(parser):
    """Tell ``parser`` to collect all text into a single namespace parameter.

    Args:
        parser (:class:`argparse.ArgumentParser`):
            The parser to extend with the new parameter.

    """
    remainder = parser.add_argument(
        "remainder",
        nargs="*",
        help=argparse.SUPPRESS,
    )
    remainder.completer = _complete_util.SequencedCompleter(
        "remainder",
        _complete_util.ExecutablesCompleter,
        _complete_util.FilesCompleter(),
    )


def _build(namespace):
    """Build Sphinx documentation, using details from ``namespace``.

    Args:
        namespace (:class:`argparse.Namespace`):
            The parsed user content. It contains all of the necessary
            attributes to generate Sphinx documentation.

    Raises:
        :class:`.UserInputError`:
            If the user passes `sphinx-apidoc`_ arguments but also
            specified that they don't want to build API documentation.

    """
    _split_build_arguments(namespace)

    if namespace.no_api_doc and namespace.api_doc_arguments:
        raise exception.UserInputError(
            'You cannot specify --apidoc-arguments "{namespace.api_doc_arguments}" '
            "while also --no-apidoc.".format(namespace=namespace)
        )

    builder.build(
        namespace.directory,
        api_mode=namespace.api_documentation,
        api_options=namespace.api_doc_arguments,
        no_api_doc=namespace.no_api_doc,
    )


def _build_order(namespace):
    """Show the user the order which documentation must be built.

    Args:
        namespace (:class:`argparse.Namespace`):
            The parsed user content. It contains all of the necessary
            attributes to generate Sphinx documentation.

    """
    normalized = [path_control.expand_path(path) for path in namespace.packages_path]
    raise ValueError("uniquify paths here")

    _LOGGER.info('Searching within "%s" for Rez packages.', normalized)

    searcher = search_mode.get_mode_by_name(namespace.search_mode)
    packages = build_orderer.collect_packages(normalized, searcher)

    if not namespace.include_existing:
        packages = build_orderer.filter_existing_documentation(packages)

    caller = suggestion_mode.get_mode_by_name(namespace.suggestion_mode)
    caller(normalized)


def _check(namespace):
    """Make sure :doc:`configuring_rez_sphinx` are valid, globally and within ``namespace``.

    Args:
        namespace (:class:`argparse.Namespace`):
            The parsed user content. It contains all of the necessary
            attributes to generate Sphinx documentation.

    Raises:
        :class:`.UserInputError`:
            If the user passes `sphinx-apidoc`_ arguments but also
            specified that they don't want to build API documentation.

    """
    directory = os.path.normpath(namespace.directory)
    _LOGGER.debug('Found "%s" directory.', directory)

    preference.validate_base_settings()

    print("All rez_sphinx settings are valid!")


def _init(namespace):
    """Create a Sphinx project, rooted at ``namespace``.

    Args:
        namespace (:class:`argparse.Namespace`):
            The parsed user content. It contains all of the necessary
            attributes to generate Sphinx documentation.

    """
    preference.validate_base_settings()

    _split_init_arguments(namespace)

    directory = os.path.normpath(namespace.directory)
    _LOGGER.debug('Found "%s" directory.', directory)
    package = finder.get_nearest_rez_package(directory)

    if not package:
        raise exception.NoPackageFound(
            'Directory "{directory}" is not in a Rez package. Cannot continue.'.format(
                directory=directory
            )
        )

    _LOGGER.debug('Found "%s" Rez package.', package.name)

    initer.init(package, quick_start_options=namespace.quick_start_arguments)


def _list_default(namespace):
    """Print default :ref:`rez_sphinx` configuration settings.

    The default will show everything. ``--sparse`` will only print the simplest
    arguments.

    """
    if namespace.sparse:
        data = preference.serialize_default_sparse_settings()
    else:
        data = preference.serialize_default_settings()

    caller = print_format.get_format_caller(namespace.format)
    caller(data)


def _list_overrides(namespace):
    """Print any :ref:`rez_sphinx config` settings the user has changed.

    The default will show everything, the default settings along with their
    overrides. ``--sparse`` will only print the overrides and nothing else.

    """
    if not namespace.sparse:
        data = preference.get_base_settings()
    else:
        data = preference.serialize_override_settings()

    caller = print_format.get_format_caller(namespace.format)
    caller(data)


def _set_up_build(sub_parsers):
    """Add :doc:`build_command` CLI parameters.

    Args:
        sub_parsers (:class:`argparse._SubParsersAction`):
            A collection of parsers which the :doc:`build_command` will be
            appended onto.

    """
    build = sub_parsers.add_parser(
        "build", description="Compile Sphinx documentation from a Rez package."
    )
    _add_directory_argument(build)
    choices = sorted(api_builder.MODES, key=operator.attrgetter("label"))
    build.add_argument(
        "--no-apidoc",
        dest="no_api_doc",
        action="store_true",
        help="Disable API .rst file generation.",
    )
    build.add_argument(
        "--apidoc-arguments",
        dest="api_doc_arguments",
        help='Anything you\'d like to send for sphinx-apidoc. e.g. "--private"',
    )
    build.add_argument(
        "--api-documentation",
        choices=[mode.label for mode in choices],
        default=api_builder.FULL_AUTO.label,
        help="When building, API .rst files can be generated for your Python files.\n\n"
        + "\n".join(
            "{mode.label}: {mode.description}".format(mode=mode) for mode in choices
        ),
    )
    build.set_defaults(execute=_build)

    _add_remainder_argument(build)


def _set_up_config(sub_parsers):
    """Add :doc:`config_command` CLI parameters.

    Args:
        sub_parsers (:class:`argparse._SubParsersAction`):
            A collection of parsers which the :doc:`config_command` will be
            appended onto.

    """

    def _add_format_argument(parser):
        """Allow the user to choose :ref:`rez_sphinx config` output (`yaml`_)."""
        parser.add_argument(
            "--format",
            choices=sorted(print_format.CHOICES.keys()),
            default=print_format.PYTHON_FORMAT,
            help="Change the printed output, at will.",
        )

    def _set_up_list_default(inner_parser):
        """Define the parser for :ref:`rez_sphinx config list-default`."""
        list_default = inner_parser.add_parser(
            "list-default",
            description="Show the rez_sphinx's default settings.",
        )
        _add_format_argument(list_default)
        list_default.add_argument(
            "--sparse",
            action="store_true",
            help="If included, the reported config will only show top-level items.",
        )
        list_default.set_defaults(execute=_list_default)

    def _set_up_list_overrides(inner_parser):
        """Define the parser for :ref:`rez_sphinx config list-overrides`."""
        list_overrides = inner_parser.add_parser(
            "list-overrides",
            description="Show non-default rez_sphinx's settings.",
        )
        _add_format_argument(list_overrides)
        list_overrides.add_argument(
            "--sparse",
            action="store_true",
            help="If included, the reported config shows overrides, only.",
        )
        list_overrides.set_defaults(execute=_list_overrides)

    config = sub_parsers.add_parser(
        "config",
        help="All commands related to rez_sphinx configuration settings.",
    )
    # TODO : Figure out how to make sure a subparser is chosen
    inner_parser = config.add_subparsers()

    check = inner_parser.add_parser(
        "check", description="Report if the current rez_sphinx user settings are valid."
    )
    _add_directory_argument(check)
    check.set_defaults(execute=_check)

    _set_up_list_default(inner_parser)
    _set_up_list_overrides(inner_parser)


def _set_up_init(sub_parsers):
    """Add :doc:`init_command` CLI parameters.

    Args:
        sub_parsers (:class:`argparse._SubParsersAction`):
            A collection of parsers which the :doc:`init_command` will be
            appended onto.

    """
    init = sub_parsers.add_parser(
        "init", description="Set up a Sphinx project in a Rez package."
    )
    init.add_argument(
        "--quickstart-arguments",
        dest="quick_start_arguments",
        help="Anything you'd like to send for sphinx-quickstart. "
        'e.g. "--ext-coverage"',
    )
    init.set_defaults(execute=_init)
    _add_directory_argument(init)
    _add_remainder_argument(init)


def _set_up_suggest(sub_parsers):
    """Add :doc:`suggest_command` CLI parameters.

    Args:
        sub_parsers (:class:`argparse._SubParsersAction`):
            A collection of parsers which the :doc:`suggest_command` will be
            appended onto.

    """
    suggest = sub_parsers.add_parser(
        "suggest", description="Check the order which packages should run."
    )
    inner_parsers = suggest.add_subparsers()
    build_order = inner_parsers.add_parser("build-order")
    build_order.add_argument(
        "directories",
        default=config_.packages_path,
        help="The folders to search within for **source** Rez packages.",
    )
    build_order.add_argument(
        "--allow-cyclic",
        action="store_true",
        default=False,
        help="If packages recursively depend on each other, "
        "fail early unless this flag is added.",
    )
    build_order.add_argument(
        "--display-as",
        choices=build_display.CHOICES,
        default=build_display.DEFAULT,
        help='Choose the printed output. '
        '"names" resembles ``rez-depends``. '
        '"directories" points to the path on-disk to the Rez package.'
    )
    build_order.add_argument(
        "--include-existing",
        action="store_true",
        default=False,
        help="Packages which have documentation will be included in the results.",
    )
    build_order.add_argument(
        "--packages-path",
        default=config_.packages_path,
        help="The root Rez install folders to check for installed Rez packages.",
    )
    build_order.add_argument(
        "--search-mode",
        choices=sorted(search_mode.CHOICES.keys()),
        default=search_mode.DEFAULT,
        help='Define how to search for the source Rez packages. '
        '"flat" searches the first folder down. '
        '"recursive" searches everywhere for valid Rez packages.',
    )
    build_order.add_argument(
        "--suggestion-mode",
        choices=sorted(suggestion_mode.CHOICES.keys()),
        default=suggestion_mode.DEFAULT,
        help='Determines the way package dependency tracking runs. '
        'e.g. "config" searches package ``requires``. "guess" is hacky but may cover more cases.',
    )
    build_order.set_defaults(execute=_build_order)


def _split_build_arguments(namespace):
    """Conform ``namespace`` attributes so other functions can use it more easily.

    Warning:
        This function will modify ``namespace`` in-place.

    Args:
        namespace (:class:`argparse.Namespace`):
            The parsed user content. It contains all of the necessary
            attributes to generate Sphinx documentation.

    """
    namespace.api_doc_arguments = shlex.split(namespace.api_doc_arguments or "")

    if not namespace.remainder:
        return

    namespace.api_doc_arguments.extend(namespace.remainder)


def _split_init_arguments(namespace):
    """Conform ``namespace`` attributes so other functions can use it more easily.

    Warning:
        This function will modify ``namespace`` in-place.

    Args:
        namespace (:class:`argparse.Namespace`):
            The parsed user content. It contains all of the necessary
            attributes to generate Sphinx documentation.

    """
    namespace.quick_start_arguments = shlex.split(namespace.quick_start_arguments or "")

    if not namespace.remainder:
        return

    namespace.quick_start_arguments.extend(namespace.remainder)


def main(text):
    """Parse and run ``text``, the user's terminal arguments for :ref:`rez_sphinx`.

    Args:
        text (list[str]):
            The user-provided arguments to run via :ref:`rez_sphinx`.
            This is usually space-separated CLI text like
            ``["init", "--directory", "/path/to/rez/package"]``.

    """
    namespace = parse_arguments(text)
    run(namespace)


def parse_arguments(text):
    """Check the given text for validity and, if valid, parse + return the result.

    Args:
        text (list[str]):
            The user-provided arguments to run via :ref:`rez_sphinx`.
            This is usually space-separated CLI text like
            ``["init", "--directory", "/path/to/rez/package"]``.

    Returns:
        :class:`argparse.Namespace`: The parsed user content.

    """
    parser = argparse.ArgumentParser(
        description="Auto-generate Sphinx documentation for Rez packages.",
    )

    sub_parsers = parser.add_subparsers(dest="commands")
    sub_parsers.required = True

    _set_up_build(sub_parsers)
    _set_up_config(sub_parsers)
    _set_up_init(sub_parsers)
    _set_up_suggest(sub_parsers)

    # TODO : Fix the error where providing no subparser command
    # DOES NOT show the help message
    return parser.parse_args(text)


def run(namespace, modify=True):
    """Run the selected subparser.

    Args:
        namespace (:class:`argparse.Namespace`):
            The parsed user content. It should have a callable method called
            "execute" which takes ``namespace`` as its only argument.
        modify (bool, optional):
            If True, run extra calls directly modifying ``namespace``
            before calling the main execution function. If False, just
            take ``namespace`` directly as-is.

    """
    # TODO : This is weird. Remove it
    if modify and hasattr(namespace, "directory"):
        namespace.directory = path_control.expand_path(namespace.directory)

    namespace.execute(namespace)
