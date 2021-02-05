from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from os.path import join
import json

app = Flask(__name__)


def relative(path="."):
    return join(app.root_path, path)


with open(relative("env.json")) as f:
    config = json.load(f)

app.config["SECRET_KEY"] = config.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = config.get("SQLALCHEMY_DATABASE_URI")
app.config["BABEL_DEFAULT_LOCALE"] = config.get("BABEL_DEFAULT_LOCALE")
app.config["LANGUAGES"] = config.get("LANGUAGES")

babel = Babel(app)
db = SQLAlchemy(app)

from thecollector import routes
