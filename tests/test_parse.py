from typing import Iterable
from graftlib.lex import lex
from graftlib.parse import (
    FunctionCall,
    Modify,
    Number,
    Symbol,
    parse,
)


def do_parse(chars: Iterable[str]):
    return list(parse(lex(chars)))


def test_function_calls_are_parsed():
    assert do_parse(":S") == [FunctionCall("S")]


def test_symbols_are_parsed():
    assert do_parse("s") == [Symbol("s")]


def test_function_call_then_increment_is_parsed():
    assert (
        do_parse(":S+d") ==
        [
            FunctionCall("S"),
            Modify(sym="d", op="+", value=Number("10"))
        ]
    )


def test_function_call_then_add_is_parsed():
    assert (
        do_parse(":S95+d") ==
        [
            FunctionCall("S"),
            Modify(sym="d", op="+", value=Number("95"))
        ]
    )


def test_continuation_extends_previous_item_into_next():
    assert (
        do_parse(":R~+d:S") ==
        [
            Modify(
                sym="d",
                op="+",
                value=FunctionCall("R"),
            ),
            FunctionCall("S"),
        ]
    )
