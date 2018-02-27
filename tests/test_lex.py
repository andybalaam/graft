from typing import Iterable
from graftlib.lex import (
    ContinuationToken,
    FunctionToken,
    NumberToken,
    OperatorToken,
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


def test_operator_followed_by_number_makes_two_tokens():
    assert (
        do_lex("3+90") ==
        [NumberToken("3"), OperatorToken("+"), NumberToken("90")]
    )


# def test_negative_number_is_lexed():
#     assert do_lex("-90") == [NumberToken("-90")]
#     assert do_lex("-0.03") == [NumberToken("-0.03")]


def test_functions_are_lexed():
    assert do_lex(":S3") == [FunctionToken("S"), NumberToken("3")]
    assert do_lex("3:S") == [NumberToken("3"), FunctionToken("S")]


def test_operators_are_lexed():
    assert (
        do_lex("3=d") ==
        [NumberToken("3"), OperatorToken("="), SymbolToken("d")]
    )


def test_decimals_are_lexed():
    assert do_lex("1.1d") == [NumberToken("1.1"), SymbolToken("d")]


def test_function_call_then_add_is_lexed():
    assert (
        do_lex(":S95+_ab_c") ==
        [
            FunctionToken("S"),
            NumberToken("95"),
            OperatorToken("+"),
            SymbolToken("_ab_c"),
        ]
    )


def test_continuation_is_lexed():
    assert (
        do_lex(":R~+d:S") ==
        [
            FunctionToken("R"),
            ContinuationToken(),
            OperatorToken("+"),
            SymbolToken("d"),
            FunctionToken("S"),
        ]
    )
