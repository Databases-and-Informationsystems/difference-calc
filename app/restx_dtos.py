from flask_restx import fields
from app.controllers import api


token_response = api.model(
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
token_request = api.model(
    "token request",
    {
        "id": fields.Integer(required=True),
        "text": fields.String(required=False),
        "document_index": fields.Integer(required=False),
        "sentence_index": fields.Integer(required=False),
        "pos_tag": fields.String(required=False),
    },
)

document_request = api.model(
    "document",
    {
        "id": fields.Integer(
            required=False, description="The unique identifier for the document"
        ),
        "tokens": fields.List(fields.Nested(token_request)),
    },
)

entity_request = api.model(
    "entity",
    {
        "id": fields.Integer(required=True),
    },
)

mention_request = api.model(
    "mention",
    {
        "tag": fields.String(required=True),
        "tokens": fields.List(fields.Nested(token_request)),
        "entity": fields.Nested(entity_request),
    },
)

relation_request = api.model(
    "relation",
    {
        "tag": fields.String(required=True),
        "head_mention": fields.Nested(mention_request),
        "tail_mention": fields.Nested(mention_request),
    },
)
document_edit_request = api.model(
    "document_edit",
    {
        "document": fields.Nested(
            document_request, required=True, description="The document being edited"
        ),
        "mentions": fields.List(
            fields.Nested(mention_request, required=True), required=True
        ),
        "relations": fields.List(
            fields.Nested(relation_request, required=True), required=True
        ),
    },
)

similarity_score_response = api.model(
    "similarity score response",
    {
        "mention_score": fields.Float(required=True),
        "considered_entitiy_quote": fields.Float(required=True),
        "entity_score": fields.Float(required=True),
        "considered_relation_quote": fields.Float(required=True),
        "relation_score": fields.Float(required=True),
    },
)
