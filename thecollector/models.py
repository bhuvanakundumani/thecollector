from thecollector import db
from sqlalchemy_serializer import SerializerMixin


class Data(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    context = db.Column(db.Text)
    question = db.Column(db.String())
    answer_text = db.Column(db.String())
    answer_start = db.Column(db.Integer)
    answer_end = db.Column(db.Integer)
    is_impossible = db.Column(db.Boolean)

    serialize_rules = (
        "-answer_text",
        "-answer_start",
        "-answer_end",
        "answers",
    )

    @property
    def answers(self):
        return [
            {
                "answer_start": self.answer_start,
                "answer_end": self.answer_end,
                "text": self.answer_text,
            }
        ]
