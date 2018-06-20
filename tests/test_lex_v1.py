from typing import Iterable
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
    lex,
)


def do_lex(chars: Iterable[str]):
    return list(lex(chars))


def test_symbol_is_lexed():
    assert do_lex("d") == [SymbolToken("d")]
    assert do_lex("_d") == [SymbolToken("_d")]


def test_label_is_lexed():
    assert do_lex("^") == [LabelToken()]


def test_number_and_symbol_are_lexed_separately():
    assert do_lex("3d") == [NumberToken("3"), SymbolToken("d")]


def test_operator_followed_by_number_makes_two_tokens():
    assert (
        do_lex("3+90") ==
        [NumberToken("3"), OperatorToken("+"), NumberToken("90")]
    )


def test_negative_sign_is_lexed_as_operator_number():
    assert do_lex("-90") == [OperatorToken("-"), NumberToken("90")]
    assert do_lex("-0.03") == [OperatorToken("-"), NumberToken("0.03")]


def test_functions_are_lexed():
    assert (
        do_lex(":S3") ==
        [
            FunctionCallToken(),
            SymbolToken("S"),
            NumberToken("3"),
        ]
    )
    assert (
        do_lex("3:S") ==
        [
            NumberToken("3"),
            FunctionCallToken(),
            SymbolToken("S"),
        ]
    )


def test_operators_are_lexed():
    assert (
        do_lex("3=d") ==
        [NumberToken("3"), OperatorToken("="), SymbolToken("d")]
    )
    assert (
        do_lex("3-d") ==
        [NumberToken("3"), OperatorToken("-"), SymbolToken("d")]
    )
    assert (
        do_lex("3/d") ==
        [NumberToken("3"), OperatorToken("/"), SymbolToken("d")]
    )


def test_decimals_are_lexed():
    assert do_lex("1.1d") == [NumberToken("1.1"), SymbolToken("d")]


def test_braces_are_lexed():
    assert do_lex("{") == [StartFunctionDefToken()]
    assert (
        do_lex("34{:S}") ==
        [
            NumberToken("34"),
            StartFunctionDefToken(),
            FunctionCallToken(),
            SymbolToken("S"),
            EndFunctionDefToken(),
        ]
    )


def test_function_call_then_add_is_lexed():
    assert (
        do_lex(":S95+_ab_c") ==
        [
            FunctionCallToken(),
            SymbolToken("S"),
            NumberToken("95"),
            OperatorToken("+"),
            SymbolToken("_ab_c"),
        ]
    )


def test_continuation_is_lexed():
    assert (
        do_lex(":R~+d:S") ==
        [
            FunctionCallToken(),
            SymbolToken("R"),
            ContinuationToken(),
            OperatorToken("+"),
            SymbolToken("d"),
            FunctionCallToken(),
            SymbolToken("S"),
        ]
    )


def test_semicolon_is_lexed_separately():
    assert (
        do_lex("/;ab") ==
        [
            OperatorToken("/"),
            SeparatorToken(),
            SymbolToken("ab"),
        ]
    )
