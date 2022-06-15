import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'q1w2a3s4'