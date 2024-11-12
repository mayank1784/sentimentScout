import os
basedir = os.path.abspath(os.path.dirname(__file__))
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess-i-am-from-iitm-diploma'
    REMEMBER_COOKIE_DURATION = timedelta(days=3)  # Example: 30 days
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'sentimentScout.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
