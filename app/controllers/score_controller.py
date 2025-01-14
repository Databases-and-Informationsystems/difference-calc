import typing
from flask import request, jsonify, Response
from flask_restx import Resource
from pydantic import TypeAdapter

from app.controllers import ns_score
from app.model.document import DocumentEdit
from app.restx_dtos import document_edit_request, similarity_score_response
from app.util.score_calculator import ScoreCalculator


@ns_score.route("")
class ScoreController(Resource):

    @ns_score.doc(
        description="Create score for similarity of documents",
        responses={
            200: ("Successful response", similarity_score_response),
            400: "Bad Request",
            500: "Internal Server Error",
        },
    )
    @ns_score.expect([document_edit_request], validate=True)
    def post(self):
        try:
            document_edits: typing.List[DocumentEdit] = TypeAdapter(
                list[DocumentEdit]
            ).validate_json(request.get_data())
            for document_edit in document_edits:
                document_edit.resolve_mentions_in_relations()
            if len(document_edits) != 2:
                return Response(
                    "Payload must contain exactly 2 document requests.", status=400
                )
        except Exception as e:
            return Response(str(e), 400)
        try:
            score_calculator = ScoreCalculator()
            score = score_calculator.calc_score(
                document0=document_edits[0], document1=document_edits[1]
            )
            return jsonify(score.model_dump(mode="json"))
        except Exception as e:
            return Response(str(e), 500)
