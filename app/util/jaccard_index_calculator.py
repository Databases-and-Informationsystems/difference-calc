import typing
from itertools import combinations

from app.model.document import DocumentEdit, Relation, SupportsIsEqual, Entity
from app.model.similarity_score import JaccardIndexResponse, JaccardScore
from app.util.utils import validate_document_edit_lists, get_entities_with_mentions


class JaccardIndexCalculator:

    def calculate(
        self, document_edits: typing.List[DocumentEdit]
    ) -> JaccardIndexResponse:
        validate_document_edit_lists(document_edits)

        return JaccardIndexResponse(
            combined=calculate_combined_jaccard_index(document_edits),
            average=calculate_average_jaccard_index(document_edits),
        )


def calculate_combined_jaccard_index(
    document_edits: typing.List[DocumentEdit],
) -> JaccardIndexResponse:
    # Mentions
    mention_union = get_union(list(map(lambda d: d.mentions, document_edits)))
    mention_intersection = get_intersection(
        list(map(lambda d: d.mentions, document_edits))
    )
    mention_index = (
        (len(mention_union) / len(mention_intersection))
        if len(mention_intersection) > 0
        else 0
    )

    # Relations
    relations_lists = list(map(lambda d: d.relations, document_edits))
    relation_index = calculate_jaccard_index_for_relations(relations_lists)
    considered_relations_lists = [
        list(
            filter(
                lambda r: (any(m.equals(r.mention_head) for m in mention_union))
                and (any(m.equals(r.mention_head) for m in mention_union)),
                relations,
            )
        )
        for relations in relations_lists
    ]
    considered_relation_index = calculate_jaccard_index_for_relations(
        considered_relations_lists
    )

    # Entities (with mentions as attributes)
    entities_lists: typing.List[typing.List[Entity]] = [
        get_entities_with_mentions(de.mentions) for de in document_edits
    ]
    entity_index = calculate_jaccard_index_for_entities(entities_lists)
    considered_entities_lists = [
        list(
            filter(
                lambda entity: all(
                    any(mention_of_entity.equals(mention) for mention in mention_union)
                    for mention_of_entity in entity.mentions
                ),
                entities,
            )
        )
        for entities in entities_lists
    ]
    considered_entity_index = calculate_jaccard_index_for_entities(
        considered_entities_lists
    )
    return JaccardScore(
        mention_index=mention_index,
        relation_index=relation_index,
        considered_relation_index=considered_relation_index,
        entity_index=entity_index,
        considered_entities_index=considered_entity_index,
        combined_index=calculate_combined_index(
            mention_index, considered_relation_index, considered_entity_index
        ),
    )


def calculate_average_jaccard_index(
    document_edits: typing.List[DocumentEdit],
) -> JaccardIndexResponse:
    jaccard_scores: typing.List[JaccardScore] = []

    # all possible pairs with size 2 of given document_edits
    for document_edit_pair in combinations(document_edits, 2):
        jaccard_scores.append(
            calculate_combined_jaccard_index(list(document_edit_pair))
        )

    total_combinations = len(jaccard_scores)

    mention_index = (
        sum(map(lambda x: x.mention_index, jaccard_scores)) / total_combinations
    )
    relation_index = (
        sum(map(lambda x: x.relation_index, jaccard_scores)) / total_combinations
    )
    considered_relation_index = (
        sum(map(lambda x: x.considered_relation_index, jaccard_scores))
        / total_combinations
    )
    entity_index = (
        sum(map(lambda x: x.entity_index, jaccard_scores)) / total_combinations
    )
    considered_entities_index = (
        sum(map(lambda x: x.considered_entities_index, jaccard_scores))
        / total_combinations
    )

    return JaccardScore(
        mention_index=mention_index,
        relation_index=relation_index,
        considered_relation_index=considered_relation_index,
        entity_index=entity_index,
        considered_entities_index=considered_entities_index,
        combined_index=calculate_combined_index(
            mention_index, considered_relation_index, considered_entities_index
        ),
    )


def calculate_combined_index(
    mention_index: float, relation_index: float, entity_index: float
) -> float:
    # TODO -- it might be a better approach to weight the relations and entities depending on
    # TODO -- the relation of considered_relation_index and relation_index (considered_entity_index and entity_index
    return (mention_index + (0.5 * relation_index) + (0.5 * entity_index)) / 2


def calculate_jaccard_index_for_relations(
    relations: typing.List[typing.List[Relation]],
) -> float:
    union = get_union(relations)
    intersection = get_intersection(relations)
    if len(intersection) == 0:
        return 0
    return len(union) / len(intersection)


def calculate_jaccard_index_for_entities(
    entities: typing.List[typing.List[Entity]],
) -> float:
    union = get_union(entities)
    intersection = get_intersection(entities)
    if len(intersection) == 0:
        return 0
    return len(union) / len(intersection)


def get_union(
    items_lists: typing.List[typing.List[SupportsIsEqual]],
) -> typing.List[SupportsIsEqual]:
    """

    :param items_lists:
    :return: union of all items from all given items lists
    """
    union: typing.List[SupportsIsEqual] = []
    base_items = items_lists[0]
    remaining_items_lists = items_lists[1:]
    for base_item in base_items:
        if all(
            any(base_item.equals(remaining_item) for remaining_item in remaining_items)
            for remaining_items in remaining_items_lists
        ):
            union.append(base_item)
    return union


def get_intersection(
    items_lists: typing.List[typing.List[SupportsIsEqual]],
) -> typing.List[SupportsIsEqual]:
    """

    :param items_lists:
    :return: intersection of all items from all given items lists
    """
    intersection: typing.List[SupportsIsEqual] = []
    for items in items_lists:
        for item in items:
            if not any(item.equals(i) for i in intersection):
                intersection.append(item)
    return intersection
