import pytest

from app import create_app
from app.model.document import Mention, Token, Relation, Entity
from app.util.heatmap_creator import similarity_mention_score


@pytest.fixture
def app():
    app = create_app()
    with app.app_context():
        yield app


def test_similarity_mention_score_empty_lists():
    """
    If there is an empty list of mentions, the score should be the size of the other list
    :return:
    """
    token1 = Token(id=1, text="The", document_index=0, sentence_index=0, pos_tag="NN")
    token2 = Token(id=1, text="The", document_index=0, sentence_index=0, pos_tag="NN")
    entity1 = Entity(id=1)
    entity2 = Entity(id=2)
    mention1 = Mention(tag="tag1", tokens=[token1], entity=entity1)
    mention2 = Mention(tag="tag2", tokens=[token2], entity=entity2)
    assert similarity_mention_score([], []) == 0
    assert similarity_mention_score([], [mention1, mention2]) == 2
    assert (
        similarity_mention_score(
            [
                Relation(
                    id=1, tag="executes", mention_head=mention1, mention_tail=mention2
                )
            ],
            [],
        )
        == 1
    )


def test_similar_mention_score_same_mentions():
    """
    If the lists contain the same mentions, the score should be 0
    :return:
    """
    token1 = Token(id=1, text="The", document_index=0, sentence_index=0, pos_tag="NN")
    token2 = Token(id=1, text="The", document_index=0, sentence_index=0, pos_tag="NN")
    mention1 = Mention(tag="tag1", tokens=[token1], entity=Entity(id=1))
    mention2 = Mention(tag="tag1", tokens=[token2], entity=Entity(id=1))

    assert similarity_mention_score([mention1], [mention2]) == 0


def test_similar_mention_score_different_mentions():
    """
    In the complex way, the score should be the count of elements from the larger list, that are in one but not the other list
    :return:
    """
    token11 = Token(id=1, text="The", document_index=0, sentence_index=0, pos_tag="NN")
    token12 = Token(id=1, text="The", document_index=0, sentence_index=0, pos_tag="NN")
    token21 = Token(
        id=2, text="company", document_index=0, sentence_index=0, pos_tag="NN"
    )
    token22 = Token(
        id=2, text="company", document_index=0, sentence_index=0, pos_tag="NN"
    )
    mention11 = Mention(tag="tag1", tokens=[token11], entity=Entity(id=1))
    mention21 = Mention(tag="tag1", tokens=[token12], entity=Entity(id=1))
    mention12 = Mention(tag="tag2", tokens=[token21], entity=Entity(id=2))
    mention22 = Mention(tag="tag2", tokens=[token22], entity=Entity(id=2))

    assert similarity_mention_score([mention11, mention12], [mention22, mention21]) == 0
    assert similarity_mention_score([mention11, mention21], [mention22, mention12]) == 2
    assert similarity_mention_score([mention11], [mention22, mention21]) == 1
    assert similarity_mention_score([mention11, mention22], [mention12]) == 1
