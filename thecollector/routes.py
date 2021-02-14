from thecollector import app
from thecollector.forms import DataForm
import thecollector.helpers as helpers
from flask import render_template, flash, request, jsonify
from flask_babel import gettext


@app.route("/", methods=["GET", "POST"])
def form():
    form = DataForm()
    if form.validate_on_submit():
        form.commit(nullify=True)
        flash(gettext("Recorded"), "success")
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
    return jsonify(helpers.data_len())
