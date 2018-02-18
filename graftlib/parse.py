from typing import Iterator, List
from graftlib.lex import (
    FunctionToken,
    NumberToken,
    OperatorToken,
    SymbolToken,
)
import attr


@attr.s
class FunctionCall:
    fn: FunctionToken = attr.ib()


@attr.s
class IncompleteTree:
    """Returned when parsing stopped in the middle of a parse tree"""
    tokens: List = attr.ib()


@attr.s
class Modify:
    sym: SymbolToken = attr.ib()
    op: OperatorToken = attr.ib()
    value = attr.ib(NumberToken("10"))


@attr.s
class Symbol:
    value: SymbolToken = attr.ib()


def next_tree(token, it: Iterator):
    if type(token) == FunctionToken:   # :foo
        return FunctionCall(token)
    elif type(token) == SymbolToken:   # _bar
        return Symbol(token)
    elif type(token) == NumberToken:   # 3+baz
        try:
            op_token = next(it)
            sym_token = next(it)
        except StopIteration:
            return IncompleteTree(
                [token] if op_token is None else [token, op_token]
            )
        sym: Symbol = next_tree(sym_token, it)
        return Modify(sym=sym.value, op=op_token, value=token)
    else:                              # +baz
        try:
            next_token = next(it)
        except StopIteration:
            return IncompleteTree([token])
        sym: Symbol = next_tree(next_token, it)
        return Modify(sym=sym.value, op=token)


#: Iterable[Token]
def parse(tokens):
    it = iter(tokens)
    while True:
        token = next(it)
        yield next_tree(token, it)
