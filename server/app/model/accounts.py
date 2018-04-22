# coding=utf-8
from .. import *


class Accounts(Base):
    __tablename__ = 'Accounts'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    username = Column(VARCHAR(128), nullable=False, unique=True)
    nickname = Column(VARCHAR(128), nullable=False)
    password = Column(VARCHAR(256), nullable=False)
    email = Column(VARCHAR(128), nullable=False)
    photo = Column(VARCHAR(128), nullable=False)
    authority = Column(Integer)

    def __repr__(self):
        return '<Accounts: username:{} nickname:{} password:{} email:{} photo:{} authority:{}>'.format(self.username,
                                                                                                       self.nickname,
                                                                                                       self.password,
                                                                                                       self.email,
                                                                                                       self.photo,
                                                                                                       self.authority)


def create_table():
    Base.metadata.create_all(engine)


def add_account(_username: str,
                _nickname: str,
                _password: str,
                _email: str,
                _photo: str,
                add_fail_callback: func,
                add_succeed_callback: func):
    """
    :param _username: used to login
    :param _nickname: used to display
    :param _password: used to login
    :param _email: used to find password
    :param _photo: used to display
    :param add_fail_callback: (err)
    :param add_succeed_callback: (Account)
    """
    account = Accounts(username=_username,
                       nickname=_nickname,
                       password=_password,
                       email=_email,
                       photo=_photo)
    try:
        session.add(account)
        session.commit()
        add_succeed_callback(account)
    except Exception as err:
        add_fail_callback(err)


def find_account_by_id(_id: int,
                       find_fail_callback: func,
                       find_succeed_callback: func):
    """
    :param _id:
    :param find_fail_callback: (err)
    :param find_succeed_callback: (Account List)
    """
    try:
        account = session.query(Accounts).filter(Accounts.id == _id)
        session.commit()
        find_succeed_callback(account.all())
    except Exception as err:
        find_fail_callback(err)


def find_accounts_by_authority(_authority: int,
                               find_fail_callback: func,
                               find_succeed_callback: func):
    """

    :param _authority:
    :param find_fail_callback: (err)
    :param find_succeed_callback: (Account list)
    """
    try:
        accounts = session.query(Accounts).filter(Accounts.authority == _authority)
        session.commit()
        find_succeed_callback(accounts.all())
    except Exception as err:
        find_fail_callback(err)


def update_account_by_id(_id: int,
                         _username=None,
                         _nickname=None,
                         _password=None,
                         _email=None,
                         _photo=None,
                         _authority=None,
                         update_fail_callback=None,
                         update_succeed_callback=None):
    """
    :param _id:
    :param _username:
    :param _nickname:
    :param _password:
    :param _email:
    :param _photo:
    :param _authority:
    :param update_fail_callback: (err)
    :param update_succeed_callback: (the count of rows matched as returned by the database’s “row count” feature.)
    """
    try:
        account = session.query(Accounts).filter(Accounts.id == _id).update({
            "username": _username if _username is not None else Accounts.username,
            "nickname": _nickname if _nickname is not None else Accounts.nickname,
            "password": _password if _password is not None else Accounts.password,
            "email": _email if _email is not None else Accounts.email,
            "photo": _photo if _photo is not None else Accounts.photo,
            "_authority": _authority if _authority is not None else Accounts.authority
        })
        session.commit()
        update_succeed_callback(account)
    except Exception as err:
        update_fail_callback(err)


def delete_accound_by_id(_id: int,
                         delete_fail_callback=None,
                         delete_succeed_callback=None):
    """
    :param _id:
    :param delete_fail_callback: (err)
    :param delete_succeed_callback: (the count of rows matched as returned by the database’s “row count” feature.)
    """
    try:
        accounts = session.query(Accounts).filter(Accounts.id == _id).delete()
        session.commit()
        delete_succeed_callback(accounts)
    except Exception as err:
        delete_fail_callback(err)


if __name__ == '__main__':
    init_db('root', '161518324', 'yelda', func)
    create_table()


    def fail_func(err):
        print("[Error] {}".format(err))


    def succeed_func(object):
        print("[Succeed] {}".format(object))


    add_account(_username='yanzexin',
                _nickname='颜泽鑫',
                _password='123455',
                _email='yzx9610@outlook.com',
                _photo='self.png',
                add_fail_callback=fail_func,
                add_succeed_callback=succeed_func)

    add_account(_username='yanzexin',
                _nickname='颜泽鑫',
                _password='123455',
                _email='yzx9610@outlook.com',
                _photo='self.png',
                add_fail_callback=fail_func,
                add_succeed_callback=succeed_func)

    find_account_by_id(_id=1,
                       find_fail_callback=fail_func,
                       find_succeed_callback=succeed_func)

    find_accounts_by_authority(_authority=None,
                               find_fail_callback=fail_func,
                               find_succeed_callback=succeed_func)

    update_account_by_id(_id=15,
                         _username="124",
                         update_fail_callback=fail_func,
                         update_succeed_callback=succeed_func)

    delete_accound_by_id(_id=15,
                         delete_fail_callback=fail_func,
                         delete_succeed_callback=succeed_func)
