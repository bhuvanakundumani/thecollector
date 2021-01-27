from flask_wtf import FlaskForm
from thecollector.validators import AnswerIndicesImplyContext, RelativeNumberRange
from wtforms import SubmitField, StringField, TextAreaField
from wtforms.fields.html5 import IntegerField
from wtforms.widgets.html5 import NumberInput
from wtforms.validators import DataRequired, NumberRange, InputRequired


class DataForm(FlaskForm):
    title = StringField("Title")
    context = TextAreaField("Context", validators=[DataRequired()])
    question = StringField("Question", validators=[DataRequired()])
    answer_start = IntegerField(
        "Start",
        widget=NumberInput(min=0),
        validators=[
            InputRequired(),
            RelativeNumberRange(min=0, max="context"),
        ],
    )
    answer_end = IntegerField(
        "End",
        widget=NumberInput(min=0),
        validators=[
            InputRequired(),
            RelativeNumberRange(
                min="answer_start",
                max="context",
                exclusive=True,
            ),
        ],
    )
    answer_text = StringField(
        "Answer",
        validators=[
            DataRequired(),
            AnswerIndicesImplyContext("context", "answer_start", "answer_end"),
        ],
    )
    submit = SubmitField("Submit")
