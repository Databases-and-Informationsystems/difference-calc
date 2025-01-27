import typing

from pydantic import BaseModel, ConfigDict


class SupportsIsEqual(typing.Protocol):
    def equals(self, other: object) -> bool: ...


class Token(BaseModel):
    id: int
    text: typing.Optional[str] = None
    document_index: typing.Optional[int] = None
    sentence_index: typing.Optional[int] = None
    pos_tag: typing.Optional[str] = None

    score: typing.Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

    def equals(self, token: "Token") -> bool:
        return self.id == token.id and (
            self.text == token.text
            and self.document_index == token.document_index
            and self.sentence_index == token.sentence_index
            and self.pos_tag == token.pos_tag
        )


class Entity(BaseModel):
    id: int

    mentions: typing.Optional[typing.List["Mention"]] = None

    def equals(self, entity: typing.Optional["Entity"]) -> bool:
        if entity is None:
            return False
        if (
            self.mentions is None
            and entity.mentions is not None
            or self.mentions is not None
            and entity.mentions is None
        ):
            return False
        if self.mentions is None and entity.mentions is None:
            return True

        # Entity equals other entity of all mentions contain same entries

        return all(any(om.equals(sm) for om in entity.mentions) for sm in self.mentions)

    def __repr__(self) -> str:
        return f"Entity(id={self.id}, mentions={[m.__repr__() for m in self.mentions]})"


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

    def __repr__(self) -> str:
        return f"Mention(tag={self.tag}, entity={"Entity(id={self.entity.id})" if self.entity else None}, tokens={[t.text for t in self.tokens]})"


class Relation(BaseModel):
    id: typing.Optional[int] = None
    tag: str
    mention_head: Mention
    mention_tail: Mention

    def equals(self, relation: "Relation") -> bool:
        return (
            self.tag == relation.tag
            and self.mention_head.equals(relation.mention_head)
            and self.mention_tail.equals(relation.mention_tail)
        )


class Document(BaseModel):
    id: typing.Optional[int] = None
    name: typing.Optional[str] = None
    content: typing.Optional[str] = None
    tokens: typing.List[Token] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentEdit(BaseModel):
    document: Document
    mentions: typing.Optional[typing.List[Mention]] = None
    relations: typing.Optional[typing.List[Relation]] = None

    model_config = ConfigDict(from_attributes=True)

    def get_mentions_of_token(self, token: Token) -> typing.List[Mention]:
        return list(
            filter(lambda mention: mention.contains_token(token), self.mentions or [])
        )

    def get_all_relations_of_mention(self, mention: Mention) -> typing.List[Relation]:
        return list(
            filter(
                lambda relation: relation.mention_head.equals(mention)
                or relation.mention_tail.equals(mention),
                self.relations or [],
            )
        )

    def get_entity_of_mention(self, mention: Mention) -> typing.Optional[Entity]:
        return next((m.entity for m in self.mentions if m.equals(mention)), None)
