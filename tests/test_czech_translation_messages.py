import re

from marshmallow import Schema, fields, ValidationError, validate

MISSING = 'missing'


def load_field(fld_class, value, **kwargs):
    class TS(Schema):
        a = fld_class(**kwargs)
    if value is MISSING:
        return TS().load({})
    return TS().load({'a': value})


def cleanup(x):
    return re.sub(r'\s+', ' ', x.strip())

def check_field(fld_class, value, expected_error, **kwargs):
    try:
        load_field(fld_class, value, **kwargs)
        assert False, 'Expected error'
    except ValidationError as e:
        a_messages = e.messages['a']
        if not isinstance(a_messages, list):
            a_messages = {cleanup(str(a_messages))}
        else:
            a_messages = set(cleanup(str(x)) for x in a_messages)
        if not isinstance(expected_error, list):
            expected_error = {expected_error}
        else:
            expected_error = set(expected_error)
        assert a_messages == expected_error


def test_required(babel_cs):
    check_field(fields.Str, MISSING, 'Chybí povinné pole.', required=True)


def test_null(babel_cs):
    check_field(fields.Str, None, 'Pole nemůže být prázdné (null).')


def test_float_nan(babel_cs):
    check_field(fields.Float, 'nan',
                'Speciální numerické hodnoty (jako nan - není číslo, nekonečno) nejsou povoleny.')


def test_date(babel_cs):
    check_field(fields.DateTime, False, 'Neplatný typ objektu datetime.')


def test_equal(babel_cs):
    check_field(fields.Str, 'a', 'Hodnota musí být rovna "b".',
                validate=[validate.Equal('b')])


def test_range(babel_cs):
    check_field(fields.Int, 1, 'Musí být větší nebo rovno 2 a menší nebo rovno 3.',
                validate=[validate.Range(2, 3)])