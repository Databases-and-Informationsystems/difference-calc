from flask import Flask

from app.exception import register_error_handlers


def create_app():
    app = Flask(__name__)

    from .controllers import main

    app.register_blueprint(main)

    register_error_handlers(app)

    return app
