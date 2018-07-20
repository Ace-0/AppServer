# coding=utf-8
"""Initialize `app` module."""
import os
from flask import Flask
from werkzeug.security import generate_password_hash
from config import config
import logging
from logging.handlers import RotatingFileHandler
from sqlalchemy.exc import IntegrityError
from .model import init_db

log_file = './log/exception.log'
log_mode = logging.DEBUG


def create_app(config_name):

    """
    Create the app object.
    :param config_name: type of configuration
    :return: the app object
    """
    app = Flask(__name__, instance_relative_config=True)
    # Load public config
    app.config.from_object(config[config_name])
    # Load private config at instance/config.py
    if os.path.exists('instance/config.py'):
        app.config.from_pyfile('config.py')

    # Initialize database
    try:
        init_db(
            app.config['DB_USERNAME'],
            app.config['DB_PASSWORD'],
            app.config['DB_HOST'],
            app.config['DB_PORT'],
            app.config['DB_NAME'],
            app.config['TESTING']
        )
    except Exception as err:
        print(err)
        print('You have to configure your correct MySQL account in server/instance/config.py')
        exit(-1)

    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)

    from .model import accounts
    @login_manager.user_loader
    def load_user(userid):
        """Load user."""
        user = accounts.find_account_by_id(userid)
        if user:
            return user

    @login_manager.unauthorized_handler
    def unauthorized():
        return {'message:': '用户未登录'}, 401  # Don't replace this Magic Number!

    from .api.utils import ConstantCodes
    # Initialize an admin account
    try:
        accounts.add_account(
            app.config['ADMIN_USERNAME'],
            '',
            generate_password_hash(app.config['ADMIN_PASSWORD']),
            '',
            'default.png',
            ConstantCodes.Admin
        )
        print('新建管理员账号')
    except IntegrityError:
        print('管理员账号已存在')

    from .api import api
    api.init_app(app)

    # In case that the log directory has not been created
    log_dir = os.path.dirname(log_file)
    mkdir(log_dir)

    handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)
    fmt = '%(asctime)s - %(filename)s:%(lineno)s - func: [%(name)s] - %(message)s'
    
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)

    app.logger.addHandler(handler)
    app.logger.setLevel(log_mode)

    mkdir(os.path.join(os.environ['HOME'], app.config['CSV_PERSONAL_FOLDER']))
    mkdir(os.path.join(os.environ['HOME'], app.config['CSV_ALL_FOLDER']))

    return app


def mkdir(target_dir):
    """Make directory when the target does not exist."""
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
