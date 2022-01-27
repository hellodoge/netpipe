import os
from math import ceil

MAX_LEN_OF_SECRET = 32
LEN_OF_SECRET = 12

class Configuration(object):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
