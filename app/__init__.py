"""App"""

import os

from flask import Flask

from .db import DB

def create_app() -> Flask:
    """app factory"""
    app = Flask(__name__)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
    app.secret_key = os.environ["SECRET_KEY"]
    DB.init_app(app)

    with app.app_context():
        DB.drop_all()
        DB.create_all()
        # We import here to avoid a circular import because views uses
        # flask.current_app
        from .views import BP
        app.register_blueprint(BP)

    return app
