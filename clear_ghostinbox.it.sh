#!/bin/sh

. venv/bin/activate
python email_stats.py
python web_stats.py
deactivate
