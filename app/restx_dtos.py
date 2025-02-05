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
        "score": fields.Float(required=False),
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
        "entity": fields.Nested(entity_request, required=False),
    },
)

relation_request = api.model(
    "relation",
    {
        "tag": fields.String(required=True),
        "mention_head": fields.Nested(mention_request),
        "mention_tail": fields.Nested(mention_request),
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

f1_score_request = api.model(
    "f1_score_request",
    {
        "actual": fields.Nested(document_edit_request),
        "predicted": fields.Nested(document_edit_request),
    },
)

similarity_score_response = api.model(
    "similarity score response",
    {
        "mention_score": fields.Float(required=True),
        "considered_entity_quote": fields.Float(required=True),
        "entity_score": fields.Float(required=True),
        "considered_relation_quote": fields.Float(required=True),
        "relation_score": fields.Float(required=True),
    },
)

jaccard_index_response = api.model(
    "jaccard index response",
    {
        "combined_index": fields.Float(
            required=True,
            description="An approximation of the overall Jaccard index, where relations and entities are weighted less than mentions.",
        ),
        "mention_index": fields.Float(required=True),
        "relation_index": fields.Float(required=True),
        "considered_relation_index": fields.Float(required=True),
        "entity_index": fields.Float(required=True),
        "considered_entities_index": fields.Float(required=True),
    },
)

jaccard_response = api.model(
    "jaccard index response",
    {
        "average": fields.Nested(
            jaccard_index_response,
            description="The average jaccard index where the index for all pairs of documents is calculated and the average is returned, e.g. ((A∩B/A∪B)+(A∩C/A∪C)+(B∩C/B∪C))/3",
        ),
        "combined": fields.Nested(
            jaccard_index_response,
            description="The combined jaccard index where one index for all documents in calculated at once, e.g. (A∩B∩C/A∪B∪C)",
        ),
    },
)
