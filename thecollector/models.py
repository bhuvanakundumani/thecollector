from thecollector import DB
from sqlalchemy_serializer import SerializerMixin


class Data(DB.Model, SerializerMixin):
    id = DB.Column(DB.Integer, primary_key=True)
    title = DB.Column(DB.String())
    context = DB.Column(DB.Text)
    question = DB.Column(DB.String())
    answer_text = DB.Column(DB.String())
    answer_start = DB.Column(DB.Integer)
    answer_end = DB.Column(DB.Integer)

    serialize_rules = (
        "-id",
        "-answer_text",
        "-answer_start",
        "-answer_end",
        "answers",
    )

    @property
    def answers(self):
        return {
            "answer_start": [self.answer_start],
            "answer_end": [self.answer_end],
            "text": [self.answer_text],
        }
