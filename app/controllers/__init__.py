from flask import Blueprint
from flask_restx import Api, Namespace

main = Blueprint("difference calculator api", __name__, url_prefix="/difference-calc")

api = Api(
    main,
    title="Annotation Project Difference Calculator Microservice",
    version="1.0",
    description="A microservice to calculate differences on different levels for edited documents",
    doc="/docs",
    serve_path="/difference-calc",  # available via /difference-calc/docs
)

# Import and add namespaces
ns_heatmap: Namespace = Namespace("heatmap", description="")
from .heatmap_controller import HeatmapController

ns_score: Namespace = Namespace("f1-score", description="")
from .f1_score_controller import F1ScoreController

api.add_namespace(ns_heatmap)
api.add_namespace(ns_score)
