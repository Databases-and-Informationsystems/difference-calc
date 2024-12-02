from flask import Flask
from .routes.similarity_calc import similarity_calc_api


def create_app():
    app = Flask(__name__)
    app.register_blueprint(similarity_calc_api)
    return app
