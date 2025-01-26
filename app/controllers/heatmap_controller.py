import typing

from flask import jsonify, request, Response
from flask_restx import Resource
from pydantic import TypeAdapter

from app.controllers import ns_heatmap
from app.model.document import DocumentEdit
from app.restx_dtos import token_response, document_edit_request
from app.util.heatmap_creator import HeatmapCreator


@ns_heatmap.route("")
class HeatmapController(Resource):

    @ns_heatmap.doc(
        description="Create Heatmap of the tokens by comparing multiple edits of a document",
        responses={
            200: ("Successful response"),
            400: "Bad Request",
            500: "Internal Server Error",
        },
    )
    @ns_heatmap.expect([document_edit_request], validate=True, required=True)
    @ns_heatmap.marshal_with(token_response, as_list=True, code=200)
    def post(self):
        document_edits: typing.List[DocumentEdit] = TypeAdapter(
            list[DocumentEdit]
        ).validate_json(request.get_data())

        heatmap_creator = HeatmapCreator()

        token_heatmap = heatmap_creator.create_heatmap(document_edits)

        return token_heatmap
