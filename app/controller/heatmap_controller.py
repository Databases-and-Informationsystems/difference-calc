import typing

from flask import jsonify, request, Response
from flask_restx import Namespace, Resource, fields
from pydantic import TypeAdapter

from app.model.document import DocumentEdit
from app.util.heatmap_creator import HeatmapCreator

heatmap_ns: Namespace = Namespace(
    name="heatmap",
    description="Create Heatmap of the tokens by comparing multiple edits of a document",
)

token_response = heatmap_ns.model(
    "token response",
    {
        "id": fields.Integer(required=True),
        "text": fields.String(required=False),
        "document_index": fields.Integer(required=False),
        "sentence_index": fields.Integer(required=False),
        "pos_tag": fields.String(required=False),
        "score": fields.Float(required=True),
    },
)
token_request = heatmap_ns.model(
    "token request",
    {
        "id": fields.Integer(required=True),
        "text": fields.String(required=False),
        "document_index": fields.Integer(required=False),
        "sentence_index": fields.Integer(required=False),
        "pos_tag": fields.String(required=False),
    },
)
document_request = heatmap_ns.model(
    "document",
    {
        "id": fields.Integer(
            required=False, description="The unique identifier for the document"
        ),
        "tokens": fields.List(fields.Nested(token_request)),
    },
)
document_edit_request = heatmap_ns.model(
    "document_edit",
    {
        "document": fields.Nested(
            document_request, required=True, description="The document being edited"
        ),
    },
)


@heatmap_ns.route("")
class HeatmapController(Resource):

    @heatmap_ns.doc(
        description="",
        responses={
            200: ("Successful response", token_response),
            400: "Bad Request",
            500: "Internal Server Error",
        },
    )
    @heatmap_ns.expect([document_edit_request], validate=True)
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
