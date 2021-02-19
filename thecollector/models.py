from thecollector import db
from sqlalchemy_serializer import SerializerMixin


class Base:
    @classmethod
    def col_startswith(
        cls, col, key=None, exact=False, distinct=True, all=False, reshape=True
    ):
        """Find a value in a column that has a value that starts like `key`.

        Can also be used as a search method for the column with `exact` set to False.
        In that case, if nothing is found, `False` is returned.

        If `key` is None or empty, all values will be returned.

        `reshape` implies `all`. If reshape is set to `True`, a one dimensional
        list will be returned. Otherwise the list will have each element in a tuple."""
        if key is None and exact:
            return False
        col = getattr(cls, col)
        val = db.session.query(col)
        if distinct:
            val = val.distinct()
        if key is not None:
            if exact:
                val = val.filter(col == key)
            else:
                val = val.filter(col.startswith(key))
        if reshape or all:
            val = val.all()
            if reshape:
                if exact:
                    try:
                        val = val[0][0]
                    except IndexError:
                        val = False
                else:
                    val = [i[0] for i in val]
        return val

    @classmethod
    def len(cls):
        return len(cls.query.all())


class Data(Base, db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    context = db.Column(db.Text)
    question = db.Column(db.String())
    answer_text = db.Column(db.String())
    answer_start = db.Column(db.Integer)
    answer_end = db.Column(db.Integer)
    sign = db.Column(db.String())
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
