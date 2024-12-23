import typing

from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    id: int
    text: typing.Optional[str] = None
    document_index: typing.Optional[int] = None
    sentence_index: typing.Optional[int] = None
    pos_tag: typing.Optional[str] = None

    score: typing.Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

    def equals(self, token: "Token") -> bool:
        return self.id == token.id or (
            self.text == token.text
            and self.document_index == token.document_index
            and self.sentence_index == token.sentence_index
            and self.pos_tag == token.pos_tag
        )


class Entity(BaseModel):
    id: int

    def equals(self, entity: typing.Optional["Entity"]) -> bool:
        if entity is None:
            return False
        return self.id == entity.id


class Mention(BaseModel):
    tag: str
    tokens: typing.List[Token]
    entity: typing.Optional[Entity] = None

    def equals(self, mention: "Mention") -> bool:
        return (
            self.tag == mention.tag
            # bidirectional check if lists contain exectly the same tokens
            and all(any(st.equals(mt) for mt in mention.tokens) for st in self.tokens)
            and all(any(mt.equals(st) for st in self.tokens) for mt in mention.tokens)
            # We do not check entity equality here. This is a separate step
        )

    def contains_token(self, token: Token) -> bool:
        return any(t.equals(token) for t in self.tokens)


class Relation(BaseModel):
    id: int
    tag: str
    head_mention: Mention
    tail_mention: Mention

    def equals(self, relation: "Relation") -> bool:
        return (
            self.tag == relation.tag
            and self.head_mention.equals(relation.head_mention)
            and self.tail_mention.equals(relation.tail_mention)
        )


class Document(BaseModel):
    id: typing.Optional[int] = None
    name: str
    content: str
    tokens: typing.Optional[typing.List[Token]] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentEdit(BaseModel):
    document: Document
    mentions: typing.Optional[typing.List[Mention]] = None
    relations: typing.Optional[typing.List[Relation]] = None
    # entities: typing.Optional[typing.List[Entity]] = None

    model_config = ConfigDict(from_attributes=True)

    def get_mentions_of_token(self, token: Token) -> typing.List[Mention]:
        return list(
            filter(lambda mention: mention.contains_token(token), self.mentions or [])
        )

    def get_all_relations_of_mention(self, mention: Mention) -> typing.List[Relation]:
        return list(
            filter(
                lambda relation: relation.head_mention.equals(mention)
                or relation.tail_mention.equals(mention),
                self.relations or [],
            )
        )

    def get_entity_of_mention(self, mention: Mention) -> typing.Optional[Entity]:
        return next((m.entity for m in self.mentions if m.equals(mention)), None)
