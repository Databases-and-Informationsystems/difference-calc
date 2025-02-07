import json
from flask import request, jsonify
from flask_restx import Resource
from pydantic import TypeAdapter

from app.controllers import ns_score
from app.model.document import DocumentEdit
from app.restx_dtos import (
    similarity_score_response,
    f1_score_request,
)
from app.util.f1_score_calculator import ScoreCalculator
from app.util.utils import get_entities_with_mentions


@ns_score.route("")
class F1ScoreController(Resource):

    @ns_score.doc(
        description="Create f1-score to measure quality of prediction",
        responses={
            200: ("Successful response", similarity_score_response),
            400: "Bad Request",
            500: "Internal Server Error",
        },
    )
    @ns_score.expect(f1_score_request, validate=True)
    def post(self):
        data = request.get_json()
        actual = TypeAdapter(DocumentEdit).validate_json(json.dumps(data.get("actual")))
        predicted = TypeAdapter(DocumentEdit).validate_json(
            json.dumps(data.get("predicted"))
        )
        actual.entities = get_entities_with_mentions(actual.mentions)
        predicted.entities = get_entities_with_mentions(predicted.mentions)

        score_calculator = ScoreCalculator()
        score = score_calculator.calc_score(
            actual_document=actual, predicted_document=predicted
        )
        return jsonify(score.model_dump(mode="json"))
