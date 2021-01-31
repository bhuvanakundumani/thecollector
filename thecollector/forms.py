from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField, FormField, Form, FieldList
from wtforms.widgets.html5 import NumberInput
from wtforms.validators import ValidationError, DataRequired, InputRequired, Length
from thecollector.models import Data


class NoAnswerForm(Form):
    _index_widget = NumberInput(min=0)
    question = StringField("Question", validators=[DataRequired()])


class AnswerForm(NoAnswerForm):
    _index_widget = NoAnswerForm._index_widget
    question = NoAnswerForm.question
    text = StringField("Answer", validators=[DataRequired()])
    start = StringField(
        "Start",
        widget=_index_widget,
        validators=[InputRequired()],
    )
    end = StringField(
        "End",
        widget=_index_widget,
        validators=[InputRequired()],
    )


class DataForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    context = TextAreaField(
        "Context",
        render_kw={
            "minlength": 512,
            "rows": 12,
        },
        validators=[
            Length(min=512),
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
    submit = SubmitField("Submit")

    def validate_title(self, field):
        if Data.query.filter_by(title=field.data).first():
            raise ValidationError(
                field.gettext(
                    "The title is already available. Work on something else, perhaps?"
                )
            )

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        is_valid = True
        for pair in self.answerables:
            if (
                pair.text.data
                != self.context.data[int(pair.start.data) : int(pair.end.data)]
            ):
                pair.text.errors.append(
                    "Field must be equal to a slice from the start index"
                    " to the end index of the context, %s." % self.context.name
                )
                is_valid = False
        return is_valid
