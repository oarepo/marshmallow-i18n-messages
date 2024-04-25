from gettext import gettext


def test_czech_translations_common(babel_cs):
    assert gettext('Missing data for required field.') == 'Chybí povinné pole.'