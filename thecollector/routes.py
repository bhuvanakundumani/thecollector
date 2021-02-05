from thecollector import App, Babel
from thecollector.forms import DataForm
from flask import render_template, flash, request
from flask_babel import gettext


@Babel.localeselector
def get_locale():
    return request.args.get(
        "lang",
        default=App.config["BABEL_DEFAULT_LOCALE"],
        type=str,
    )


def locales(exclude_current=False):
    val = App.config["LANGUAGES"]
    if exclude_current:
        current = get_locale()
        return {k: v for k, v in val.items() if v != current}
    return val


@App.route("/", methods=["GET", "POST"])
def form():
    form = DataForm()
    if form.validate_on_submit():
        form.commit(nullify=True)
        flash(gettext("recorded"), "success")
    return render_template(
        "form.html",
        form=form,
        lang=get_locale(),
        other_locales=locales(exclude_current=True),
    )


@App.route("/guideline")
def guideline():
    return render_template("guideline.html")
