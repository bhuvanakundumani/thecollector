from thecollector import App, DB, relative
from thecollector.forms import DataForm
from thecollector.models import Data
from flask import (
    render_template,
    flash,
    redirect,
    send_from_directory,
    url_for,
)
from time import strftime, gmtime
import json


@App.route("/", methods=["GET", "POST"])
def root():
    form = DataForm()
    if form.validate_on_submit():
        for pair in form.answerables:
            DB.session.add(
                Data(
                    title=form.title.data,
                    context=form.context.data,
                    question=pair.question.data,
                    answer_text=pair.text.data,
                    answer_start=pair.start.data,
                    answer_end=pair.end.data,
                    is_impossible=False,
                )
            )
        for pair in form.impossibles:
            DB.session.add(
                Data(
                    title=form.title.data,
                    context=form.context.data,
                    question=pair.question.data,
                    is_impossible=True,
                )
            )
        DB.session.commit()
        flash("Recorded", "success")
    return render_template("form.html", form=form)


# @App.route("/dump")
# def dump():
#     fname = "data_" + strftime("%y%m%d-%H%M%S", gmtime()) + ".json"
#     fpath = relative("static/data/" + fname)
#     data = [i.to_dict() for i in Data.query.all()]
#     with open(fpath, "w") as f:
#         json.dump(data, f)
#     return redirect(url_for("send_data", path=fname))


# @App.route("/static/data/<path:path>")
# def send_data(path):
#     return send_from_directory("static/data", path, as_attachment=True)
