import os
from pathlib import Path

import pytest
import gettext

from marshmallow_i18n_messages.patch_marshmallow import add_i18n_to_marshmallow


@pytest.fixture(autouse=True, scope="session")
def applied_translations():
    add_i18n_to_marshmallow()


@pytest.fixture()
def babel_cs():
    # add czech babel loader
    locale_path = str(Path(__file__).parent.parent / 'marshmallow_i18n_messages/translations')
    gettext.bindtextdomain('messages', locale_path)
    cs = gettext.translation('messages', locale_path, ['cs'])
    gettext.textdomain('messages')
    os.environ['LANGUAGE'] = 'cs'
    cs.install()