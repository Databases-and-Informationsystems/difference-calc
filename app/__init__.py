from flask import Flask


def create_app():
    app = Flask(__name__)

    from .controllers import main

    app.register_blueprint(main, url_prefix="/difference-calc")
    return app
