import typing

from flask import request, jsonify
from flask_restx import Resource
from pydantic import TypeAdapter

from app.controllers import ns_jaccard_index
from app.model.document import DocumentEdit
from app.restx_dtos import document_edit_request, jaccard_index_response
from app.util.jaccard_index_calculator import JaccardIndexCalculator


@ns_jaccard_index.route("")
class JaccardIndexController(Resource):

    @ns_jaccard_index.doc(
        description="Calculate jaccard index for similarity of document edits",
        responses={
            200: ("Successful response", jaccard_index_response),
            400: "Bad Request",
            500: "Internal Server Error",
        },
    )
    @ns_jaccard_index.expect([document_edit_request], validate=True)
    def post(self):
        document_edits: typing.List[DocumentEdit] = TypeAdapter(
            list[DocumentEdit]
        ).validate_json(request.get_data())

        jaccard_index_calculator = JaccardIndexCalculator()
        result = jaccard_index_calculator.calculate(document_edits)

        return jsonify(result.model_dump(mode="json"))
