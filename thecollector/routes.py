from thecollector import app
from thecollector.forms import DataForm
from thecollector.models import Data
from flask import render_template, flash, request, jsonify
from flask_babel import gettext as _


@app.route("/", methods=["GET", "POST"])
def form():
    form = DataForm()
    if form.validate_on_submit():
        form.commit(nullify=True)
        flash(_("Recorded"), "success")
    return render_template(
        "form.html",
        form=form,
        sign=request.args.get("sign"),
    )


@app.route("/guideline")
def guideline():
    return render_template("guideline.html")


@app.route("/api/data_len")
def data_len():
    return jsonify(Data.len())


@app.route("/api/title_match/")
@app.route("/api/title_match/<string:title>")
def title_match(title=None):
    return jsonify(Data.col_startswith('title', title, exact=True))
