from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField, FormField, Form, FieldList
from wtforms.widgets.html5 import NumberInput
from wtforms.validators import ValidationError, DataRequired, InputRequired, Length
from thecollector import db
from thecollector.models import Data
from flask_babel import lazy_gettext as _


class NoAnswerForm(Form):
    _index_widget = NumberInput(min=0)
    question = StringField(_("Question"), validators=[DataRequired()])


class AnswerForm(NoAnswerForm):
    _index_widget = NoAnswerForm._index_widget
    question = NoAnswerForm.question
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


class DataForm(FlaskForm):
    duplicate_title_error = _(
        "The title is already recorded. Work on something else, perhaps?"
    )
    title = StringField(_("Title"), validators=[DataRequired()])
    context = TextAreaField(
        _("Context"),
        render_kw={
            "minlength": 800,
            "rows": 12,
        },
        validators=[
            Length(min=800),
            DataRequired(),
        ],
    )
    answerables = FieldList(
        FormField(AnswerForm),
        min_entries=7,
        max_entries=7,
    )
    impossibles = FieldList(
        FormField(NoAnswerForm),
        min_entries=3,
        max_entries=3,
    )
    sign = StringField(_("By"))
    submit = SubmitField(_("Submit"))

    def validate_title(self, field):
        if Data.query.filter_by(title=field.data).first():
            raise ValidationError(self.duplicate_title_error)

    def validate(self, force_unique_questions=False):
        if not FlaskForm.validate(self):
            return False
        is_valid = True
        # Check answer indices, their availability in the context,
        # and if they match with the typed answer.
        for pair in self.answerables:
            if (
                pair.text.data
                != self.context.data[int(pair.start.data) : int(pair.end.data)]
            ):
                pair.text.errors.append(
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

    def commit(self, nullify=False):
        for pair in self.answerables:
            db.session.add(
                Data(
                    title=self.title.data,
                    context=self.context.data,
                    question=pair.question.data,
                    answer_text=pair.text.data,
                    answer_start=pair.start.data,
                    answer_end=pair.end.data,
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
                for pair in self.answerables:
                    pair.question.data = None
                    pair.text.data = None
                    pair.start.data = None
                    pair.end.data = None
                for pair in self.impossibles:
                    pair.question.data = None
                self.title.data = None
                self.context.data = None
                self.sign.data = None
