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
            200: ("Successful response", token_response),
            400: "Bad Request",
            500: "Internal Server Error",
        },
    )
    @ns_heatmap.expect([document_edit_request], validate=True, required=True)
    def post(self):
        try:
            document_edits: typing.List[DocumentEdit] = TypeAdapter(
                list[DocumentEdit]
            ).validate_json(request.get_data())
        except Exception as e:
            return Response(str(e), 400)

        try:
            heatmap_creator = HeatmapCreator()

            token_heatmap = heatmap_creator.create_heatmap(document_edits)

            return jsonify([t.model_dump(mode="json") for t in token_heatmap])
        except Exception as e:
            return Response(str(e), 500)
