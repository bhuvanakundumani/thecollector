from random import randint

from .app import app
from .forms import DataForm, TestDataForm, IdImpossibleForm, IdAnswerableForm
from .db.models import Data

from flask import render_template, flash, request, jsonify, abort, redirect, url_for
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
        title=_("Test dataset form"),
        sign=request.args.get("sign"),
    )


@app.route("/edit/", methods=["GET"])
@app.route("/edit/random", methods=["GET"])
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_id(id=None):
    if id is None:
        return redirect(url_for("edit_id", id=randint(1, Data.len())))
    rec = Data.record(id)
    if rec is None:
        return abort(404)
    form = IdImpossibleForm() if rec.is_impossible else IdAnswerableForm()
    if form.validate_on_submit():
        form.commit(record=rec, excludes=["context"])
        flash(_("Recorded"), "success")
    form.title.data = rec.title
    form.context.data = rec.context
    form.sign.data = rec.sign
    if rec.is_impossible:
        pair = form.impossibles[0]
        pair.question.data = rec.question
    else:
        pair = form.answerables[0]
        pair.question.data = rec.question
        pair = pair.answers[0]
        pair.text.data = rec.answer_text
        pair.start.data = rec.answer_start
        pair.end.data = rec.answer_end
    return render_template(
        "form.html",
        form=form,
        title=_("Edit entry form: #%s") % id,
        sign=rec.sign,
        editable_sign=True,
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
