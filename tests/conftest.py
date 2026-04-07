# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2026 CESNET z.s.p.o.
#
# marshmallow-i18n-messages is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

import gettext
import os
from pathlib import Path

import pytest

from marshmallow_i18n_messages.patch_marshmallow import add_i18n_to_marshmallow


@pytest.fixture(scope="module")
def applied_translations():
    """Apply i18n patches to marshmallow."""
    add_i18n_to_marshmallow()


@pytest.fixture()
def babel_cs():
    """Activate the Czech (``cs``) locale for a single test.

    Binds the ``messages`` text domain to the bundled translations directory
    and installs the Czech gettext catalogue.
    """
    # add czech babel loader
    locale_path = str(
        Path(__file__).parent.parent / "marshmallow_i18n_messages/translations"
    )
    gettext.bindtextdomain("messages", locale_path)
    cs = gettext.translation("messages", locale_path, ["cs"])
    gettext.textdomain("messages")
    os.environ["LANGUAGE"] = "cs"
    cs.install()
