#!/usr/bin/env python3
# A mishmash of lazy functions that are not tested nor recommended to use.
# NOTE do NOT put this or any code copied from here in the stable branches.

# To export the database simply run the command below:
# python -c 'from thecollector.db.helper import *; data_dump_real();'

from ..app import app, relative
from . import db
from .models import Data

from time import strftime, gmtime
from typing import Union, Literal, List, Dict
import json
import re
import shutil

import sqlalchemy

tsf = "%y%m%d-%H%M%S"


def hw():
    print("Too lazy to test, hah?")


def delete_title(titles: Union[str, List], final: bool = False) -> None:
    if isinstance(titles, str):
        titles = [titles]
    for i in titles:
        print("Selected %s for deletion" % Data.query.filter_by(title=titles).delete())
    if final:
        db.session.commit()
        print("Committed to DB")
    else:
        print("Dry run")


def db_exec(q: str, skip_backup=False) -> None:
    if (not skip_backup) and (app.config.get("ENV") == "production"):
        backup_db()
    db.engine.execute(sqlalchemy.text(q))


def backup_db() -> str:
    db = re.sub(r"^(\w+:///)", "", app.config["SQLALCHEMY_DATABASE_URI"])
    back = "backup-" + strftime(tsf, gmtime()) + "_" + db
    print("Copying", relative(db), "to the same dir", back)
    return shutil.copy2(relative(db), relative(back))


def signed_by(name) -> List[Data]:
    return Data.query.filter(
        sqlalchemy.func.lower(Data.sign) == sqlalchemy.func.lower(name)
    ).all()


def data_len() -> int:
    return len(Data.query.all())


def data_jsonify(col=None) -> Dict[str, List[Dict[str, Union[str, List[Dict]]]]]:
    if col is None:
        val = []
        for title in [i[0] for i in db.session.query(Data.title).distinct().all()]:
            data = Data.query.filter_by(title=title).all()
            context = data[0].__dict__["context"]
            pairs = [i.to_dict(rules=("-context", "-title")) for i in data]
            val.append(
                {
                    "title": title,
                    "context": context,
                    "pairs": pairs,
                }
            )
    else:
        val = [i.to_dict() for i in col]
    return val


def data_jsonify_squad(
    only: Literal["single", "multi", None] = None,
) -> List[Dict[str, Union[str, List[Dict]]]]:
    # TODO optimize, so HACK-y
    val = []
    for title in [i[0] for i in db.session.query(Data.title).distinct().all()]:
        data = Data.query.filter_by(title=title).all()
        context = data[0].__dict__["context"]
        pairs = [i.to_dict(rules=("-context", "-title")) for i in data]
        redundant_pairs = []
        # multianswer = []
        multianswer = False
        for i in range(len(pairs)):
            # if pairs[i]["sign"] is None:
            #     pairs[i]["sign"] = ""
            if i in redundant_pairs:
                continue
            for j in range(i + 1, len(pairs)):
                if pairs[i]["question"] == pairs[j]["question"]:
                    pairs[i]["answers"].append(pairs[j]["answers"][0])
                    redundant_pairs.append(j)
                    multianswer = True
        for i in range(len(redundant_pairs)):
            del pairs[redundant_pairs[i] - i]
        # Empty answers if impossible instead of null
        for i in pairs:
            if i["is_impossible"]:
                i["answers"] = []
        if (
            only is None
            or (only == "single" and not multianswer)
            or (only == "multi" and multianswer)
        ):
            val.append(
                {
                    "title": title,
                    "paragraphs": [
                        {
                            "qas": pairs,
                            "context": context,
                        }
                    ],
                }
            )
    return {"data": val}


def data_dump(func=data_jsonify_squad, name=None, *func_args, **func_kwargs) -> None:
    fpath = ("data_" + strftime(tsf, gmtime()) + ".json") if name is None else name
    fpath = relative("db/" + fpath)
    with open(fpath, "w") as f:
        json.dump(
            func(*func_args, **func_kwargs),
            f,
            ensure_ascii=False,
            indent=2,
        )
    print("Wrote to: ", fpath)


def data_dump_real():
    time = strftime(tsf, gmtime())
    data_dump(name="REAL_all_data_" + time + ".json")
    data_dump(name="REAL_singles_data_" + time + ".json", only="single")
    data_dump(name="REAL_multis_data_" + time + ".json", only="multi")


# read_squad_v2 function
def data_test_custom(path) -> List[Dict]:
    path = relative(path)
    ds = []
    with open(path, encoding="utf-8") as f:
        squad = json.load(f)
        for example in squad["data"]:
            title = example.get("title", "").strip()
            for paragraph in example["paragraphs"]:
                context = paragraph["context"].strip()
                for qa in paragraph["qas"]:
                    question = qa["question"].strip()
                    id_ = qa["id"]
                    answer_starts = [answer["answer_start"] for answer in qa["answers"]]
                    answers = [answer["text"].strip() for answer in qa["answers"]]
                    ds.append(
                        {
                            "title": title,
                            "context": context,
                            "question": question,
                            "id": id_,
                            "answers": {
                                "answer_start": answer_starts,
                                "text": answers,
                            },
                        }
                    )
    return ds
