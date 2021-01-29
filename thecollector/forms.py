from flask_wtf import FlaskForm
from thecollector.validators import AnswerIndicesImplyContext, RelativeNumberRange
from wtforms import SubmitField, StringField, TextAreaField
from wtforms.widgets.html5 import NumberInput
from wtforms.validators import DataRequired, Length


class DataForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    context = TextAreaField(
        "Context",
        render_kw={"minlength": 512},
        validators=[
            Length(min=512),
            DataRequired(),
        ],
    )
    question = StringField("Question", validators=[DataRequired()])
    answer_start = StringField(
        "Start",
        widget=NumberInput(min=0),
        validators=[
            RelativeNumberRange(
                min=0,
                max="context",
                allow_empty=True,
            ),
        ],
    )
    answer_end = StringField(
        "End",
        widget=NumberInput(min=0),
        validators=[
            RelativeNumberRange(
                min="answer_start",
                max="context",
                exclusive=True,
                allow_empty=True,
            ),
        ],
    )
    answer_text = StringField(
        "Answer",
        validators=[
            AnswerIndicesImplyContext(
                "context",
                "answer_start",
                "answer_end",
                allow_empty=True,
            ),
        ],
    )
    submit = SubmitField("Submit")
