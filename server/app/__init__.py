from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

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
