from pydantic import BaseModel


class SimilarityScoreResponse(BaseModel):
    mention_score: float
    # considered_entitiy_quote: float
    # entity_score: float
    considered_relation_quote: float
    relation_score: float
