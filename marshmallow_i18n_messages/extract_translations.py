# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2026 CESNET z.s.p.o.
#
# marshmallow-i18n-messages is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""
Translation extraction utilities.

Scans all marshmallow field, schema, and validator classes for error messages
and writes them as translatable strings into a PO/POT file.
"""

from pathlib import Path
from typing import Any

import polib

from marshmallow_i18n_messages.marshmallow_iterator import MarshmallowIterator

extra_translated_strings = [
    "Must be greater than or equal to {min} and less than or equal to {max}.",
    "Must be greater than to {min} and less than or equal to {max}.",
    "Must be greater than or equal to {min} and less than {max}.",
    "Must be greater than to {min} and less than {max}.",
    "Must be less than or equal to {max}.",
    "Must be less than {max}.",
    "Must be greater than or equal to {min}.",
    "Must be greater than {min}.",
]


def extract_translations(outfile: Path) -> None:
    """Scan all marshmallow classes and validators for error messages and write them to *outfile*.

    Existing PO entries are preserved; new ones are appended. The file is saved on completion.

    :param outfile: Path to the PO/POT file to update.
    """
    if not outfile.exists():
        po = polib.POFile()
    else:
        po = polib.pofile(outfile)
    initial_entries = {entry.msgid: entry for entry in po}
    by_msgid = {entry.msgid: entry for entry in po}

    for clz in MarshmallowIterator().classes():
        extract_error_messages_from_dict(
            by_msgid, clz, getattr(clz, "error_messages", {}), po
        )
        extract_error_messages_from_dict(
            by_msgid, clz, getattr(clz, "default_error_messages", {}), po
        )
        extract_error_message(by_msgid, clz, getattr(clz, "default_message", ""), po)
        extract_error_message(
            by_msgid, clz, getattr(clz, "default_error_message", ""), po
        )

    for validator in MarshmallowIterator().validators():
        extract_error_message(
            by_msgid, validator, getattr(validator, "default_message", ""), po
        )
        extract_error_message(
            by_msgid, validator, getattr(validator, "default_error_message", ""), po
        )
        extract_error_message(
            by_msgid, validator, getattr(validator, "message", ""), po
        )
        for name, attr in validator.__dict__.items():
            if name.startswith("message_"):
                extract_error_message(by_msgid, validator, attr, po)

    for msg_id, entry in by_msgid.items():
        occurrences = set()
        for idx, occurrence in enumerate(entry.occurrences):
            if isinstance(occurrence[1], str):
                occurrences.add((occurrence[0], int(occurrence[1])))

        if msg_id not in initial_entries:
            po.append(entry)
        else:
            entry = initial_entries[msg_id]
            for idx, occurrence in enumerate(entry.occurrences):
                if isinstance(occurrence[1], str):
                    occurrences.add((occurrence[0], int(occurrence[1])))

        entry.occurrences = list(sorted(occurrences))

    for msg in extra_translated_strings:
        if msg not in by_msgid:
            by_msgid[msg] = polib.POEntry(msgid=msg, msgstr="")
            po.append(by_msgid[msg])

    po.save(outfile)


def extract_error_messages_from_dict(
    by_msgid: dict[str, polib.POEntry],
    clz: type[Any],
    error_messages: dict[str, Any],
    po: polib.POFile,
) -> None:
    """Extract all error message strings from *error_messages* into the PO file.

    :param by_msgid: Known msgid→POEntry mapping; updated in place.
    :param clz: Owner marshmallow class; used for occurrence tracking.
    :param error_messages: Dict of error key → message string.
    :param po: POFile being built; new entries appended in place.
    """
    for v in error_messages.values():
        extract_error_message(by_msgid, clz, v, po)


def extract_error_message(
    by_msgid: dict[str, polib.POEntry], clz: type[Any], msg: str, po: polib.POFile
) -> None:
    """Ensure a single error message string is present in the PO file.

    Creates a new POEntry if *msg* is not yet tracked. Empty values are ignored.

    :param by_msgid: Known msgid→POEntry mapping; updated in place.
    :param clz: Owner marshmallow class; used for occurrence tracking.
    :param msg: Raw (untranslated) error message string.
    :param po: POFile being built; new entries appended in place.
    """
    if not msg:
        return

    if msg not in by_msgid:
        by_msgid[msg] = polib.POEntry(msgid=msg, msgstr="")
        po.append(by_msgid[msg])

    place = (f"{clz.__module__}.{clz.__name__}.error_messages", 1)
    if place not in by_msgid[msg].occurrences:
        by_msgid[msg].occurrences.append(place)


if __name__ == "__main__":
    extract_translations(Path(__file__).parent / "translations/messages.pot")
