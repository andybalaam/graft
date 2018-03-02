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
    negate: bool = attr.ib(default=False)


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


def next_tree_fn(so_far, tok, it):
    return next_tree(FunctionCall(tok.value, so_far), it)


def next_tree_op(so_far, tok, it):
    try:
        if so_far is None:
            if tok.value == "-":
                if type(it.peek()) == NumberToken:
                    ret = next_tree(None, Peekable(iter([next(it)])))
                    ret.negate = not ret.negate
                    return next_tree(ret, it)

        rhs = next_tree(None, it)
    except StopIteration:
        raise Exception(
            (
                "Parse error: I don't know how to handle an "
                "operator (%s) at the end of an expression - it should " +
                "be followed by a number or symbol."
            ) % tok.value
        )

    if type(rhs) != Symbol:
        raise Exception(
            "Parse error: we can only do operations to variables, but " +
            "after '%s' I found a %s (%s)." %
            (tok.value, type(rhs).__name__, str(rhs))
        )
    return next_tree(
        Modify(value=so_far, op=tok.value, sym=rhs.value),
        it
    )


def next_tree_num(so_far, tok, it):
    if so_far is not None:
        raise Exception(
            (
                "Parse error: I don't know how to deal with a %s " +
                "('%s') before a number (%s)."
            ) % (type(so_far), str(so_far), tok.value)

        )
    return next_tree(Number(tok.value), it)


def next_tree_sym(so_far, tok, it):
    if so_far is None:
        sym = tok
        return next_tree(Symbol(sym.value), it)
    else:
        if type(so_far) == Number:
            return next_tree(
                Modify(value=so_far, op="", sym=tok.value),
                it
            )
        else:
            raise Exception(
                (
                    "Parse error: don't know what to do with " +
                    "'{so_far}' before the symbol {tok}.  You can " +
                    "have a number before a symbol, " +
                    "or an operator like +, but not a {type_so_far}."
                ).format(
                    so_far=so_far,
                    tok=tok.value,
                    type_so_far=type(so_far).__name__,
                )
            )


def next_tree_for_token(so_far, tok, it):
    # We have decided at this point that any so_far we do have
    # is OK to pass on to the next person, so we get rid of
    # ~s, which just tell us to do exactly that.
    tok = swallow_continuations(tok, it)

    tok_type = type(tok)
    if tok_type == FunctionToken:
        return next_tree_fn(so_far, tok, it)
    elif tok_type == OperatorToken:
        return next_tree_op(so_far, tok, it)
    elif tok_type == NumberToken:
        return next_tree_num(so_far, tok, it)
    elif tok_type == SymbolToken:
        return next_tree_sym(so_far, tok, it)
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
