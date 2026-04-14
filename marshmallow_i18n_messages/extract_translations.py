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
    # Range validator modifies error messages in constructor, so we need
    # to translate these prepared messages and not the original error messages.
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

    The output PO file is overwritten.

    :param outfile: Path to the PO/POT file to write the translations to.
    """
    po = polib.POFile()
    by_msgid: dict[str, polib.POEntry] = {}

    for clz in MarshmallowIterator().classes():
        extract_error_messages_from_dict(
            by_msgid, clz, getattr(clz, "error_messages", {})
        )
        extract_error_messages_from_dict(
            by_msgid, clz, getattr(clz, "default_error_messages", {})
        )
        extract_error_message(by_msgid, clz, getattr(clz, "default_message", ""))
        extract_error_message(by_msgid, clz, getattr(clz, "default_error_message", ""))

    for validator in MarshmallowIterator().validators():
        extract_error_message(
            by_msgid, validator, getattr(validator, "default_message", "")
        )
        extract_error_message(
            by_msgid, validator, getattr(validator, "default_error_message", "")
        )
        extract_error_message(by_msgid, validator, getattr(validator, "message", ""))
        for name, attr in validator.__dict__.items():
            if name.startswith("message_"):
                extract_error_message(by_msgid, validator, attr)

    for _msg_id, entry in sorted(by_msgid.items()):
        po.append(entry)

    for msg in extra_translated_strings:
        if msg not in by_msgid:
            po.append(polib.POEntry(msgid=msg, msgstr=""))

    po.save(outfile)


def extract_error_messages_from_dict(
    by_msgid: dict[str, polib.POEntry],
    clz: type[Any],
    error_messages: dict[str, Any],
) -> None:
    """Extract all error message strings from *error_messages* into the PO file.

    :param by_msgid: Known msgid→POEntry mapping; updated in place.
    :param clz: Owner marshmallow class; used for occurrence tracking.
    :param error_messages: Dict of error key → message string.
    :param po: POFile being built; new entries appended in place.
    """
    for v in error_messages.values():
        extract_error_message(by_msgid, clz, v)


def extract_error_message(
    by_msgid: dict[str, polib.POEntry], clz: type[Any], msg: str
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
    msg = str(msg)
    if msg not in by_msgid:
        by_msgid[msg] = polib.POEntry(msgid=msg, msgstr="")

    place = (f"{clz.__module__}.{clz.__name__}.error_messages", 1)
    if place not in by_msgid[msg].occurrences:
        by_msgid[msg].occurrences.append(place)


if __name__ == "__main__":
    extract_translations(Path(__file__).parent / "translations/messages.pot")
