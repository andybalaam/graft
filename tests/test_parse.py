from typing import Iterable
from graftlib.lex import (
    FunctionToken,
    NumberToken,
    OperatorToken,
    SymbolToken,
    lex,
)
from graftlib.parse import (
    FunctionCall,
    Modify,
    Symbol,
    parse,
)


def do_parse(chars: Iterable[str]):
    return list(parse(lex(chars)))


def test_function_calls_are_parsed():
    assert do_parse(":s") == [FunctionCall(FunctionToken("s"))]


def test_symbols_are_parsed():
    assert do_parse("s") == [Symbol(SymbolToken("s"))]


def test_function_call_then_increment_is_parsed():
    assert (
        do_parse(":s+d") ==
        [
            FunctionCall(FunctionToken("s")),
            Modify(
                sym=SymbolToken("d"),
                op=OperatorToken("+"),
                value=NumberToken("10"),
            )
        ]
    )


def test_function_call_then_add_is_parsed():
    assert (
        do_parse(":s95+d") ==
        [
            FunctionCall(FunctionToken("s")),
            Modify(
                sym=SymbolToken("d"),
                op=OperatorToken("+"),
                value=NumberToken("95"),
            )
        ]
    )
