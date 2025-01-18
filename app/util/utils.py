import typing
from app.model.document import Token, DocumentEdit


def all_edits_contain_same_tokens(
    token_lists: typing.List[typing.List[Token]],
) -> bool:
    base_list = token_lists[0]
    for token_list in token_lists[1:]:
        if not all(
            any(tl.equals(bt) for bt in base_list) for tl in token_list
        ) or not all(any(bt.equals(tl) for tl in token_list) for bt in base_list):
            return False
    return True


def validate_document_edit_lists(document_edits: typing.List[DocumentEdit]):
    if len(document_edits) < 2:
        raise ValueError("At least 2 edits of a document have to be compared.")

    if not (
        all_edits_contain_same_tokens(
            list(map(lambda de: de.document.tokens, document_edits))
        )
    ):
        raise ValueError(
            "Tokens in the different edits of the document are not the same."
        )
