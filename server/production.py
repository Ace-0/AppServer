# coding=utf-8
"""Provide production app to Gunicorn"""

from app import create_app
app = create_app('default')
