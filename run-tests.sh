#!/bin/bash

PYTHON=python3

set -e

VENV=".venv"

if test -d $VENV ; then
  rm -rf $VENV
fi

$PYTHON -m venv $VENV
. $VENV/bin/activate
pip install -U setuptools pip wheel

pip install -e ".[tests]"

pytest tests