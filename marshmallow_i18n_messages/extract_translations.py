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

    for validator in MarshmallowIterator().validators():
        extract_error_message(by_msgid, validator, getattr(validator, "default_message", ''), po)
        extract_error_message(by_msgid, validator, getattr(validator, "default_error_message", ''), po)
        extract_error_message(by_msgid, validator, getattr(validator, "message", ''), po)
        for name, attr in validator.__dict__.items():
            if name.startswith("message_"):
                extract_error_message(by_msgid, validator, attr, po)

    for entry in by_msgid.values():
        po.append(entry)
        for idx, occurrence in enumerate(entry.occurrences):
            if isinstance(occurrence[1], str):
                entry.occurrences[idx] = (occurrence[0], int(occurrence[1]))
        entry.occurrences = list(set(entry.occurrences))

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
