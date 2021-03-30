from .app import app

from flask import request
from flask_babel import Babel

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
                val += k + "=" + v + "&"
            else:
                val += k + "=" + locale + "&"
    return request.base_url + "?" + val


app.jinja_env.globals.update(
    locale=locale,
    locales=locales,
    url_for_locale=url_for_locale,
)
