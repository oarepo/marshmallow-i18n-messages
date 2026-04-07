# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2026 CESNET z.s.p.o.
#
# marshmallow-i18n-messages is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""
Patch marshmallow to support GNU gettext translations.

Replaces hard-coded error messages on marshmallow field, schema, and validator
classes with lazy-gettext equivalents translated at render time.

Call :func:`add_i18n_to_marshmallow` once at application startup to activate
i18n globally.  For schemas that were already imported before that call, use
:func:`enable_i18n` to patch them explicitly.
"""

from .patch_marshmallow import add_i18n_to_marshmallow, enable_i18n

__all__ = ("add_i18n_to_marshmallow", "enable_i18n")
