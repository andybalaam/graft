from typing import List, Optional
from graftlib.lex import (
    ContinuationToken,
    FunctionToken,
    NumberToken,
    OperatorToken,
    SymbolToken,
)
from graftlib.peekable import Peekable
import attr


@attr.s
class FunctionCall:
    fn: str = attr.ib()

    # args: Tree - e.g. Number("3")
    #                or Tuple(Number("3"), Number("6"))?
    # (or None for no args)
    args: Optional = attr.ib(None)


@attr.s
class IncompleteTree:
    """Returned when parsing stopped in the middle of a parse tree"""
    tokens: List = attr.ib()


@attr.s
class Number:
    value: str = attr.ib()


@attr.s
class Modify:
    sym: str = attr.ib()
    op: str = attr.ib()
    value = attr.ib(None, convert=lambda x: Number("10") if x is None else x)


@attr.s
class Symbol:
    value: str = attr.ib()


def swallow_continuations(tok, it: Peekable):
    while type(tok) == ContinuationToken:
        tok = next(it)
    return tok


def next_tree_for_token(so_far, tok, it):
    # We have decided at this point that any so_far we do have
    # is OK to pass on to the next person, so we get rid of
    # ~s, which just tell us to do exactly that.
    tok = swallow_continuations(tok, it)

    tok_type = type(tok)
    if tok_type == FunctionToken:
        return next_tree(FunctionCall(tok.value, so_far), it)
    elif tok_type == OperatorToken:
        rhs = next_tree(None, it)
        if type(rhs) != Symbol:
            raise Exception(
                "Parse error: we can only do operations to variables, but " +
                "after the %s, I found a %s (%s)." %
                (str(tok), type(rhs).__name__, str(rhs))
            )
        return next_tree(
            Modify(value=so_far, op=tok.value, sym=rhs.value),
            it
        )
    elif tok_type == NumberToken:
        val = tok
        return next_tree(Number(val.value), it)
    elif tok_type == SymbolToken:
        sym = tok
        return next_tree(Symbol(sym.value), it)
    else:
        raise Exception(
            "Parse error: the token %s is an unknown type (%s)" %
            (str(tok), tok_type.__name__)
        )


def next_tree(so_far, it: Peekable):

    # If we've hit the end of the stream, return what we have so far,
    # but if we have nothing so far, we can allow the StopIteration to
    # leak out when we try to get the next token.
    if so_far is not None:
        try:
            it.peek()
        except StopIteration:
            return so_far

    # Symbols and function calls signal the end of the
    # statement, unless they are followed by a ~.
    # Just peek and see whether the next token is a ~,
    # and if not, return immediately.
    if type(so_far) in (FunctionCall, Modify, Symbol):
        if type(it.peek()) != ContinuationToken:
            return so_far

    return next_tree_for_token(so_far, next(it), it)


#: Iterable[Token]
def parse(tokens):
    it = Peekable(iter(tokens))
    while True:
        yield next_tree(None, it)
