# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2026 CESNET z.s.p.o.
#
# marshmallow-i18n-messages is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""
Core patching logic for marshmallow i18n support.

Replaces hard-coded error-message strings on marshmallow field, schema, and
validator classes with lazy-gettext equivalents translated at render time.

Call :func:`add_i18n_to_marshmallow` once at startup.  For schemas created
before that call use :func:`enable_i18n` instead.
"""

import inspect
import logging
from collections.abc import Callable
from gettext import gettext
from threading import Lock
from typing import Any

from marshmallow import Schema, ValidationError, fields
from speaklater import make_lazy_gettext

from marshmallow_i18n_messages.marshmallow_iterator import MarshmallowIterator

log = logging.getLogger("marshmallow_i18n_messages")


def _lazy_gettext(*args: Any, **kwargs: Any) -> Any:
    """Return a lazy-translated string using the currently active ``gettext`` function.

    Translation is deferred until render time, so the locale may change between
    field definition and error production.

    :returns: A lazy string proxy that translates on demand.
    """
    return make_lazy_gettext(lambda: gettext)(*args, **kwargs)


add_i18n_to_marshmallow_called = False
add_i18n_to_marshmallow_lock = Lock()


def add_i18n_to_marshmallow(gettext_impl: Callable[..., Any] = _lazy_gettext) -> None:
    """Patch all marshmallow classes and validators to use i18n error messages.

    Idempotent and thread-safe.  Also monkey-patches
    :meth:`marshmallow.fields.Field.make_error` so that format-string
    placeholders in translated messages are resolved correctly.

    :param gettext_impl: Callable used to wrap raw message strings.  Defaults
        to :func:`_lazy_gettext`.
    """
    with add_i18n_to_marshmallow_lock:
        global add_i18n_to_marshmallow_called
        if add_i18n_to_marshmallow_called:
            return

        # Patch all marshmallow classes and validators
        _patch_all_classes(gettext_impl)

        # Patch ValidationError.__init__ to support lazy strings
        _patch_validation_error()

        # monkey patch make error
        _patch_make_error()

        add_i18n_to_marshmallow_called = True


def _patch_make_error() -> None:
    """
    Monkey-patches :meth:`fields.Field.make_error` to support lazy strings.
    """
    previous_make_error = fields.Field.make_error

    def apply_kwargs(inst: Any, param: Any, **kwargs: Any) -> Any:
        if isinstance(param, dict):
            for k, v in list(param.items()):
                param[k] = apply_kwargs(inst, v, **kwargs)
            return param
        elif isinstance(param, list):
            for i, v in enumerate(param):
                param[i] = apply_kwargs(inst, v, **kwargs)
            return param
        return str(param).format(**kwargs)

    def make_error_i18n(self: fields.Field, key: str, **kwargs) -> ValidationError:
        error = previous_make_error(self, key, **kwargs)
        error.messages = apply_kwargs(self, error.messages, **kwargs)
        return error

    fields.Field.make_error = make_error_i18n  # type: ignore


def _patch_validation_error() -> None:
    """Patch :class:`~marshmallow.exceptions.ValidationError` to correctly wrap lazy strings into lists."""
    if getattr(ValidationError, "__init_replaced__", False):
        return
    setattr(ValidationError, "__init_replaced__", True)
    old_init = ValidationError.__init__

    def new_init(self: ValidationError, messages: Any = None, **kwargs: Any) -> None:
        if not isinstance(messages, (dict, list)):
            messages = [messages]
        old_init(self, messages, **kwargs)  # type: ignore

    ValidationError.__init__ = new_init  # type: ignore


def _patch_all_classes(gettext_impl: Callable[..., Any]) -> None:
    """Patch every marshmallow field/schema and validator class found by :class:`~marshmallow_i18n_messages.marshmallow_iterator.MarshmallowIterator`.

    :param gettext_impl: Callable used to wrap raw message strings.
    """
    _visited = set()
    for clz in MarshmallowIterator().classes():
        enable_i18n(clz, gettext_impl, _visited=_visited)
    for clz in MarshmallowIterator().validators():
        _patch_validator(clz, gettext_impl, _visited=_visited)


def _translate_dict(clz: Any, prop_name: str, gettext_impl: Callable[..., Any]) -> None:
    """Translate the values of a dictionary property on *clz* using *gettext_impl*."""
    d = getattr(clz, prop_name, {})
    for k, v in d.items():
        if isinstance(v, str):
            d[k] = gettext_impl(v)


def _translate_prop(clz: Any, prop_name: str, gettext_impl: Callable[..., Any]) -> None:
    """Translate a single property on *clz* using *gettext_impl*."""
    value = getattr(clz, prop_name, None)
    if isinstance(value, str):
        setattr(clz, prop_name, gettext_impl(value))


def enable_i18n(
    clz: type[Schema] | type[fields.Field] | Schema | fields.Field,
    gettext_impl: Callable[..., Any] = _lazy_gettext,
    _visited: set | None = None,
) -> None:
    """Replace static error-message strings on *clz* with lazy-gettext wrappers.

    Handles ``error_messages``, ``default_error_messages``, ``default_message``,
    ``default_error_message``, and any nested ``validators`` attribute.

    :param clz: Marshmallow Schema or Field class/instance to patch.
    :param gettext_impl: Callable used to wrap raw message strings.
    """
    log.debug("Translating schema/validator class/instance %s", clz)

    if _visited is None:
        _visited = set()

    if id(clz) in _visited:
        return
    _visited.add(id(clz))

    # If the class is a subclass of Schema or Field, patch its parent classes as well
    if inspect.isclass(clz):
        for m in clz.mro()[1:]:
            if issubclass(m, (Schema, fields.Field)):
                enable_i18n(m, gettext_impl, _visited=_visited)
    # if the object is a Field instance, patch its class as well
    elif isinstance(clz, fields.Field):
        enable_i18n(type(clz), gettext_impl, _visited=_visited)
    # if the object is a Schema instance, patch its class as well
    elif isinstance(clz, Schema):
        enable_i18n(type(clz), gettext_impl, _visited=_visited)

    # translate error message dictionaries (error_messages are on instances, default_error_messages are on classes)
    _translate_dict(clz, "error_messages", gettext_impl)
    _translate_dict(clz, "default_error_messages", gettext_impl)

    # translate default message properties
    _translate_prop(clz, "default_message", gettext_impl)
    _translate_prop(clz, "default_error_message", gettext_impl)

    if validators := getattr(clz, "validators", None):
        _patch_validators(validators, gettext_impl, _visited=_visited)

    if declared_fields := getattr(clz, "_declared_fields", None):
        _patch_fields(declared_fields, gettext_impl, _visited=_visited)


def _patch_validators(
    validators: Any, gettext_impl: Callable[..., Any], *, _visited: set | None
) -> None:
    """Patch a validator or list of validators in place.

    :param validators: A single validator class/instance or a list thereof.
    :param gettext_impl: Callable used to wrap raw message strings.
    """
    if not validators:
        return
    if not isinstance(validators, list):
        validators = [validators]
    for validator in validators:
        _patch_validator(validator, gettext_impl, _visited=_visited)


def _patch_validator(
    validator: Any, gettext_impl: Callable[..., Any], *, _visited: set | None
) -> None:
    """Patch a single marshmallow validator instance or class for i18n.

    In addition to :func:`enable_i18n` handling, also wraps ``message`` and
    any attribute whose name starts with ``message_``.

    .. note::

        Validators like :class:`~marshmallow.validate.Range` compose their
        message in ``__init__``, so the POT file must also include those
        composed strings — see
        :data:`~marshmallow_i18n_messages.extract_translations.extra_translated_strings`.

    :param validator: Marshmallow validator class or instance to patch.
    :param gettext_impl: Callable used to wrap raw message strings.
    """
    enable_i18n(validator, gettext_impl, _visited=_visited)
    # special handling for validator properties
    _translate_prop(validator, "message", gettext_impl)
    for name, attr in inspect.getmembers(validator):
        if name.startswith("message_"):
            if isinstance(attr, str):
                setattr(validator, name, gettext_impl(attr))
    # note: for some validators, such as Range validator,
    # the message is processed in the constructor and will look like:
    # "Must be greater than or equal to {min} and less than or equal to {max}."
    # and not the original "Must be {min_op} {{min}} and {max_op} {{max}}."
    # The po files must contain these translated strings as well.


def _patch_fields(
    declared_fields: dict[str, fields.Field],
    gettext_impl: Callable[..., Any],
    _visited: set,
) -> None:
    """Patch fields of a marshmallow schema class or instance."""

    # for each field, patch the field itself and if it's a nested field, patch the nested schema
    for name, fld in declared_fields.items():
        enable_i18n(fld, gettext_impl, _visited=_visited)
        if isinstance(fld, fields.Nested):
            try:
                # fld.nested may be a string reference ("self", dotted name, …);
                # fld.schema resolves it to an actual Schema instance.
                nested = fld.schema
                enable_i18n(nested, gettext_impl, _visited)
            except Exception:
                log.error(
                    "Could not resolve nested schema for field %s, skipping",
                    fld,
                )
