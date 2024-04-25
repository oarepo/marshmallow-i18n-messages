#!/bin/bash

set -e

python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,tests]'

cd marshmallow_i18n_messages

python extract_translations.py

# for each language, update the messages
pybabel update -l cs -i translations/messages.pot -d translations

pybabel compile -d translations