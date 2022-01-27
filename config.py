import os
from math import ceil

LEN_OF_SECRET = 8
BASE64_LEN_OF_SECRET = ceil(LEN_OF_SECRET * 8 / 6) + 1


class Configuration(object):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
