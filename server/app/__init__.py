# coding=utf-8
"""Initialize `app` module."""

from flask import Flask
from config import config
from .api import api
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import os

engine = None
Base = None
session = None


def init_db(_user,
            _password,
            _db_name,
            connect_fail_callback):
    global engine
    global Base
    global session
    try:
        engine = create_engine('mysql://{}:{}@localhost/{}?charset=utf8'.format(_user,
                                                                   _password,
                                                                   _db_name), echo=True)
        Base = declarative_base()
        Session = sessionmaker(bind=engine)
        session = Session()
    except Exception as err:
        connect_fail_callback(err)


def create_app(config_name):
    """
    Create the app object.
    :param config_name: type of configuration
    :return: the app object
    """
    app = Flask(__name__, instance_relative_config=True)
    # load public config
    app.config.from_object(config[config_name])
    # load private config at instance/config.py
    if os.path.exists('../instance/config.py'):
        app.config.from_pyfile('config.py')

    api.init_app(app)

    return app
