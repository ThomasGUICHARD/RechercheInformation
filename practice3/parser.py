
from typing import Generator, List, Set
from index import IndexStore


def locate_end_parenthesis(exp: List[str], start: int) -> int:
    deep = 0
    for i in range(start, len(exp)):
        c = exp[i]
        if c == '(':
            deep += 1
        elif c == ')':
            if deep == 0:
                return i
            else:
                deep -= 1
    raise Exception("No end parenthesis!")


def and_lst(a: Set[str], b: Set[str], not_b: bool) -> None:
    """
    equivalent to a &= b
    """
    if not_b:
        raise Exception("'not' not implemented")

    a = a.intersection(b)


def or_lst(a: Set[str], b: Set[str], not_b: bool) -> None:
    """
    equivalent to a |= b
    """
    if not_b:
        raise Exception("'not' not implemented")

    a = a.union(b)


def parse_expr(store: IndexStore, exp: List[str]) -> Set[str]:
    and_result = set()

    i = 0
    next_inverted = False
    while i < len(exp):
        op = exp[i]
        i += 1

        if op == "!":
            next_inverted = True
            continue

        if op == "":
            continue

        if op == "(":
            end = locate_end_parenthesis(exp, i)
            output = store.parse_expr(exp[i:end])
            and_lst(and_result, output, next_inverted)
            i = end + 1
        elif op == "|":
            b = store.parse_expr(exp[i:len(exp)])
            or_lst(and_result, b, next_inverted)
            return and_result
        else:
            # word
            and_lst(and_result, store.fetch_word_tf(op), next_inverted)
        next_inverted = False

    return and_result


def parse(store: IndexStore, exp: str) -> Generator[str, None, None]:
    result = store.parse_expr(exp.lower().split(" "))

    for i in range(len(result)):
        if result[i] != 0:
            yield store.corpus_name_ids[i]
