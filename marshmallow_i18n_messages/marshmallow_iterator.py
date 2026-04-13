# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2026 CESNET z.s.p.o.
#
# marshmallow-i18n-messages is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Iterators for discovering marshmallow classes and validators."""

import inspect
import logging
import pkgutil
from collections.abc import Callable, Generator, Iterator
from types import ModuleType
from typing import Any

log = logging.getLogger("marshmallow_i18n_messages")


class MarshmallowIterator:
    """Discover marshmallow field/schema and validator classes by walking their modules.

    Lazily imports ``marshmallow`` and ``marshmallow_utils`` on first use.
    """

    def classes(self) -> Generator[type[Any], None, None]:
        """Yield every Field and Schema subclass found in ``marshmallow`` and ``marshmallow_utils``."""
        import marshmallow
        import marshmallow_utils

        def is_marshmallow_class(member):
            return issubclass(member, (marshmallow.fields.Field, marshmallow.Schema))

        yield from self.iter_module_tree(marshmallow, is_marshmallow_class)
        yield from self.iter_module_tree(marshmallow_utils, is_marshmallow_class)

    def validators(self) -> Generator[type[Any], None, None]:
        """Yield every Validator subclass found in ``marshmallow.validate``."""
        import marshmallow
        import marshmallow.validate
        import marshmallow_utils

        def is_marshmallow_validator(member):
            return issubclass(member, marshmallow.validate.Validator)

        yield from self.iter_module_tree(marshmallow, is_marshmallow_validator)
        yield from self.iter_module_tree(marshmallow_utils, is_marshmallow_validator)

    def iter_module_tree(
        self, root_module: ModuleType, predicate: Callable[[Any], bool]
    ) -> Generator[Any, None, None]:
        """Recursively yield items from *root_module* and submodules that satisfy *predicate*."""
        import importlib

        yield from iter_module(root_module, predicate)

        # Discover all submodules and yield items from them
        for modinfo in pkgutil.walk_packages(
            root_module.__path__, root_module.__name__ + "."
        ):
            try:
                yield from iter_module(importlib.import_module(modinfo.name), predicate)
            except Exception:
                log.error("Can not iterate module %s", modinfo.name)


def iter_module(
    python_module: ModuleType, condition: Callable[[type[Any]], bool]
) -> Iterator[type[Any]]:
    """Recursively yield classes from *python_module* that satisfy *condition*.

    Descends into sub-modules whose ``__name__`` starts with
    ``python_module.__name__``.  Dunder names are skipped.

    :param python_module: Module to inspect.
    :param condition: Callable returning ``True`` for classes to yield.
    """
    for name in dir(python_module):
        if name.startswith("__"):
            continue
        member = getattr(python_module, name)
        if inspect.ismodule(member):
            if member.__name__.startswith(python_module.__name__):
                yield from iter_module(member, condition)
        elif inspect.isclass(member):
            full_name = f"{member.__module__}.{member.__name__}"
            if full_name.startswith(python_module.__name__) and condition(member):
                yield member
