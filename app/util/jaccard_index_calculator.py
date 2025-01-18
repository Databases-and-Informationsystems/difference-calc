import typing

from app.model.document import DocumentEdit
from app.model.similarity_score import JaccardIndexResponse
from app.util.utils import validate_document_edit_lists


class JaccardIndexCalculator:

    def calculate(
        self, document_edits: typing.List[DocumentEdit]
    ) -> JaccardIndexResponse:
        validate_document_edit_lists(document_edits)
        # TODO
        return JaccardIndexResponse()
