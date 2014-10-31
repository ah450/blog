from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api

app = Flask(__name__)
app.config.from_object('app.config')

api = Api(app)

# SQL Alchemy
db = SQLAlchemy(app)
