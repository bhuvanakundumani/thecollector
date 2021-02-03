from thecollector import App
from thecollector.forms import DataForm
from flask import render_template, flash


@App.route("/", methods=["GET", "POST"])
def form():
    form = DataForm()
    if form.validate_on_submit():
        form.commit(nullify=True)
        flash("Recorded", "success")
    return render_template("form.html", form=form)


@App.route("/guideline")
def guideline():
    return render_template("guideline.html")
