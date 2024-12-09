from flask import Blueprint, request, jsonify
from flask_restx import Namespace, Resource
from pydantic import ValidationError
from app.model.document import DocumentEdit

score_ns: Namespace = Namespace(
    name="score", description="Create score for similarity of documents"
)


def calculate_similarity(doc_edit1: DocumentEdit, doc_edit2: DocumentEdit) -> float:
    mentions1 = {mention.tag for mention in doc_edit1.mentions or []}
    mentions2 = {mention.tag for mention in doc_edit2.mentions or []}
    common_mentions = mentions1.intersection(mentions2)
    total_mentions = mentions1.union(mentions2)

    if not total_mentions:
        return 0.0

    return len(common_mentions) / len(total_mentions)


@score_ns.route("")
class ScoreController(Resource):

    def post(self):
        try:
            data = request.json
            doc_edit1 = DocumentEdit(**data["doc_edit1"])
            doc_edit2 = DocumentEdit(**data["doc_edit2"])
        except (ValidationError, KeyError) as e:
            return jsonify({"error": str(e)}), 400

        similarity = calculate_similarity(doc_edit1, doc_edit2)
        return jsonify({"similarity": similarity})
