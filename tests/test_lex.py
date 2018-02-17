from typing import Iterable
from graftlib.lex import (
    NumberToken,
    SymbolToken,
    lex,
)


def do_lex(chars: Iterable[str]):
    return list(lex(chars))


def test_symbol_is_lexed():
    assert do_lex("d") == [SymbolToken("d")]
    assert do_lex("_d") == [SymbolToken("_d")]


def test_number_and_symbol_are_lexed_separately():
    assert do_lex("3d") == [NumberToken("3"), SymbolToken("d")]
