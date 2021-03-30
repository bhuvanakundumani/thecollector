from .app import app
from .forms import DataForm, TestDataForm
from .db.models import Data

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


@app.route("/test/", methods=["GET", "POST"])
def test_form():
    form = TestDataForm()
    if form.validate_on_submit():
        form.commit(nullify=True)
        flash(_("Recorded"), "success")
    return render_template(
        "form.html",
        form=form,
        guideline="test_guideline",
        sign=request.args.get("sign"),
    )


@app.route("/guideline")
def guideline():
    return render_template("guideline.html")


@app.route("/test/guideline")
def test_guideline():
    return render_template("test_guideline.html")


@app.route("/api/data_len")
def data_len():
    return jsonify(Data.len())


@app.route("/api/title_match/")
@app.route("/api/title_match/<string:title>")
def title_match(title=None):
    return jsonify(Data.col_startswith("title", title, exact=True))
