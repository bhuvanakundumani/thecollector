from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
import json, os

App = Flask(__name__)
babel = Babel(App)

def relative(path="."):
    return os.path.join(App.root_path, path)

with open(relative("env.json")) as f:
    config = json.load(f)

App.config["SECRET_KEY"] = config.get("SECRET_KEY")
App.config["SQLALCHEMY_DATABASE_URI"] = config.get("SQLALCHEMY_DATABASE_URI")
App.config["BABEL_DEFAULT_LOCALE"] = config.get("BABEL_DEFAULT_LOCALE") # Default language is farsi
App.config["LANGUAGES"] = config.get("LANGUAGES")

DB = SQLAlchemy(App)

from thecollector import routes
