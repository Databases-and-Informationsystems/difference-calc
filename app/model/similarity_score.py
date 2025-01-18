from pydantic import BaseModel


class F1ScoreResponse(BaseModel):
    mention_score: float
    # considered_entity_quote: float
    # entity_score: float
    considered_relation_quote: float
    relation_score: float


class JaccardIndexResponse(BaseModel):
    # TODO
    pass
