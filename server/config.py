# coding=utf-8
"""Public configuration module."""


class Config(object):
    """Basic configuration class."""

    DEBUG = False
    TESTING = False
    HOST = '0.0.0.0'


class DevelopmentConfig(Config):
    """Used in normal development environment."""

    DEBUG = False


class TestingConfig(Config):
    """Used in testing environment."""

    DEBUG = True
    TESTING = True


config = {
    'development': DevelopmentConfig,
    'test': TestingConfig,
    'default': Config
}