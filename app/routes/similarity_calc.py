from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from app.model.document import DocumentEdit

similarity_calc_api = Blueprint("similarity_calc_api", __name__)


def calculate_similarity(doc_edit1: DocumentEdit, doc_edit2: DocumentEdit) -> float:
    mentions1 = {mention.tag for mention in doc_edit1.mentions or []}
    mentions2 = {mention.tag for mention in doc_edit2.mentions or []}
    common_mentions = mentions1.intersection(mentions2)
    total_mentions = mentions1.union(mentions2)

    if not total_mentions:
        return 0.0

    return len(common_mentions) / len(total_mentions)


@similarity_calc_api.route("/")
def get():
    return jsonify("hello world")


@similarity_calc_api.route("/calc_similarity", methods=["POST"])
def calculate_similarity_api():
    try:
        data = request.json
        doc_edit1 = DocumentEdit(**data["doc_edit1"])
        doc_edit2 = DocumentEdit(**data["doc_edit2"])
    except (ValidationError, KeyError) as e:
        return jsonify({"error": str(e)}), 400

    similarity = calculate_similarity(doc_edit1, doc_edit2)
    return jsonify({"similarity": similarity})
