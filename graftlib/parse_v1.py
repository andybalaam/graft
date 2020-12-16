from typing import List, Optional
from graftlib.labeltree import LabelTree
from graftlib.lex_v1 import (
    ContinuationToken,
    EndFunctionDefToken,
    FunctionCallToken,
    LabelToken,
    NumberToken,
    OperatorToken,
    SeparatorToken,
    StartFunctionDefToken,
    SymbolToken,
)
from graftlib.peekable import Peekable
import attr


@attr.s
class FunctionCall:
    fn = attr.ib()
    repeat: Optional = attr.ib(default=1)


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
    negative: bool = attr.ib(default=False)

    def negate(self):
        self.negative = not self.negative


@attr.s
class Modify:
    sym: str = attr.ib()
    op: str = attr.ib()
    value = attr.ib(None, converter=lambda x: Number("10") if x is None else x)


@attr.s
class Symbol:
    value: str = attr.ib()


def _swallow_continuations(tok, it: Peekable):
    while type(tok) == ContinuationToken:
        tok = next(it)
    return tok


@attr.s
class _Parser:
    it: Peekable = attr.ib()
    end_tok_type = attr.ib()
    single_item: bool = attr.ib()

    def greedy(self):
        return _Parser(self.it, self.end_tok_type, True)

    def next_or_single(self, value):
        if self.single_item:
            return value
        else:
            return self.continuing_tree(value)

    def next_tree_fn(self, so_far, tok):
        fn = self.greedy().next_tree()
        if so_far is None:
            repeat = 1
        elif type(so_far) == Number:
            try:
                repeat = int(so_far.value)
            except ValueError:
                raise Exception(
                    (
                        "Parse error: repeat argument before function " +
                        "call (%s) must be an integer, but it was %s."
                    ) % (tok.value, str(so_far))
                )
        else:
            raise Exception(
                (
                    "Parse error: repeat argument before function call (%s) " +
                    "must be a number, but it was %s, which is a %s."
                ) % (tok.value, type(so_far), str(so_far))
            )

        return self.next_or_single(FunctionCall(fn, repeat))

    def next_tree_op(self, so_far, tok):
        try:
            if so_far is None:
                if tok.value == "-":
                    if type(self.it.peek()) == NumberToken:
                        ret: Number = self.greedy().next_tree()
                        ret.negate()
                        return self.next_or_single(ret)

            rhs = self.next_tree()
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

        return self.next_or_single(
            Modify(value=so_far, op=tok.value, sym=rhs.value)
        )

    def next_tree_num(self, so_far, tok):
        if so_far is not None:
            raise Exception(
                (
                    "Parse error: I don't know how to deal with a %s " +
                    "('%s') before a number (%s)."
                ) % (type(so_far), str(so_far), tok.value)
            )
        return self.next_or_single(Number(tok.value))

    def next_tree_sym(self, so_far, tok):
        if so_far is None:
            sym = tok
            return self.next_or_single(Symbol(sym.value))
        else:
            if type(so_far) in (Number, Symbol):
                return self.next_or_single(
                    Modify(value=so_far, op="", sym=tok.value)
                )
            else:
                raise Exception(
                    (
                        "Parse error: don't know what to do with " +
                        "'{so_far}' before the symbol {tok}.  You can " +
                        "have a number (or symbol then ~) before a symbol, " +
                        "or an operator like +, but not a {type_so_far}."
                    ).format(
                        so_far=so_far,
                        tok=tok.value,
                        type_so_far=type(so_far).__name__,
                    )
                )

    def next_tree_fndef(self, _so_far, _tok):
        body = [n for n in _parse_peekable(self.it, EndFunctionDefToken)]
        return self.next_or_single(FunctionDef(body))

    def next_tree_label(self, _so_far, _tok):
        return LabelTree()

    def next_tree_for_token(self, so_far, tok):
        # We have decided at this point that any so_far we do have
        # is OK to pass on to the next person, so we get rid of
        # ~s, which just tell us to do exactly that.
        tok = _swallow_continuations(tok, self.it)

        tok_type = type(tok)
        if tok_type == FunctionCallToken:
            return self.next_tree_fn(so_far, tok)
        elif tok_type == OperatorToken:
            return self.next_tree_op(so_far, tok)
        elif tok_type == NumberToken:
            return self.next_tree_num(so_far, tok)
        elif tok_type == SymbolToken:
            return self.next_tree_sym(so_far, tok)
        elif tok_type == SeparatorToken:
            return self.next_or_single(None)
        elif tok_type == StartFunctionDefToken:
            return self.next_tree_fndef(so_far, tok)
        elif tok_type == LabelToken:
            return self.next_tree_label(so_far, tok)
        else:
            raise Exception(
                "Parse error: the token %s is an unknown type (%s)" %
                (str(tok), tok_type.__name__)
            )

    def continuing_tree(self, so_far):

        # If we've hit the end of the stream, return what we have so far,
        # but if we have nothing so far, we can allow the StopIteration to
        # leak out when we try to get the next token.
        if so_far is not None:
            try:
                self.it.peek()
            except StopIteration:
                return so_far

        # Symbols and function calls signal the end of the
        # statement, unless they are followed by a ~.
        # Just peek and see whether the next token is a ~,
        # and if not, return immediately.
        if type(so_far) in (FunctionCall, Modify, Symbol):
            if type(self.it.peek()) != ContinuationToken:
                return so_far

        nx = next(self.it)

        if type(nx) == self.end_tok_type:
            if so_far is None:
                raise StopIteration()
            else:
                return so_far

        return self.next_tree_for_token(so_far, nx)

    def next_tree(self):
        return self.continuing_tree(None)


#: Iterable[Token]
def parse_v1(tokens):
    return _parse_peekable(Peekable(iter(tokens)), None)


def _parse_peekable(it: Peekable, end_tok_type):
    while True:
        yield _Parser(it, end_tok_type, False).next_tree()
