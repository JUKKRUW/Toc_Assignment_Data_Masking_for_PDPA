"""Vercel entrypoint.

Vercel looks for a Flask instance named `app` in index.py and runs it as one Vercel Function.
Locally you can still use:  flask --app pdpa_shield.app run --debug
"""
from pdpa_shield.app import create_app

app = create_app()
