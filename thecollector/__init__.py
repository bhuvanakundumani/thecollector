from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json, os

App = Flask(__name__)


def relative(path="."):
    return os.path.join(App.root_path, path)


with open(relative("env.json")) as f:
    config = json.load(f)

App.config["SECRET_KEY"] = config.get("SECRET_KEY")
App.config["SQLALCHEMY_DATABASE_URI"] = config.get("SQLALCHEMY_DATABASE_URI")

DB = SQLAlchemy(App)

from thecollector import routes
