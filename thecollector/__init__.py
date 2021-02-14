from flask import Flask, request
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

db = SQLAlchemy(app)

babel = Babel(app)


@babel.localeselector
def locale(key="lang"):
    """Return the current locale."""
    if app.config["BABEL_DEFAULT_LOCALE"]:
        default = app.config["BABEL_DEFAULT_LOCALE"]
    else:
        default = "en"
    return request.args.get(
        key,
        default=default,
        type=str,
    )


def locales(exclude_current=False):
    """Return all available locales including or excluding the current one."""
    val = app.config["LANGUAGES"]
    if val is None:
        return []
    elif exclude_current:
        return {k: v for k, v in val.items() if v != locale()}
    else:
        return val


def url_for_locale(locale, key="lang"):
    """Create a url for the given locale while keeping the original arguments."""
    val = ""
    if len(request.args) == 0:
        val = key + "=" + locale
    else:
        for k, v in request.args.items():
            if k != key:
                val += (k + "=" + v + "&")
            else:
                val += (k + "=" + locale + "&")
    return request.base_url + "?" + val


app.jinja_env.globals.update(
    locale=locale,
    locales=locales,
    url_for_locale=url_for_locale,
)

from thecollector import routes
