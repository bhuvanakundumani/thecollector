from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField, FormField, Form
from wtforms.widgets.html5 import NumberInput
from wtforms.validators import ValidationError, DataRequired, InputRequired, Length
from thecollector.models import Data


class NoAnswerForm(Form):
    _index_widget = NumberInput(min=0)
    question = StringField("Question", validators=[DataRequired()])


class AnswerForm(NoAnswerForm):
    _index_widget = NoAnswerForm._index_widget
    question = NoAnswerForm.question
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
    text = StringField("Answer", validators=[DataRequired()])


class AnswersForm(Form):
    answer_1 = FormField(AnswerForm)
    answer_2 = FormField(AnswerForm)
    answer_3 = FormField(AnswerForm)
    answer_4 = FormField(AnswerForm)
    answer_5 = FormField(AnswerForm)
    answer_6 = FormField(AnswerForm)
    answer_7 = FormField(AnswerForm)
    no_answer_1 = FormField(NoAnswerForm)
    no_answer_2 = FormField(NoAnswerForm)
    no_answer_3 = FormField(NoAnswerForm)


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
    pairs = AnswersForm()
    submit = SubmitField("Submit")

    def validate_title(self, field):
        if Data.query.filter_by(title=field.data).first():
            raise ValidationError(
                field.gettext(
                    "The title is already available. Work on something else, perhaps?"
                )
            )

    def validate_pairs(self, pairs):
        # Implement a minimal RelativeNumberRange here and loop for every pair
        pass
