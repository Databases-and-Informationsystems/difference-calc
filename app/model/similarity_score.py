from pydantic import BaseModel


class F1ScoreResponse(BaseModel):
    mention_score: float
    # considered_entity_quote: float
    # entity_score: float
    considered_relation_quote: float
    relation_score: float


class JaccardScore(BaseModel):
    mention_index: float
    relation_index: float
    considered_relation_index: float
    entity_index: float
    considered_entities_index: float
    combined_index: float


class JaccardIndexResponse(BaseModel):
    combined: JaccardScore
    average: JaccardScore
