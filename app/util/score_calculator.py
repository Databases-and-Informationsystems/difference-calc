import typing
from app.model.document import DocumentEdit, Mention, Relation, Token
from app.model.similarity_score import SimilarityScoreResponse


class ScoreCalculator:
    def calc_score(self, document0: DocumentEdit, document1: DocumentEdit):
        if not (
            _all_edits_contain_same_tokens(
                [document0.document.tokens, document1.document.tokens]
            )
        ):
            raise ValueError(
                "Tokens in the different edits of the document are not the same."
            )
        mention_score = _calc_mention_score(
            mention_list_0=document0.mentions, mention_list_1=document1.mentions
        )
        common_mentions_0, common_mentions_1 = _get_common_mention_indices(
            mention_list_0=document0.mentions, mention_list_1=document1.mentions
        )
        relations_by_mentions_0 = _get_relations_by_mentions(
            document0.relations, common_mentions_0
        )
        relations_by_mentions_1 = _get_relations_by_mentions(
            document1.relations, common_mentions_1
        )
        considered_relation_quote = 0
        if (len(document0.relations) + len(document1.relations)) != 0:
            considered_relation_quote = (
                len(relations_by_mentions_0) + len(relations_by_mentions_1)
            ) / (len(document0.relations) + len(document1.relations))
        relation_score = _calc_relation_score(
            relation_list_0=relations_by_mentions_0,
            relation_list_1=relations_by_mentions_1,
        )
        similarity_score_response = SimilarityScoreResponse(
            mention_score=mention_score,
            considered_relation_quote=considered_relation_quote,
            relation_score=relation_score,
        )
        return similarity_score_response


def _calc_mention_score(
    mention_list_0: typing.List[Mention], mention_list_1: typing.List[Mention]
):
    true_positives = sum(
        any(m0.equals(m1) for m1 in mention_list_1) for m0 in mention_list_0
    )
    return _calc_f1_score(
        length_0=len(mention_list_0),
        length_1=len(mention_list_1),
        true_positives=true_positives,
    )


def _calc_relation_score(
    relation_list_0: typing.List[Relation], relation_list_1: typing.List[Relation]
):
    true_positives = sum(
        any(r0.equals(r1) for r1 in relation_list_1) for r0 in relation_list_0
    )
    return _calc_f1_score(
        length_0=len(relation_list_0),
        length_1=len(relation_list_1),
        true_positives=true_positives,
    )


def _get_common_mention_indices(
    mention_list_0: typing.List[Mention], mention_list_1: typing.List[Mention]
) -> tuple[typing.List[Mention], typing.List[Mention]]:
    common_mentions_0 = [
        m0 for m0 in mention_list_0 if any(m0.equals(m1) for m1 in mention_list_1)
    ]
    common_mentions_1 = [
        m1 for m1 in mention_list_1 if any(m1.equals(m0) for m0 in mention_list_0)
    ]
    return (common_mentions_0, common_mentions_1)


def _all_edits_contain_same_tokens(
    token_lists: typing.List[typing.List[Token]],
) -> bool:
    base_list = token_lists[0]
    for token_list in token_lists[1:]:
        if not all(
            any(tl.equals(bt) for bt in base_list) for tl in token_list
        ) or not all(any(bt.equals(tl) for tl in token_list) for bt in base_list):
            return False
    return True


def _calc_f1_score(length_0, length_1, true_positives):
    precision = true_positives / length_0 if length_0 > 0 else 0
    recall = true_positives / length_1 if length_1 > 0 else 0
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
            relation.head_mention in mention_list
            and relation.tail_mention in mention_list
        ):
            relation_by_mentions_list.append(relation)
    return relation_by_mentions_list
