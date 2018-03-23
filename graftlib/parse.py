from typing import List, Optional
from graftlib.lex import (
    ContinuationToken,
    EndFunctionDefToken,
    FunctionCallToken,
    NumberToken,
    OperatorToken,
    SeparatorToken,
    StartFunctionDefToken,
    SymbolToken,
)
from graftlib.peekable import Peekable
import attr


@attr.s
class ParseState:
    it: Peekable = attr.ib()
    end_tok_type = attr.ib()
    single_item: bool = attr.ib()


@attr.s
class FunctionCall:
    fn = attr.ib()

    # args: Tree - e.g. Number("3")
    #                or Tuple(Number("3"), Number("6"))?
    # (or None for no args)
    args: Optional = attr.ib(None)


@attr.s
class FunctionDef:
    body: List = attr.ib()


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


def next_or_single(value, state: ParseState):
    if state.single_item:
        return value
    else:
        return next_tree(value, state)


def next_tree_fn(so_far, tok, state: ParseState):
    fn = next_tree(None, ParseState(state.it, state.end_tok_type, True))
    return next_or_single(FunctionCall(fn, so_far), state)


def next_tree_op(so_far, tok, state: ParseState):
    try:
        if so_far is None:
            if tok.value == "-":
                if type(state.it.peek()) == NumberToken:
                    ret = next_tree(
                        None,
                        ParseState(
                            Peekable(iter([next(state.it)])),
                            state.end_tok_type,
                            state.single_item,
                        )
                    )
                    ret.negate = not ret.negate
                    return next_or_single(ret, state)

        rhs = next_tree(None, state)
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
    return next_or_single(
        Modify(value=so_far, op=tok.value, sym=rhs.value), state
    )


def next_tree_num(so_far, tok, state: ParseState):
    if so_far is not None:
        raise Exception(
            (
                "Parse error: I don't know how to deal with a %s " +
                "('%s') before a number (%s)."
            ) % (type(so_far), str(so_far), tok.value)

        )
    return next_or_single(Number(tok.value), state)


def next_tree_sym(so_far, tok, state: ParseState):
    if so_far is None:
        sym = tok
        return next_or_single(Symbol(sym.value), state)
    else:
        if type(so_far) == Number:
            return next_or_single(
                Modify(value=so_far, op="", sym=tok.value), state
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


def next_tree_fndef(so_far, tok, state: ParseState):
    body = [n for n in parse_peekable(state.it, EndFunctionDefToken)]
    return next_or_single(FunctionDef(body), state)


def next_tree_for_token(so_far, tok, state: ParseState):
    # We have decided at this point that any so_far we do have
    # is OK to pass on to the next person, so we get rid of
    # ~s, which just tell us to do exactly that.
    tok = swallow_continuations(tok, state.it)

    tok_type = type(tok)
    if tok_type == FunctionCallToken:
        return next_tree_fn(so_far, tok, state)
    elif tok_type == OperatorToken:
        return next_tree_op(so_far, tok, state)
    elif tok_type == NumberToken:
        return next_tree_num(so_far, tok, state)
    elif tok_type == SymbolToken:
        return next_tree_sym(so_far, tok, state)
    elif tok_type == SeparatorToken:
        return next_or_single(None, state)
    elif tok_type == StartFunctionDefToken:
        return next_tree_fndef(so_far, tok, state)
    else:
        raise Exception(
            "Parse error: the token %s is an unknown type (%s)" %
            (str(tok), tok_type.__name__)
        )


def next_tree(so_far, state: ParseState):

    # If we've hit the end of the stream, return what we have so far,
    # but if we have nothing so far, we can allow the StopIteration to
    # leak out when we try to get the next token.
    if so_far is not None:
        try:
            state.it.peek()
        except StopIteration:
            return so_far

    # Symbols and function calls signal the end of the
    # statement, unless they are followed by a ~.
    # Just peek and see whether the next token is a ~,
    # and if not, return immediately.
    if type(so_far) in (FunctionCall, Modify, Symbol):
        if type(state.it.peek()) != ContinuationToken:
            return so_far

    nx = next(state.it)

    if type(nx) == state.end_tok_type:
        if so_far is None:
            raise StopIteration()
        else:
            return so_far

    return next_tree_for_token(so_far, nx, state)


#: Iterable[Token]
def parse(tokens):
    return parse_peekable(Peekable(iter(tokens)), None)


def parse_peekable(it: Peekable, end_tok_type):
    while True:
        yield next_tree(None, ParseState(it, end_tok_type, False))
