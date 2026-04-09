# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2026 CESNET z.s.p.o.
#
# marshmallow-i18n-messages is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Smoke test verifying that the Czech translation catalogue is loaded correctly."""

from gettext import gettext


def test_czech_translations_common(applied_translations, babel_cs):
    """Verify that a common marshmallow error message is translated into Czech."""
    assert gettext("Missing data for required field.") == "Chybí povinné pole."
