#!/bin/bash
uv run python manage.py migrate
sqlite3 /db.sqlite3 'PRAGMA journal_mode=WAL;'
sqlite3 /db.sqlite3 'PRAGMA synchronous=1;'
uv run gunicorn --bind :8000 --workers 2 peervue.wsgi
