import os
import logging

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'

    DATABASE_USER = os.environ.get('DATABASE_USER') or 'your-db-user'
    DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD') or 'your-db-password'
    DATABASE_NAME = os.environ.get('DATABASE_NAME') or 'your-db-name'
    DATABASE_HOST = os.environ.get('DATABASE_HOST') or 'localhost'
    DATABASE_PORT = os.environ.get('DATABASE_PORT') or '5432'

    SQLALCHEMY_DATABASE_URI = f'postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
