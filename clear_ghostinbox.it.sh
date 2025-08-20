#!/bin/sh

. venv/bin/activate
python stats.py
python cleanup.py
deactivate
