import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess-i-am-from-iitm-diploma'  # Fallback if not set
    REMEMBER_COOKIE_DURATION = timedelta(days=3)  # Can be adjusted as needed
    
    # Use DATABASE_URL for production databases (e.g., PostgreSQL, MySQL)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'sentimentScout.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids unnecessary overhead for modification tracking
    
    # For Production Logging and Error Handling
    if os.environ.get('FLASK_ENV') == 'production':
        DEBUG = False
        TESTING = False
        LOGGING_LEVEL = 'ERROR'
    else:
        DEBUG = True
        TESTING = True
        LOGGING_LEVEL = 'DEBUG'

    