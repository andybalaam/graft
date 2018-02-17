from typing import Iterable, Iterator, Optional
import typing
import re
import attr


Pattern = typing.re.Pattern


@attr.s
class Peekable:
    _it: Iterator = attr.ib()
    _nxt = attr.ib(None)

    def __attrs_post_init__(self) -> None:
        self._nxt = self.move_next()

    def move_next(self) -> Optional[str]:
        try:
            return next(self._it)
        except StopIteration:
            return None

    def peek(self) -> str:
        if self._nxt is None:
            raise StopIteration()
        else:
            return self._nxt

    def __iter__(self) -> Iterator[str]:
        return self

    def __next__(self) -> str:
        if self._nxt is None:
            raise StopIteration()
        else:
            ret = self._nxt
            self._nxt = self.move_next()
            return ret


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


digit: Pattern = re.compile("[0-9]")
function: Pattern = re.compile(":")
operator: Pattern = re.compile("[+-<>=]")
symbol_letter: Pattern = re.compile("[_a-zA-Z]")


def next_token(c: str, it: Iterable[str]):
    if digit.match(c):
        return NumberToken(collect(c, it, digit))
    elif function.match(c):
        return FunctionToken(collect("", it, symbol_letter))
    elif operator.match(c):
        return OperatorToken(collect(c, it, operator))
    else:
        return SymbolToken(collect(c, it, symbol_letter))


def lex(chars: Iterable[str]):
    it = Peekable(iter(chars))
    while True:
        c = next(it)
        yield next_token(c, it)
