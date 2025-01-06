import typing
from app.model.document import Token


def all_edits_contain_same_tokens(
    token_lists: typing.List[typing.List[Token]],
) -> bool:
    base_list = token_lists[0]
    for token_list in token_lists[1:]:
        if not all(
            any(tl.equals(bt) for bt in base_list) for tl in token_list
        ) or not all(any(bt.equals(tl) for tl in token_list) for bt in base_list):
            return False
    return True
