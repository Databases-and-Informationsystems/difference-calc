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
from app.util.score_calculator import ScoreCalculator


@ns_score.route("")
class F1ScoreController(Resource):

    @ns_score.doc(
        description="Create score for similarity of documents",
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

        score_calculator = ScoreCalculator()
        score = score_calculator.calc_score(document0=actual, document1=predicted)
        return jsonify(score.model_dump(mode="json"))
