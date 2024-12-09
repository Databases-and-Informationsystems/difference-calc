from flask import Flask

from .controller import blueprint


def create_app():
    app = Flask(__name__)
    app.register_blueprint(blueprint, url_prefix="/difference-calc")
    return app
