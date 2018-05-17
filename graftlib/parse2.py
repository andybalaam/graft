from typing import List
import attr

from graftlib.peekablestream import PeekableStream
from graftlib.lex2 import (
    AssignmentToken,
    EndFunctionDefToken,
    EndParamListToken,
    ListSeparatorToken,
    NumberToken,
    OperatorToken,
    ParamListPreludeToken,
    StartFunctionDefToken,
    StartParamListToken,
    StatementSeparatorToken,
    StringToken,
    SymbolToken,
)


@attr.s
class AssignmentTree:
    symbol = attr.ib()
    value = attr.ib()


@attr.s
class NumberTree:
    value: str = attr.ib()


@attr.s
class FunctionCallTree:
    fn = attr.ib()
    args: List = attr.ib()


@attr.s
class FunctionDefTree:
    params: List = attr.ib()
    body: List = attr.ib()


@attr.s
class OperationTree:
    operation: str = attr.ib()
    symbol = attr.ib()
    new_value = attr.ib()


@attr.s
class StringTree:
    value: str = attr.ib()


@attr.s
class SymbolTree:
    value: str = attr.ib()


class Parser:
    def __init__(self, tokens, stop_at):
        self.tokens = tokens
        self.stop_at = stop_at

    def next_expression(self, prev):
        self.fail_if_at_end(";")
        tok = self.tokens.next
        typ = type(tok)
        if typ in self.stop_at:
            return prev
        self.tokens.move_next()
        if typ == NumberToken and prev is None:
            return self.next_expression(NumberTree(tok.value))
        elif typ == StringToken and prev is None:
            return self.next_expression(StringTree(tok.value))
        elif typ == SymbolToken and prev is None:
            return self.next_expression(SymbolTree(tok.value))
        elif typ == OperatorToken:
            nxt = self.next_expression(None)
            return self.next_expression(OperationTree(tok.value, prev, nxt))
        elif typ == StartParamListToken:
            args = self.multiple_expressions(
                ListSeparatorToken, EndParamListToken)
            return self.next_expression(FunctionCallTree(prev, args))
        elif typ == StartFunctionDefToken:
            params = self.parameters_list()
            body = self.multiple_expressions(
                StatementSeparatorToken, EndFunctionDefToken)
            return self.next_expression(FunctionDefTree(params, body))
        elif typ == AssignmentToken:
            if type(prev) != SymbolTree:
                raise Exception(
                    "You can't assign to anything except a symbol.")
            nxt = self.next_expression(None)
            return self.next_expression(AssignmentTree(prev, nxt))
        else:
            raise Exception("Unexpected token: " + str(tok))

    def parameters_list(self):
        if type(self.tokens.next) != ParamListPreludeToken:
            return []  # If there's no colon, this function takes no args
        self.tokens.move_next()
        typ = type(self.tokens.next)
        if typ != StartParamListToken:
            raise Exception("':' must be followed by '(' in a function.")
        self.tokens.move_next()
        ret = self.multiple_expressions(ListSeparatorToken, EndParamListToken)
        for param in ret:
            if type(param) != SymbolTree:
                raise Exception(
                    "Only symbols are allowed in function parameter lists." +
                    " I found: " + str(param) + "."
                )
        return ret

    def multiple_expressions(self, sep, end):
        ret = []
        self.fail_if_at_end(end)
        typ = type(self.tokens.next)
        if typ == end:
            self.tokens.move_next()
        else:
            arg_parser = Parser(self.tokens, (sep, end))
            while typ != end:
                p = arg_parser.next_expression(None)
                if p is not None:
                    ret.append(p)
                typ = type(self.tokens.next)
                self.tokens.move_next()
                self.fail_if_at_end(end)
        return ret

    def fail_if_at_end(self, expected):
        if self.tokens.next is None:
            raise Exception("Hit end of file - expected '%s'." % expected)


def parse(tokens_iterator):
    parser = Parser(
        PeekableStream(tokens_iterator),
        (StatementSeparatorToken,)
    )
    while parser.tokens.next is not None:
        p = parser.next_expression(None)
        if p is not None:
            yield p
        parser.tokens.move_next()
