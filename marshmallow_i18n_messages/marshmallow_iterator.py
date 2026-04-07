# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2026 CESNET z.s.p.o.
#
# marshmallow-i18n-messages is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Iterators for discovering marshmallow classes and validators."""

import inspect


class MarshmallowIterator:
    """Discover marshmallow field/schema and validator classes by walking their modules.

    Lazily imports ``marshmallow`` and ``marshmallow_utils`` on first use.
    """

    def classes(self):
        """Yield every Field and Schema subclass found in ``marshmallow`` and ``marshmallow_utils``."""
        import marshmallow
        import marshmallow_utils.fields
        import marshmallow_utils.schemas

        def is_marshmallow_class(member):
            return issubclass(member, (marshmallow.fields.Field, marshmallow.Schema))

        yield from iter_module(marshmallow, is_marshmallow_class)
        yield from iter_module(marshmallow.fields, is_marshmallow_class)
        yield from iter_module(marshmallow_utils, is_marshmallow_class)
        yield from iter_module(marshmallow_utils.fields, is_marshmallow_class)
        yield from iter_module(marshmallow_utils.schemas, is_marshmallow_class)

    def validators(self):
        """Yield every Validator subclass found in ``marshmallow.validate``."""
        import marshmallow
        import marshmallow.validate

        def is_marshmallow_validator(member):
            return issubclass(member, marshmallow.validate.Validator)

        yield from iter_module(marshmallow.validate, is_marshmallow_validator)


def iter_module(python_module, condition):
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
