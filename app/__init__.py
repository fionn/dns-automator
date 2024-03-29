"""App"""

import os

from flask import Flask

def create_app() -> Flask:
    """app factory"""
    app = Flask(__name__, static_url_path="")
    app.secret_key = os.environ["SECRET_KEY"]

    with app.app_context():
        # We import here to avoid a circular import because views uses
        # flask.current_app
        # pylint: disable=import-outside-toplevel
        from .views import BP
        app.register_blueprint(BP)

    return app
