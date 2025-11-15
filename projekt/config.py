import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'DEV'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance/db.db')