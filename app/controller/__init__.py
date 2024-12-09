from flask import Blueprint
from flask_restx import Api, Namespace

blueprint = Blueprint("difference calculator api", __name__)

api = Api(
    blueprint,
    title="Annotation Project Difference Calculator Microservice",
    version="1.0",
    description="A microservice to calculate differences on different levels for edited documents",
    doc="/docs",
    serve_path="/difference-calc",  # available via /difference-calc/docs
)

# Import and add namespaces
from .heatmap_controller import heatmap_ns as heatmap_ns
from .score_controller import score_ns as score_ns

api.add_namespace(heatmap_ns)
api.add_namespace(score_ns)
