# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2026 CESNET z.s.p.o.
#
# marshmallow-i18n-messages is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""
Integration test for patching a schema not covered by the global patch.

Verifies that :class:`MySchema` (created before
:func:`~marshmallow_i18n_messages.patch_marshmallow.add_i18n_to_marshmallow`
is called) produces English messages before patching and Czech translations
after an explicit :func:`~marshmallow_i18n_messages.patch_marshmallow.enable_i18n`
call.

.. note::

    Deliberately omits the ``applied_translations`` fixture so that
    :class:`MySchema` starts unpatched.  Must run before any test that
    triggers the global patch.
"""

import json

import marshmallow.class_registry
from marshmallow import Schema, ValidationError, fields, validate

from marshmallow_i18n_messages.patch_marshmallow import (
    _lazy_gettext,
    _patch_validation_error,
    enable_i18n,
)


class MySchema(Schema):
    """Minimal test schema with a required string field and a range-validated integer field."""

    name = fields.String(required=True)
    age = fields.Integer(required=True, validate=[validate.Range(min=0, max=150)])


# ---------------------------------------------------------------------------
# Schemas for nested-patching tests
# Three independent nested schemas — one per reference style — so that
# patching via one parent does not silently cover the others.
# ---------------------------------------------------------------------------


class CitySchemaA(Schema):
    """Nested schema used with a direct class reference."""

    name = fields.String(required=True)


class CitySchemaB(Schema):
    """Nested schema used with a string class-registry reference."""

    name = fields.String(required=True)


marshmallow.class_registry.register("CitySchemaB", CitySchemaB)


class CitySchemaC(Schema):
    """Nested schema used with a lambda reference."""

    name = fields.String(required=True)


class NestedByClass(Schema):
    """Parent schema whose nested field is given as a class."""

    city = fields.Nested(CitySchemaA)


class NestedByString(Schema):
    """Parent schema whose nested field is given as a class-registry string."""

    city = fields.Nested("CitySchemaB")


class NestedByLambda(Schema):
    """Parent schema whose nested field is given as a lambda returning a class."""

    city = fields.Nested(lambda: CitySchemaC)


def test_schema_correctly_translated(babel_cs):
    """Verify that :func:`enable_i18n` translates a schema in place.

    Phase 1 asserts English messages before patching; phase 2 asserts Czech
    translations after patching.

    :param babel_cs: Fixture that activates the Czech locale.
    """

    def expect_error(schema_cls, data, expected, msg=""):
        """Load *data* through *schema_cls* and assert the expected validation errors.

        :param schema_cls: Schema class to instantiate and load through.
        :param data: Input dict for ``schema_cls().load()``.
        :param expected: Expected error dict mapping field names to string(s).
        :param msg: Custom assertion failure message.
        :raises AssertionError: If no ValidationError is raised, or messages differ.
        """
        try:
            schema_cls().load(data)
            raise AssertionError("Expected ValidationError, but no error was raised.")
        except ValidationError as e:
            actual = json.loads(json.dumps(e.messages, default=str))
            assert actual == expected, (
                msg or f"Unexpected messages for {schema_cls.__name__}"
            )

    # Phase 1: schema is not yet patched — English messages expected.
    unpatched_msg = "Error messages do not match for untranslated schema. Are we called as the first test?"
    expect_error(
        MySchema,
        {},
        {
            "name": ["Missing data for required field."],
            "age": ["Missing data for required field."],
        },
        unpatched_msg,
    )
    expect_error(
        MySchema,
        {"name": "John"},
        {"age": ["Missing data for required field."]},
        unpatched_msg,
    )
    expect_error(
        MySchema,
        {"name": "John", "age": -1},
        {
            "age": [
                "Must be greater than or equal to 0 and less than or equal to 150.",
            ]
        },
        unpatched_msg,
    )

    # Phase 1b: nested schemas are not yet patched — English messages expected.
    nested_unpatched_msg = (
        "English nested messages expected for {}.  Are we called as the first test?"
    )
    for schema_cls in [NestedByClass, NestedByString, NestedByLambda]:
        expect_error(
            schema_cls,
            {"city": {}},
            {"city": {"name": ["Missing data for required field."]}},
            nested_unpatched_msg.format(schema_cls.__name__),
        )

    # Patch each parent; enable_i18n recurses into the
    # nested field and patches the corresponding CitySchema* class as well.
    for schema_cls in [NestedByClass, NestedByString, NestedByLambda]:
        enable_i18n(schema_cls, _lazy_gettext)

    # Patch MySchema explicitly, as the finalizer would do for InvenioRDM service schemas.
    enable_i18n(MySchema, _lazy_gettext)

    # Wrap lazy strings in lists inside ValidationError before raising translated errors.
    _patch_validation_error()

    # Phase 2: schema is now patched — Czech translations expected.
    expect_error(
        MySchema, {}, {"name": ["Chybí povinné pole."], "age": ["Chybí povinné pole."]}
    )
    expect_error(MySchema, {"name": "John"}, {"age": ["Chybí povinné pole."]})
    expect_error(
        MySchema,
        {"name": "John", "age": -1},
        {"age": ["Musí být větší nebo rovno 0 a menší nebo rovno 150."]},
    )

    # Phase 2b: nested schemas patched — Czech translations expected.
    for schema_cls in [NestedByClass, NestedByString, NestedByLambda]:
        expect_error(
            schema_cls,
            {"city": {}},
            {"city": {"name": ["Chybí povinné pole."]}},
        )
