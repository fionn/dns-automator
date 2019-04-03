"""App"""

import os

from flask import Flask

def create_app() -> Flask:
    """app factory"""
    app = Flask(__name__)
    app.secret_key = os.environ["SECRET_KEY"]

    with app.app_context():
        # We import here because views uses flask.current_app to avoid a
        # circular import
        from .views import BP as views_bp
        app.register_blueprint(views_bp)

    return app
