from thecollector import app, babel
from thecollector.forms import DataForm
import thecollector.helpers as helpers
from flask import render_template, flash, request, jsonify
from flask_babel import gettext


@babel.localeselector
def get_locale():
    if app.config["BABEL_DEFAULT_LOCALE"]:
        default = app.config["BABEL_DEFAULT_LOCALE"]
    else:
        default = "en"
    return request.args.get(
        "lang",
        default=default,
        type=str,
    )


def locales(exclude_current=False):
    val = app.config["LANGUAGES"]
    if val is None:
        return []
    elif exclude_current:
        return {k: v for k, v in val.items() if v != get_locale()}
    else:
        return val


@app.route("/", methods=["GET", "POST"])
def form():
    form = DataForm()
    if form.validate_on_submit():
        form.commit(nullify=True)
        flash(gettext("Recorded"), "success")
    return render_template(
        "form.html",
        form=form,
        lang=get_locale(),
        other_locales=locales(exclude_current=True),
    )


@app.route("/guideline")
def guideline():
    return render_template("guideline.html")


@app.route("/api/data_len")
def data_len():
    return jsonify(helpers.data_len())
