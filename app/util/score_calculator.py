import typing
from app.model.document import DocumentEdit, Mention, Relation
from app.model.similarity_score import SimilarityScoreResponse
from app.util.utils import all_edits_contain_same_tokens


class ScoreCalculator:
    def calc_score(
        self, actual_document: DocumentEdit, predicted_document: DocumentEdit
    ):
        if not (
            all_edits_contain_same_tokens(
                [actual_document.document.tokens, predicted_document.document.tokens]
            )
        ):
            raise ValueError(
                "Tokens in the different edits of the document are not the same."
            )
        mention_score = _calc_mention_score(
            actual_mentions=actual_document.mentions,
            predicted_mentions=predicted_document.mentions,
        )
        common_actual_mentions, common_predicted_mentions = _get_common_mention_indices(
            actual_mentions=actual_document.mentions,
            predicted_mentions=predicted_document.mentions,
        )
        actual_relations_by_mentions = _get_relations_by_mentions(
            actual_document.relations, common_actual_mentions
        )
        predicted_relations_by_mentions = _get_relations_by_mentions(
            predicted_document.relations, common_predicted_mentions
        )
        considered_relation_quote = 0
        if (len(actual_document.relations) + len(predicted_document.relations)) != 0:
            considered_relation_quote = (
                len(actual_relations_by_mentions) + len(predicted_relations_by_mentions)
            ) / (len(actual_document.relations) + len(predicted_document.relations))
        relation_score = _calc_relation_score(
            actual_relations=actual_relations_by_mentions,
            predicted_relations=predicted_relations_by_mentions,
        )
        similarity_score_response = SimilarityScoreResponse(
            mention_score=mention_score,
            considered_relation_quote=considered_relation_quote,
            relation_score=relation_score,
        )
        return similarity_score_response


def _calc_mention_score(
    actual_mentions: typing.List[Mention], predicted_mentions: typing.List[Mention]
):
    true_positives = sum(
        any(m0.equals(m1) for m1 in predicted_mentions) for m0 in actual_mentions
    )
    return _calc_f1_score(
        actual_length=len(actual_mentions),
        predicted_length=len(predicted_mentions),
        true_positives=true_positives,
    )


def _calc_relation_score(
    actual_relations: typing.List[Relation], predicted_relations: typing.List[Relation]
):
    true_positives = sum(
        any(r0.equals(r1) for r1 in predicted_relations) for r0 in actual_relations
    )
    return _calc_f1_score(
        actual_length=len(actual_relations),
        predicted_length=len(predicted_relations),
        true_positives=true_positives,
    )


def _get_common_mention_indices(
    actual_mentions: typing.List[Mention], predicted_mentions: typing.List[Mention]
) -> tuple[typing.List[Mention], typing.List[Mention]]:
    common_mentions_0 = [
        m0 for m0 in actual_mentions if any(m0.equals(m1) for m1 in predicted_mentions)
    ]
    common_mentions_1 = [
        m1 for m1 in predicted_mentions if any(m1.equals(m0) for m0 in actual_mentions)
    ]
    return (common_mentions_0, common_mentions_1)


def _calc_f1_score(actual_length, predicted_length, true_positives):
    precision = true_positives / actual_length if actual_length > 0 else 0
    recall = true_positives / predicted_length if predicted_length > 0 else 0
    if precision + recall > 0:
        f1_score = 2 * (precision * recall) / (precision + recall)
    else:
        f1_score = 0
    return f1_score


def _get_relations_by_mentions(
    relation_list: typing.List[Relation], mention_list: typing.List[Mention]
) -> typing.List[Relation]:
    relation_by_mentions_list = []
    for relation in relation_list:
        if (
            relation.mention_head in mention_list
            and relation.mention_tail in mention_list
        ):
            relation_by_mentions_list.append(relation)
    return relation_by_mentions_list
