import json
from os.path import join

from flask import Flask, request

app = Flask(__name__)


def relative(path="."):
    return join(app.root_path, path)


with open(relative("env.json")) as f:
    config = json.load(f)

app.config["SECRET_KEY"] = config.get("SECRET_KEY")
