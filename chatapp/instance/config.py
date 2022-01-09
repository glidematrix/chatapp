import os

class Config(object):
    DEBUG = True
    DEVELOPMENT = True
    SECRET_KEY = os.urandom(12)

class ProductionConfig(Config):
    DEVELOPMENT = False
    DEBUG = False