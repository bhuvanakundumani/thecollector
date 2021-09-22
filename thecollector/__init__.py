from .app import app
from .routes import *
from .babel import babel
from .db import * 

def main(*args, **kwargs) -> None:
    db.create_all()
    app.run(*args, **kwargs)
