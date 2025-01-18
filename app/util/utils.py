import typing
from app.model.document import Token, DocumentEdit, Mention, Entity


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


def get_entities_with_mentions(mentions: typing.List[Mention]) -> typing.List[Entity]:
    """

    :param mentions:
    :return: List of entities, where each entity hat the property mentions with all mentions that belong to this entity
    """
    unique_entity_ids = list({mention.entity.id for mention in mentions})
    mentions_by_entity_id = {}
    for unique_entity_id in unique_entity_ids:
        mentions_by_entity_id[unique_entity_id] = []

    for mention in mentions:
        mentions_by_entity_id[mention.entity.id].append(mention)

    return [
        Entity(id=id_key, mentions=mentions_by_entity_id.get(id_key))
        for id_key in mentions_by_entity_id
    ]


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
