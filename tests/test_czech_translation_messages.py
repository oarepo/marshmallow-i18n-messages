# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2026 CESNET z.s.p.o.
#
# marshmallow-i18n-messages is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for Czech translations of marshmallow field and validator error messages."""

import re

from marshmallow import Schema, ValidationError, fields, validate

MISSING = "missing"


def load_field(fld_class, value, **kwargs):
    """Load *value* through a temporary schema with a single field ``a`` of type *fld_class*.

    :param fld_class: The marshmallow field class to instantiate.
    :param value: Value to deserialise, or :data:`MISSING` to omit the key.
    :param kwargs: Additional keyword arguments passed to *fld_class*.
    :raises marshmallow.ValidationError: If validation fails.
    """

    class TS(Schema):
        a = fld_class(**kwargs)

    if value == MISSING:
        return TS().load({})
    return TS().load({"a": value})


def cleanup(x):
    """Strip and collapse internal whitespace runs to a single space."""
    return re.sub(r"\s+", " ", x.strip())


def check_field(fld_class, value, expected_error, **kwargs):
    """Assert that loading *value* into *fld_class* raises *expected_error*.

    :param fld_class: The marshmallow field class to test.
    :param value: Value to load, or :data:`MISSING` to omit the key.
    :param expected_error: Expected translated error string or list of strings.
    :param kwargs: Additional keyword arguments forwarded to *fld_class*.
    """
    try:
        load_field(fld_class, value, **kwargs)
        assert False, "Expected error"
    except ValidationError as e:
        a_messages = e.messages["a"]
        if not isinstance(a_messages, list):
            a_messages = {cleanup(str(a_messages))}
        else:
            a_messages = set(cleanup(str(x)) for x in a_messages)
        if not isinstance(expected_error, list):
            expected_error = {expected_error}
        else:
            expected_error = set(expected_error)
        assert a_messages == expected_error


def test_required(applied_translations, babel_cs):
    """Verify Czech error message for a missing required ``Str`` field."""
    check_field(fields.Str, MISSING, "Chybí povinné pole.", required=True)


def test_null(applied_translations, babel_cs):
    """Verify Czech error message when ``None`` is passed to a ``Str`` field."""
    check_field(fields.Str, None, "Pole nesmí být prázdné (null).")


def test_float_nan(applied_translations, babel_cs):
    """Verify Czech error message when ``"nan"`` is passed to a ``Float`` field."""
    check_field(
        fields.Float,
        "nan",
        "Speciální číselné hodnoty (NaN nebo nekonečno) nejsou povoleny.",
    )


def test_date(applied_translations, babel_cs):
    """Verify Czech error message when an invalid type is passed to a ``DateTime`` field."""
    check_field(fields.DateTime, False, "Neplatný objekt typu datetime.")


def test_equal(applied_translations, babel_cs):
    """Verify Czech error message when the ``Equal`` validator rejects a value."""
    check_field(
        fields.Str, "a", 'Hodnota musí být rovna "b".', validate=[validate.Equal("b")]
    )


def test_range(applied_translations, babel_cs):
    """Verify Czech error message when the ``Range`` validator rejects a value."""
    check_field(
        fields.Int,
        1,
        "Musí být větší nebo rovno 2 a menší nebo rovno 3.",
        validate=[validate.Range(2, 3)],
    )
