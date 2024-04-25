from pathlib import Path

from marshmallow_i18n_messages.marshmallow_iterator import MarshmallowIterator
import polib


def extract_translations(outfile):
    po = polib.pofile(outfile)
    by_msgid = {
        entry.msgid: entry for entry in po
    }

    for clz in MarshmallowIterator().classes():
        extract_error_messages_from_dict(by_msgid, clz, getattr(clz, "error_messages", {}), po)
        extract_error_messages_from_dict(by_msgid, clz, getattr(clz, "default_error_messages", {}), po)
        extract_error_message(by_msgid, clz, getattr(clz, "default_message", ''), po)
        extract_error_message(by_msgid, clz, getattr(clz, "default_error_message", ''), po)

    po.save(outfile)


def extract_error_messages_from_dict(by_msgid, clz, error_messages, po):
    for v in error_messages.values():
        extract_error_message(by_msgid, clz, v, po)


def extract_error_message(by_msgid, clz, msg, po):
    if not msg:
        return

    if msg not in by_msgid:
        by_msgid[msg] = polib.POEntry(msgid=msg, msgstr="")
        po.append(by_msgid[msg])

    place = (
        f"{clz.__module__}.{clz.__name__}.error_messages", 1
    )
    if place not in by_msgid[msg].occurrences:
        by_msgid[msg].occurrences.append(place)


if __name__ == '__main__':
    extract_translations(Path(__file__).parent / 'translations/messages.pot')
