from typing import Iterable
from graftlib.lex import lex
from graftlib.parse import (
    FunctionCall,
    FunctionDef,
    Modify,
    Number,
    Symbol,
    parse,
)
import pytest


def do_parse(chars: Iterable[str]):
    return list(parse(lex(chars)))


def test_function_calls_are_parsed():
    assert do_parse(":S") == [FunctionCall(Symbol("S"))]


def test_symbols_are_parsed():
    assert do_parse("s") == [Symbol("s")]


def test_function_call_then_increment_is_parsed():
    assert (
        do_parse(":S+d") ==
        [
            FunctionCall(Symbol("S")),
            Modify(sym="d", op="+", value=Number("10"))
        ]
    )


def test_assignment_is_parsed():
    assert (
        do_parse("3=d") ==
        [
            Modify(sym="d", op="=", value=Number("3"))
        ]
    )


def test_number_being_added_is_parsed():
    assert (
        do_parse("3+d") ==
        [
            Modify(sym="d", op="+", value=Number("3"))
        ]
    )


def test_number_being_subtracted_is_parsed():
    assert (
        do_parse("3-d") ==
        [
            Modify(sym="d", op="-", value=Number("3"))
        ]
    )


def test_function_call_passed_to_operator_is_parsed():
    assert (
        do_parse(":R~+d") ==
        [
            Modify(sym="d", op="+", value=FunctionCall(Symbol("R")))
        ]
    )


def test_number_being_divided_is_parsed():
    assert (
        do_parse("3/d") ==
        [
            Modify(sym="d", op="/", value=Number("3"))
        ]
    )


def test_negative_number_is_parsed():
    assert do_parse("-3") == [Number("3", negate=True)]


def test_plus_not_allowed_before_number():
    with pytest.raises(Exception) as e1:
        do_parse("+3")
    assert "after '+' I found a Number" in str(e1)


def test_negative_number_in_middle_of_other_expressions_is_parsed():
    assert (
        do_parse(":S-3+d") ==
        [
            FunctionCall(Symbol("S")),
            Modify(
                sym="d",
                op="+",
                value=Number("3", negate=True)
            )
        ]
    )


def test_trailing_operator_is_an_error():
    with pytest.raises(Exception) as e1:
        do_parse("+")
    assert "operator (+) at the end" in str(e1)
    with pytest.raises(Exception) as e2:
        do_parse("3+")
    assert "operator (+) at the end" in str(e2)
    with pytest.raises(Exception) as e3:
        do_parse("a~+")
    assert "operator (+) at the end" in str(e3)


def test_number_being_multiplied_is_parsed():
    assert (
        do_parse("3.5d") ==
        [
            Modify(sym="d", op="", value=Number("3.5"))
        ]
    )


def test_function_call_then_add_is_parsed():
    assert (
        do_parse(":S95+d") ==
        [
            FunctionCall(Symbol("S")),
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
                value=FunctionCall(Symbol("R")),
            ),
            FunctionCall(Symbol("S")),
        ]
    )


def test_semicolon_to_separate_statements():
    assert (
        do_parse("s;s") ==
        [
            Symbol("s"),
            Symbol("s"),
        ]
    )


def test_empty_function_def():
    assert (
        do_parse("{}") ==
        [
            FunctionDef([]),
        ]
    )


def test_nonempty_function_def():
    assert (
        do_parse("{+d:S}") ==
        [
            FunctionDef(
                [
                    Modify(
                        sym="d",
                        op="+",
                        value=Number("10"),
                    ),
                    FunctionCall(Symbol("S")),
                ]
            ),
        ]
    )


# def test_nonempty_function_def_repeated():
#     assert (
#         do_parse("3:{+d:S}") ==
#         [
#             FunctionDef(),
#         ]
#     )
#
#
# def test_repeated_call_function():
#     assert (
#         do_parse("3:S") ==
#         [
#             FunctionCall(3, Symbol("S")),
#         ]
#     )
#
#
# def test_repeated_call_function_def():
#     assert (
#         do_parse("3:{+d:S}") ==
#         [
#             FunctionCall(
#                 3,
#                 FunctionDef(
#                     [
#                         Modify(
#                             sym="d",
#                             op="+",
#                             value=Number("10"),
#                         ),
#                         FunctionCall(3, Symbol("S")),
#                     ]
#                 ),
#             ),
#         ]
#     )
#
#
# def test_function_def_assigned():
#     assert (
#         do_parse("{+d:S}=x") ==
#         [
#             Modify(
#                 sym="x",
#                 op="=",
#                 value=FunctionDef(
#                         [
#                             Modify(
#                                 sym="d",
#                                 op="+",
#                                 value=Number("10"),
#                             ),
#                             FunctionCall(3, Symbol("S")),
#                         ]
#                     ),
#             ),
#         ]
#     )
