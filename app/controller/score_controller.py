import typing
from flask import Blueprint, request, jsonify, Response
from flask_restx import Namespace, Resource, fields
from pydantic import ValidationError, TypeAdapter
from app.model.document import DocumentEdit
from app.util.score_calculator import ScoreCalculator

score_ns: Namespace = Namespace(
    name="score", description="Create score for similarity of documents"
)


similarity_score_response = score_ns.model(
    "similarity score response",
    {
        "mention_score": fields.Float(required=True),
        "considered_entitiy_quote": fields.Float(required=True),
        "entity_score": fields.Float(required=True),
        "considered_relation_quote": fields.Float(required=True),
        "relation_score": fields.Float(required=True),
    },
)
token_response = score_ns.model(
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
token_request = score_ns.model(
    "token request",
    {
        "id": fields.Integer(required=True),
        "text": fields.String(required=False),
        "document_index": fields.Integer(required=False),
        "sentence_index": fields.Integer(required=False),
        "pos_tag": fields.String(required=False),
    },
)
document_request = score_ns.model(
    "document",
    {
        "id": fields.Integer(
            required=False, description="The unique identifier for the document"
        ),
        "tokens": fields.List(fields.Nested(token_request)),
    },
)
document_edit_request = score_ns.model(
    "document_edit",
    {
        "document": fields.Nested(
            document_request, required=True, description="The document being edited"
        ),
    },
)


@score_ns.route("")
class ScoreController(Resource):

    @score_ns.doc(
        description="",
        responses={
            200: ("Successful response", similarity_score_response),
            400: "Bad Request",
            500: "Internal Server Error",
        },
    )
    @score_ns.expect([document_edit_request], validate=True)
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
