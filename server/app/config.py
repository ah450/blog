import os
# basedir is parent directory
basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../')
DEBUG = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
SECRET_KEY = "If you hide your ignorance, no one will hit you and you'll never learn."
