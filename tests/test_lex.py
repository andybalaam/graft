from typing import Iterable
from graftlib.lex import (
    FunctionToken,
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


def test_functions_are_lexed():
    assert do_lex(":s3") == [FunctionToken("s"), NumberToken("3")]
    assert do_lex("3:s") == [NumberToken("3"), FunctionToken("s")]
