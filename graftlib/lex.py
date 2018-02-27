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
class FunctionToken:
    value: str = attr.ib()


@attr.s
class NumberToken:
    value: str = attr.ib()


@attr.s
class OperatorToken:
    value: str = attr.ib()


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


continuation: Pattern = re.compile("~")
digit: Pattern = re.compile("[0-9.]")
function: Pattern = re.compile(":")
operator: Pattern = re.compile("[-+<>=]")
symbol_letter: Pattern = re.compile("[_a-zA-Z]")


def next_token(c: str, it: Iterable[str]):
    if digit.match(c):
        return NumberToken(collect(c, it, digit))
    elif function.match(c):
        return FunctionToken(collect("", it, symbol_letter))
    elif operator.match(c):
        return OperatorToken(collect(c, it, operator))
    elif continuation.match(c):
        return ContinuationToken()
    else:
        return SymbolToken(collect(c, it, symbol_letter))


def lex(chars: Iterable[str]):
    it = Peekable(iter(chars))
    while True:
        c = next(it)
        yield next_token(c, it)
