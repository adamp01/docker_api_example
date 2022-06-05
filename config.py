import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    """Parent configuration class."""
    DEBUG = True
    TESTING = False
    CSRF_ENABLED = True
    SECRET = os.getenv('SECRET')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')

class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'dev', 'app.db')

class TestConfig(Config):
    TESTING = True
    SECRET = "test"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')

class ProdConfig(Config):
    DEBUG = False

configurations = {
    "dev": DevConfig,
    "test": TestConfig,
    "prod": ProdConfig
}