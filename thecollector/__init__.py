from .app import app
from .routes import *
from .babel import babel


def main(*args, **kwargs) -> None:
    app.run(*args, **kwargs)
