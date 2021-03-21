#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main "worker" module for the command-line `move_break` tool."""

import collections
import copy
import itertools
import logging
import re

from . import finder
from .core import attribute_handler, parser

_IMPORT_EXPRESSION = re.compile(r"^import:(?P<namespace>[\w\.]+)$")
_LOGGER = logging.getLogger(__name__)


class _Dotted(object):
    """A wrapper for dot-separated Python namespaces.

    These are **not** just import paths. It can also represent attributes.

    """

    def __init__(self, full_namespace, import_namespace="", aliases=frozenset()):
        """Add namespace-related information to this instance.

        Args:
            full_namespace (str):
                An object's full namespace e.g. "foo.bar.bazz.thing".
            import_namespace (str, optional):
                An object's full namespace e.g. "bazz.thing".
            aliases (set[str], optional):
                The dot-separated extra namespaces which can also be
                used to refer to the base of `import_namespace`. e.g.
                {"something_else.thing"}.

        """
        super(_Dotted, self).__init__()

        self._full_namespace = full_namespace
        self._import_namespace = import_namespace
        self._aliases = aliases or set()

    def _needs_full_namespace(self):
        return "." not in self._import_namespace

    def _get_full_namespace(self):
        """str: The fully qualified dot-separated namespace."""
        return self._full_namespace

    def _get_reference_namespace(self):
        """Get the namespace which would be used, in a module, to refer to the namespace.

        For example, if "foo.bar.bazz" is the full namespace, we expect
        that the user would have a module like

        .. code-block:: python

            from foo import bar

            bar.bazz

        In this example, the reference namespace is "bar.bazz".

        Returns:
            str: The found dot-separated namespace.

        """
        if not self._needs_full_namespace():
            reference = ".".join(self._import_namespace.split(".")[:-1])

            return self._full_namespace[len(reference) + 1 :]

        return self._get_full_namespace()

    def in_import_namespaces(self, namespace):
        """Check if a Python dot-separated namespace can be expressed by this instance.

        Specifically, we only check **imports** within this
        instance. Which includes aliases. We do not check at attribute
        namespace(s).

        Args:
            namespace (str): Some import dot-separated namespace to check for.

        Returns:
            bool: If `namespace is in this instance.

        """
        return namespace in self.get_all_import_namespaces()

    def get_import_references(self):
        """set[str]: Every alias namespace which represents this instance."""
        reference = self._get_reference_namespace() or self._get_full_namespace()

        tail = reference.split(".")[1:]
        dots_to_remove = self._import_namespace.count(".")
        output = {reference}

        for alias in self._aliases:
            if "." in alias:
                alias = ".".join(alias.split(".")[dots_to_remove:])

            output.add(".".join([alias] + tail))

        return output

    def get_alias_tails(self):
        return {alias.split(".")[-1] for alias in self._aliases}

    def get_all_import_namespaces(self):
        """Find all valid **import** namespaces within this instance.

        This includes alias namespaces.

        Returns:
            set[str]: The found namespaces, if any.

        """
        namespace = self.get_import_namespace()
        head = ".".join(namespace.split(".")[:-1])

        if not head:
            return {reference.split(".")[0] for reference in self.get_import_references()}

        output = set()

        for reference in self.get_import_references():
            the_alias = reference.split(".")[0]

            output.add("{head}.{the_alias}".format(head=head, the_alias=the_alias))

        return output

    def get_import_namespace(self):
        """Get the full namespace of what a user might import into a module.

        Basically, it's "everything but the end of the namespace".

        Returns:
            str: The namespace.

        """
        return ".".join(self._get_full_namespace().split(".")[:-1])

    def get_tail(self, alias=False):
        if not alias:
            if not self._needs_full_namespace():
                new_reference = self._get_reference_namespace() or self._get_full_namespace()

                return _get_module_and_attribute(new_reference)

            return self._get_full_namespace()

        if not self._aliases:
            raise RuntimeError('Alias is True but "{self!r}" has no aliases.'.format(self=self))

        if not self._needs_full_namespace():
            new_reference = self._get_reference_namespace() or self._get_full_namespace()

            imports = self.get_import_references()
            alias_imports = self.get_import_references() - {new_reference}

            # Pick one of the aliases at random We do this because
            # any alias should be theoretically "valid", assuming
            # the user didn't do something weird in their module.
            #
            return next(iter(alias_imports))

        # Pick one of the aliases at random We do this because
        # any alias should be theoretically "valid", assuming
        # the user didn't do something weird in their module.
        #
        alias_import = next(iter(self._aliases))

        return ".".join([alias_import] + self._get_full_namespace().split(".")[1:])

    def add_namespace_alias(self, namespace):
        """Add `namespace` as an alternative root namespace for this instance.

        Args:
            namespace (str):
                A dot-separated Python namespace which may or may not
                describe **all** of this instance's full namespace or
                just part of the beginning of the namespace.

        """
        self._aliases.add(namespace)

    def __repr__(self):
        """str: Create an example of how to reproduce this instance."""
        return (
            "{self.__class__.__name__}("
            "{self._full_namespace!r}, "
            "import_namespace={self._import_namespace!r}, "
            "aliases={self._aliases!r}"
            ")".format(self=self)
        )

    def __str__(self):
        """str: Get a shorthand view of this instance."""
        return "<{namespace}>".format(namespace=self._get_full_namespace())


def _attach_aliases(attributes, imports):
    """Add aliased imports as aliased to `attributes`.

    Important:
        `attributes` may be modified in this function.

    Args:
        attributes (list[tuple[:class:`._Dotted`, :class:`._Dotted`]]):
            The "old / new" dot-separated Python namespace pairs. The
            old represents "the namespace that we want to refactor". The
            new is "what it should be changed to".
        imports (iter[:class:`.BaseAdapter`]):
            All Python imports within a module. These imports may or may
            not contain aliases.  If they are aliased, those aliases are
            directly added into `attributes`, if there is a namespace
            match.

    """
    namespaces_and_aliases = collections.defaultdict(set)

    for import_ in imports:
        for key, value in import_.get_node_namespace_mappings().items():
            namespaces_and_aliases[key].add(value)

    for old, _ in attributes:
        namespace = old.get_import_namespace()

        if namespace not in namespaces_and_aliases:
            # It means that `namespace` has no matching import. Skip it.
            continue

        for alias in namespaces_and_aliases[namespace]:
            if alias == namespace:
                # The namespace has no alias. Skip it.
                continue

            old.add_namespace_alias(alias)


def _get_import_match(text):
    """Check if `text` is meant to represent an importable namespace or not.

    If it's not an import namespace, it's assumed that the namespace is
    meant to be referred directly within the module.

    Example:
        >>> _get_import_match("import:foo.bar")  # Result: "foo.bar"
        >>> _get_import_match("foo.bar")  # Result: ""

    Args:
        text (str): Some namespace to check.

    Returns:
        str: A found import namespace, if any.

    """
    match = _IMPORT_EXPRESSION.match(text)

    if not match:
        return ""

    return match.group("namespace")


def _get_module_and_attribute(namespace):
    """Get a module + attribute namespace to describe `namespace`.

    `namespace` could be fully qualified import space, like
    "foo.bar.bazz.thing".  But users would normally import that as
    `from foo.bar import bazz`.  This function gets the tail bit,
    "bazz.thing".

    Args:
        namespace (str): The full, qualified Python dot-separated namespace.

    Returns:
        str: The found module + name.

    """
    parts = namespace.split(".")

    return "{module}.{name}".format(module=parts[-2], name=parts[-1])


def _find_longest_parent(text, references):
    """Find the namespace in `references` that most closely matches `text`.

    Important:
        If the longest parent is found from `references` and that parent
        looks like "some.parent.here", it's assumed that probably it is
        imported into the module as `from some.parent import here`. As
        a result of that, this function will ignore the tail and return
        "some.parent".

    Args:
        text (str):
            A Python dot-separated namespace to check. e.g. "foo.bar".
        references (iter[str]):
            All possible matches. e.g. ["bb.ttt.zz", "foo.bart", "foo"].

    Returns:
        str: The found parent, if any.

    """
    for base in sorted(references, key=len, reverse=True):
        if text.startswith(base):
            return base

    return ""


def _process_namespaces(namespaces):
    """Split `namespaces` by whether or not the namespace is meant to be an import.

    All namespaces which aren't expected as imports are just called
    "attributes". But in truth, the list of attributes could be a class,
    method, function, or attribute. It just refers to any namespace that
    the user might refer to in a module.

    Example:
        >>> _process_namespaces([("import:foo", "import:blah"), ("foo.thing", "blah.another")])
        >>> # Result: ([("foo", "blah")], [("foo.thing", "blah.another")])

    Args:
        namespaces (container[tuple[str, str]]): Each old and new namespace.

    Returns:
        tuple[list[tuple[str, str]], list[tuple[:class:`._Dotted`, :class:`_Dotted`]]]:
            Each found importable namespace and the module's expected
            inner namespaces.

    """
    output = []
    old_explicits = set()
    new_explicits = set()
    unknowns = []
    attributes = []

    for old, new in namespaces:
        old_match = _get_import_match(old)
        new_match = _get_import_match(new)

        if old_match or new_match:
            old_explicits.add(old_match)
            new_explicits.add(new_match)
            output.append((old_match, new_match))

            continue

        unknowns.append((old, new))

    for old, new in unknowns:
        old_match = _find_longest_parent(old, old_explicits)

        if not old_match:
            _LOGGER.warning(
                'Old / New "%s / %s" were skipped because no parent module could be found.',
                old,
                new,
            )

            continue

        new_match = _find_longest_parent(new, new_explicits)

        if old.count(".") > 1:
            old = _Dotted(old, import_namespace=old_match)
        else:
            old = _Dotted(old)

        if new.count(".") > 1:
            new = _Dotted(new, import_namespace=new_match)
        else:
            new = _Dotted(new)

        attributes.append((old, new))

    return output, attributes


def move_imports(  # pylint: disable=too-many-arguments,too-many-locals
    files,
    namespaces,
    partial=False,
    import_types=frozenset(),
    aliases=False,
    continue_on_syntax_error=False,
):
    """Replace the imports of every given file.

    Not every path in `files` will actually be overwritten. Because
    that depends on whether the file includes a namespace import from
    `namespaces`.

    Args:
        files (iter[str]):
            The absolute path to Python files to change.
        namespaces (list[tuple[str, str]]):
            Python dot-separated namespaces that need to be changed.
            Each tuple is the existing namespace and the namespace that
            should replace it.
        partial (bool, optional):
            If True and an import found in `files` is not fully
            described by the user-provided `namespaces`, replace
            the import anyway. Otherwise, the entire import most be
            discoverable before the import is replaced. Default is False.
        import_types (set[str], optional):
            If this is non-empty, only import adapters whose type
            match the names given here will be processed.
            Default: set().
        aliases (bool, optional):
            If True and replacing a namespace would cause Python
            statements to fail, auto-add an import alias to ensure
            backwards compatibility If False, don't add aliases. Default
            is False.
        continue_on_syntax_error (bool, optional):
            If True and a path in `files` is an invalid Python module
            and otherwise cannot be parsed then skip the file and keep
            going. Otherwise, raise an exception. Default is False.

    Raises:
        RuntimeError:
            If `continue_on_syntax_error` is False and a file with a
            syntax error is found.
        ValueError:
            If `namespaces` is empty or if any pair in `namespaces` has
            the same first and second index.

    Returns:
        set[str]: The paths from `files` that were actually overwritten.

    """
    output = set()

    if not namespaces:
        raise ValueError("Namespaces cannot be empty.")

    for old, new in namespaces:
        if old == new:
            raise ValueError(
                'Pair "{old}/{new}" cannot be the same.'.format(old=old, new=new)
            )

    namespaces, attributes = _process_namespaces(namespaces)

    for path in files:
        changed = False

        try:
            graph = finder.get_graph(path)
        except RuntimeError:
            _LOGGER.warning('Couldn\'t parse "%s" as a Python file.', path)

            if not continue_on_syntax_error:
                raise

            continue

        imports = parser.get_imports(
            graph, partial=partial, namespaces=namespaces, aliases=aliases
        )
        module_attributes = copy.deepcopy(attributes)
        _attach_aliases(module_attributes, imports)

        changed_attributes = []

        if partial or attributes:
            changed_attributes = attribute_handler.replace(
                module_attributes, graph, namespaces, aliases=aliases, partial=partial,
            )

        # Every name reference within `graph` that is still in-use even
        # after the attribute substitution.
        #
        used_namespaces = parser.get_used_namespaces(
            [node for nodes in graph.get_used_names().values() for node in nodes],
        )
        imports_to_re_add_if_needed = []

        for statement, (old, new) in itertools.product(imports, namespaces):
            if import_types and statement.get_import_type() not in import_types:
                continue

            if old in statement:
                statement.replace(
                    old,
                    new,
                    namespaces=used_namespaces,
                    attributes=[old_ for old_, _ in module_attributes],
                )
                changed = True
                imports_to_re_add_if_needed.append(old)

        new_imports = parser.get_imports(
            graph, partial=partial, namespaces=namespaces, aliases=aliases
        )

        if changed_attributes:
            attribute_handler.add_imports(
                [new for _, new in namespaces],
                graph,
                old_import_candidates=imports_to_re_add_if_needed,
                existing=new_imports,
            )

            changed = True

        if changed:
            with open(path, "w") as handler:
                handler.write(graph.get_code())

            output.add(path)

    return output
