import typing

from app.model.document import DocumentEdit, Mention, Relation, Token
from app.util.utils import validate_document_edit_lists


class HeatmapCreator:
    def create_heatmap(self, document_edits: typing.List[DocumentEdit]) -> typing.List[Token]:
        """
        Creates a heatmap by assigning a score to each token.
        A higher score indicates greater discrepancies in annotations across documents.
        """
        validate_document_edit_lists(document_edits)
        tokens = document_edits[0].document.tokens

        for token in tokens:
            token.score = _calculate_token_score(token, document_edits)
        
        return tokens


def _calculate_token_score(token: Token, document_edits: typing.List[DocumentEdit]) -> typing.Optional[float]:
    """
    Calculates a score for a token based on annotation consistency across documents.
    A score of 0 means full agreement, while higher scores indicate greater differences.
    """
    token_mentions = [de.get_mention_of_token(token) for de in document_edits]

    # If no document has a mention for this token, no score can be calculated
    if all(mention is None for mention in token_mentions):
        return None

    score = 0.0
    score += _calculate_difference_mention_score(token_mentions)
    score += _calculate_difference_entities_score(token_mentions, document_edits)
    score += _calculate_difference_relations_score(token_mentions, document_edits)
    
    return score


def _calculate_difference_mention_score(mentions: typing.List[Mention]) -> float:
    """
    Computes a score based on whether tokens are annotated the same way across different documents.
    """
    score_list = [
        0 if (m1 is None and m2 is None) or (m1 and m2 and m1.equals(m2)) else 1
        for i, m1 in enumerate(mentions) for j, m2 in enumerate(mentions) if i < j
    ]
    return sum(score_list) / len(score_list) if score_list else 0


def _calculate_difference_relations_score(mentions: typing.List[Mention], document_edits: typing.List[DocumentEdit]) -> float:
    """
    Compares relations of mentions between documents and calculates a discrepancy score.
    """
    score_list = []
    
    for i, mention1 in enumerate(mentions):
        for j, mention2 in enumerate(mentions):
            if i >= j:
                continue
            
            if mention1 and mention2 and mention1.equals(mention2):
                relations1 = document_edits[i].get_all_relations_of_mention(mention1)
                relations2 = document_edits[j].get_all_relations_of_mention(mention2)
                
                common_relations = sum(1 for r1 in relations1 for r2 in relations2 if r1.equals(r2))
                max_relations = max(len(relations1), len(relations2))
                
                score_list.append(-common_relations / max_relations if max_relations > 0 else 0)
    
    return sum(score_list) / len(score_list) if score_list else 0


def _calculate_difference_entities_score(mentions: typing.List[Mention], document_edits: typing.List[DocumentEdit]) -> float:
    """
    Compares entity annotations of mentions and assigns a discrepancy score based on differences.
    """
    score_list = []
    
    for i, mention1 in enumerate(mentions):
        for j, mention2 in enumerate(mentions):
            if i >= j:
                continue
            
            if mention1 and mention2 and mention1.equals(mention2):
                entity1 = document_edits[i].get_entity_of_mention(mention1)
                entity2 = document_edits[j].get_entity_of_mention(mention2)
                
                if entity1 and entity2 and entity1.equals(entity2):
                    score_list.append(-0.5)
                    continue
            
            score_list.append(0)
    
    return sum(score_list) / len(score_list) if score_list else 0
