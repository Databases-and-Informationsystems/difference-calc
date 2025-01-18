import typing

from app.model.document import DocumentEdit, Mention, Relation, Token
from app.util.utils import all_edits_contain_same_tokens, validate_document_edit_lists


class HeatmapCreator:

    def create_heatmap(
        self, document_edits: typing.List[DocumentEdit]
    ) -> typing.List[Token]:
        validate_document_edit_lists(document_edits)

        tokens: typing.List[Token] = document_edits[0].document.tokens

        for token in tokens:
            token.score = _calculate_token_score(token, document_edits)
        return tokens


def _calculate_token_score(
    token: Token, document_edits: typing.List[DocumentEdit]
) -> float:
    """
    Creates a score for each token

    - If the score is 0, the tokens are annotated exactly the same in all documents
    - The greater the score, the more different is the token annotated in the documents
    :param token:
    :param document_edits:
    :return:
    """
    score: float = 0.0
    token_mentions_per_document = list(
        map(lambda de: de.get_mentions_of_token(token), document_edits)
    )
    score += _calculate_group_difference_mention_score(token_mentions_per_document)

    # calculate similarity of relations associated with the mention(s) of the token
    n = len(token_mentions_per_document)
    for i in range(n):
        for j in range(i + 1, n):
            # Pairs of all mentions that are the same in both documents
            mention_pairs = _get_matching_mention_pairs(
                token_mentions_per_document[i], token_mentions_per_document[j]
            )

            score += _calculate_difference_entities_score(mention_pairs=mention_pairs)

            score += _calculate_difference_relation_score(
                mention_pairs=mention_pairs,
                document_edit1=document_edits[i],
                document_edit2=document_edits[j],
            )

    return score


def _similarity_mention_score(
    list1: typing.List[Mention],
    list2: typing.List[Mention],
) -> int:
    """

    :param list1: list of mentions
    :param list2: list of mentions
    :return: count of elements in the list, that do not exist in the other list
    """
    (longer, shorter) = (list1, list2) if len(list1) > len(list2) else (list2, list1)

    return sum(1 for x in longer if not any(x.equals(y) for y in shorter))


def _calculate_group_difference_mention_score(
    lists: typing.List[typing.List[Mention]],
) -> float:
    """

    :param lists: list of lists of the mentions associated to a specific token in a document
    :return: similarity score of the Mention lists
    """
    n = len(lists)
    total_score = 0

    # compare each pair of edited documents
    for i in range(n):
        for j in range(i + 1, n):
            total_score += _similarity_mention_score(lists[i], lists[j])

    return total_score


def _calculate_difference_relation_score(
    mention_pairs: typing.List[typing.Tuple[Mention, Mention]],
    document_edit1: DocumentEdit,
    document_edit2: DocumentEdit,
) -> float:
    score: float = 0.0
    for mention_i, mention_j in mention_pairs:
        relations_i: typing.List[Relation] = (
            document_edit1.get_all_relations_of_mention(mention_i)
        )
        relations_j: typing.List[Relation] = (
            document_edit2.get_all_relations_of_mention(mention_j)
        )

        max_relation_count = max(len(relations_i), len(relations_j))
        common_count = len(
            [
                obj_i
                for obj_i in relations_i
                if any(obj_i.equals(obj_j) for obj_j in relations_j)
            ]
        )
        score += (
            ((common_count - max_relation_count) / max_relation_count)
            if max_relation_count > 0
            else 0
        )

    return score


def _calculate_difference_entities_score(
    mention_pairs: typing.List[typing.Tuple[Mention, Mention]]
) -> float:
    score: float = 0.0
    for mention_i, mention_j in mention_pairs:
        if (
            mention_j.entity is None and mention_i.entity is not None
        ) or not mention_j.entity.equals(mention_i.entity):
            score += 0.5
    return score


def _get_matching_mention_pairs(
    list1: typing.List[Mention], list2: typing.List[Mention]
) -> typing.List[typing.Tuple[Mention, Mention]]:
    matching_pairs = []
    for x in list1:
        for y in list2:
            if x.equals(y):
                matching_pairs.append((x, y))
    return matching_pairs
