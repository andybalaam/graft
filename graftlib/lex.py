from typing import Iterable, Iterator
import typing
import re
import attr


from graftlib.peekable import Peekable


Pattern = typing.re.Pattern


@attr.s
class ContinuationToken:
    pass


@attr.s
class EndFunctionDefToken:
    pass


@attr.s
class FunctionCallToken:
    pass


@attr.s
class NumberToken:
    value: str = attr.ib()


@attr.s
class OperatorToken:
    value: str = attr.ib()


@attr.s
class SeparatorToken:
    pass


@attr.s
class StartFunctionDefToken:
    pass


@attr.s
class SymbolToken:
    value: str = attr.ib()


def collect(c: str, it: Iterator[str], regex: Pattern) -> str:
    ret = c
    try:
        while regex.match(it.peek()):
            ch = next(it)
            ret += ch
    except StopIteration:
        # We are finished - return as normal and the next next() call
        # will throw again.
        pass
    return ret


tilda: Pattern = re.compile("~")
close_brace: Pattern = re.compile("}")
digit: Pattern = re.compile("[0-9.]")
colon: Pattern = re.compile(":")
open_brace: Pattern = re.compile("{")
operator: Pattern = re.compile("[-+/=]")
semicolon: Pattern = re.compile(";")
symbol_letter: Pattern = re.compile("[_a-zA-Z]")


def next_token(c: str, it: Iterable[str]):
    if digit.match(c):
        return NumberToken(collect(c, it, digit))
    elif colon.match(c):
        return FunctionCallToken()
    elif operator.match(c):
        return OperatorToken(collect(c, it, operator))
    elif tilda.match(c):
        return ContinuationToken()
    elif semicolon.match(c):
        return SeparatorToken()
    elif open_brace.match(c):
        return StartFunctionDefToken()
    elif close_brace.match(c):
        return EndFunctionDefToken()
    else:
        return SymbolToken(collect(c, it, symbol_letter))


def lex(chars: Iterable[str]):
    it = Peekable(iter(chars))
    while True:
        c = next(it)
        yield next_token(c, it)
