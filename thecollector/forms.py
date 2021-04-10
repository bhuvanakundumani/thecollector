from typing import Dict

from .db import db
from .db.models import Data

from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField, FormField, Form, FieldList
from wtforms.fields.core import Field
from wtforms.validators import ValidationError, DataRequired, InputRequired, Length
from wtforms.widgets.html5 import NumberInput


errors: Dict[str, str] = {
    "duplicate_title_error": _(
        "The title is already recorded. Work on something else, perhaps?"
    )
}

# Forms and fields


class QuestionForm(Form):
    question = StringField(_("Question"), validators=[DataRequired()])


class AnswerForm(Form):
    _index_widget = NumberInput(min=0)
    text = StringField(_("Answer"), validators=[DataRequired()])
    start = StringField(
        _("Start"),
        widget=_index_widget,
        validators=[InputRequired()],
    )
    end = StringField(
        _("End"),
        widget=_index_widget,
        validators=[InputRequired()],
    )


def data_form_generator(
    answers_count: int = 1,
    answerables_count: int = 7,
    impossibles_count: int = 3,
) -> object:
    class PairedAnswerForm(QuestionForm):
        answers = FieldList(
            FormField(AnswerForm),
            min_entries=answers_count,
            max_entries=answers_count,
        )

    class DataForm(FlaskForm):
        title = StringField(_("Title"), validators=[DataRequired()])
        context_kw = {
            "minlength": 900,
            "rows": 12,
        }
        context = TextAreaField(
            _("Context"),
            render_kw=context_kw,
            validators=[
                Length(min=900),
                DataRequired(),
            ],
        )
        answerables = FieldList(
            FormField(PairedAnswerForm),
            min_entries=answerables_count,
            max_entries=answerables_count,
        )
        impossibles = FieldList(
            FormField(QuestionForm),
            min_entries=impossibles_count,
            max_entries=impossibles_count,
        )
        sign = StringField(_("By"))
        submit = SubmitField(_("Submit"))

        def validate_title(self, field: Field) -> None:
            if Data.query.filter_by(title=field.data).first():
                raise ValidationError(errors["duplicate_title_error"])

        def validate(self, force_unique_questions: bool = False) -> bool:
            if not FlaskForm.validate(self):
                return False
            is_valid = True
            # Check answer indices, their availability in the context,
            # and if they match with the typed answer.
            for pair in self.answerables:
                for answer in pair.answers:
                    if (
                        answer.text.data
                        != self.context.data[
                            int(answer.start.data) : int(answer.end.data)
                        ]
                    ):
                        answer.text.errors.append(
                            _(
                                "Field must be equal to a slice from the start index to the end index of the context, %s."
                            )
                            % self.context.name
                        )
                        is_valid = False
            # Check questions uniqueness
            if force_unique_questions:
                # Since it does not matter much, it is disabled by default
                both = [*self.answerables, *self.impossibles]
                r_both = range(len(both))
                for i in r_both:
                    for j in r_both:
                        if i != j and both[i].question == both[j].question:
                            both[i].question.errors.append(
                                _(
                                    "Use unique questions; Question %(first)s is the same as %(second)s."
                                )
                                % dict(first=both[i].question, second=both[j].question)
                            )
                            is_valid = False
            return is_valid

        def nullify(self):
            """Empties the list.

            Especially useful for when you want to clear the form after its
            successful submission."""
            for pair in self.answerables:
                pair.question.data = None
                for answer in pair.answers:
                    answer.text.data = None
                    answer.start.data = None
                    answer.end.data = None
            for pair in self.impossibles:
                pair.question.data = None
            self.title.data = None
            self.context.data = None
            self.sign.data = None

        def commit(self, nullify: bool = False):
            for pair in self.answerables:
                for answer in pair.answers:
                    db.session.add(
                        Data(
                            title=self.title.data,
                            context=self.context.data,
                            question=pair.question.data,
                            answer_text=answer.text.data,
                            answer_start=answer.start.data,
                            answer_end=answer.end.data,
                            is_impossible=False,
                            sign=self.sign.data,
                        )
                    )
            for pair in self.impossibles:
                db.session.add(
                    Data(
                        title=self.title.data,
                        context=self.context.data,
                        question=pair.question.data,
                        is_impossible=True,
                        sign=self.sign.data,
                    )
                )
            try:
                db.session.commit()
            except Exception as e:
                raise e
            else:
                # This else clause ensures data security for the client. In the
                # case, the commition fails it won't run.
                if nullify:
                    self.nullify()

        def update_pair(
            self,
            record: db.Model,
            nullify: bool = False,
            excludes: list = [],
        ):
            for i in ["title", "context", "sign"]:
                if i not in excludes:
                    setattr(record, i, getattr(self, i).data)
            if record.is_impossible and "question" not in excludes:
                pair = self.impossibles[0]
                record.question = pair.question.data
            else:
                pair = self.answerables[0]
                if "question" not in excludes:
                    record.question = pair.question.data
                pair = pair.answers[0]
                for i in ["text", "start", "end"]:
                    if i not in excludes:
                        setattr(record, "answer_" + i, getattr(pair, i).data)
            try:
                db.session.commit()
            except Exception as e:
                raise e
            else:
                # This else clause ensures data security for the client. In the
                # case, the commition fails it won't run.
                if nullify:
                    self.nullify()

    return DataForm


# Final forms

DataForm = data_form_generator(answers_count=1)
TestDataForm = data_form_generator(answers_count=2)

IdAnswerableForm = data_form_generator(
    answers_count=1,
    answerables_count=1,
    impossibles_count=0,
)
ro_context_kw = IdAnswerableForm.context_kw
ro_context_kw["minlength"] = None
ro_context_kw["readonly"] = ""
ro_context = lambda: TextAreaField(
    _("Context"),
    render_kw=ro_context_kw,
)
IdAnswerableForm.commit = IdAnswerableForm.update_pair
IdAnswerableForm.context = ro_context()
del IdAnswerableForm.validate_title
IdImpossibleForm = data_form_generator(
    answers_count=1,
    answerables_count=0,
    impossibles_count=1,
)
IdImpossibleForm.commit = IdAnswerableForm.update_pair
IdAnswerableForm.context = ro_context()
del IdImpossibleForm.validate_title
