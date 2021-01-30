from flask_wtf import FlaskForm
from thecollector.validators import AnswerIndicesImplyContext, RelativeNumberRange
from wtforms import SubmitField, StringField, TextAreaField
from wtforms.widgets.html5 import NumberInput
from wtforms.validators import DataRequired, InputRequired, Length


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
    question = StringField("Question", validators=[DataRequired()])
    answer_start = StringField(
        "Start",
        widget=NumberInput(min=0),
        validators=[
            InputRequired(),
            RelativeNumberRange(
                min=0,
                max="context",
            ),
        ],
    )
    answer_end = StringField(
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
            AnswerIndicesImplyContext(
                "context",
                "answer_start",
                "answer_end",
            ),
        ],
    )
    submit = SubmitField("Submit")
