# coding=utf-8
"""Initialize database connection."""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
session = None
is_testing = False


def init_db(_user,
            _password,
            _db_host,
            _db_port,
            _db_name,
            _is_testing):
    """Initialize database connections and create tables."""

    global session
    db_engine = create_engine(
        'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(
            _user, _password, _db_host, _db_port, _db_name),
        echo=True)
    session = sessionmaker(bind=db_engine)()

    global is_testing
    is_testing = _is_testing

    # Create all tables
    from . import accounts, jobs, images, labels
    Base.metadata.create_all(db_engine)


def handle_db_exception(ex):
    """Roll back session and raise the exception."""
    session.rollback()
    raise ex
