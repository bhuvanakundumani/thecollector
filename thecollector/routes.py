from thecollector import App, babel
from thecollector.forms import DataForm
from flask import render_template, flash, request


@babel.localeselector
def get_locale():
    lang = request.args.get('lang', default = 'fa', type = str)
    return lang

@App.route("/", methods=["GET", "POST"])
def form():
    available_langs = App.config["LANGUAGES"]
    lang = request.args.get('lang', default = 'fa', type = str)
    form = DataForm()
    if form.validate_on_submit():
        form.commit(nullify=True)
        flash(gettext("ثبت شد"), "success")
    return render_template("form.html", form=form, lang=lang, available_langs=available_langs)

@App.route("/guideline")
def guideline():
    return render_template("guideline.html")
