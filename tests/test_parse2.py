import pytest
from graftlib.lex2 import (
    lex,
    NumberToken,
    StringToken,
    SymbolToken,
)
from graftlib.parse2 import parse

# --- Utils ---


def parsed(inp):
    return list(parse(lex(inp)))


# --- Parsing ---


def test_Empty_file_produces_nothing():
    assert parsed("") == []


def test_Number_is_parsed_as_expression():
    assert parsed("56;") == [NumberToken("56")]


def test_Missing_semicolon_is_an_error():
    with pytest.raises(
        Exception,
        message=r"Hit end of file - expected ';'."
    ):
        parsed("56")


def test_Sum_of_numbers_is_parsed_as_expression():
    assert (
        parsed("32 + 44;") ==
        [
            ("operation", "+", NumberToken("32"), NumberToken("44"))
        ]
    )


def test_Difference_of_symbol_and_number_is_parsed_as_expression():
    assert (
        parsed("foo - 44;") ==
        [
            ("operation", "-", SymbolToken("foo"), NumberToken("44"))
        ]
    )


def test_Multiplication_of_symbols_is_parsed_as_expression():
    assert (
        parsed("foo * bar;") ==
        [
            ("operation", "*", SymbolToken("foo"), SymbolToken("bar"))
        ]
    )


def test_Variable_assignment_gets_parsed():
    assert (
        parsed("x = 3;") ==
        [
            ("assignment", SymbolToken("x"), NumberToken("3"))
        ]
    )


def test_Function_call_with_no_args_gets_parsed():
    assert (
        parsed("print();") ==
        [
            ("call", SymbolToken("print"), [])
        ]
    )


def test_Function_call_with_various_args_gets_parsed():
    assert (
        parsed("print( 'a', 3, 4 / 12 );") ==
        [
            (
                "call",
                SymbolToken("print"),
                [
                    StringToken("a"),
                    NumberToken("3"),
                    ("operation", "/", NumberToken("4"), NumberToken("12"))
                ]
            )
        ]
    )


def test_Multiple_function_calls_with_no_args_get_parsed():
    assert (
        parsed("print()();") ==
        [
            ("call", ("call", SymbolToken("print"), []), [])
        ]
    )


def test_Multiple_function_calls_with_various_args_get_parsed():
    assert (
        parsed("print( 'a', 3, 4 / 12 )(512)();") ==
        [
            (
                "call",
                (
                    "call",
                    (
                        "call",
                        SymbolToken("print"),
                        [
                            StringToken("a"),
                            NumberToken("3"),
                            (
                                "operation",
                                "/",
                                NumberToken("4"),
                                NumberToken("12")
                            )
                        ]
                    ),
                    [
                        NumberToken("512")
                    ]
                ),
                []
            )
        ]
    )


def test_Assigning_to_a_number_is_an_error():
    with pytest.raises(
        Exception,
        message=r"You can't assign to anything except a symbol."
    ):
        parsed("3 = x;")


def test_Assigning_to_an_expression_is_an_error():
    with pytest.raises(
        Exception,
        message=r"You can't assign to anything except a symbol."
    ):
        parsed("x(4) = 5;")


def test_Empty_function_definition_gets_parsed():
    assert (
        parsed("{};") ==
        [
            ("function", [], [])
        ]
    )


def test_Missing_param_definition_with_colon_is_an_error():
    with pytest.raises(
        Exception,
        message=r"':' must be followed by '(' in a function."
    ):
        parsed("{:print(x););")


def test_Multiple_commands_parse_into_multiple_expressions():
    program = """
    x = 3;
    func = {:(a) print(a);};
    func(x);
    """
    assert (
        parsed(program) ==
        [
            ("assignment", SymbolToken('x'), NumberToken('3')),
            (
                "assignment",
                SymbolToken('func'),
                (
                    "function",
                    [SymbolToken('a')],
                    [
                        ("call", SymbolToken('print'), [SymbolToken('a')])
                    ]
                )
            ),
            ("call", SymbolToken('func'), [SymbolToken('x')])
        ]
    )


def test_Empty_function_definition_with_params_gets_parsed():
    assert (
        parsed("{:(aa, bb, cc, dd)};") ==
        [
            (
                "function",
                [
                    SymbolToken("aa"),
                    SymbolToken("bb"),
                    SymbolToken("cc"),
                    SymbolToken("dd")
                ],
                []
            )
        ]
    )


def test_Function_params_that_are_not_symbols_is_an_error():
    with pytest.raises(
        Exception,
        message=(
            "Only symbols are allowed in function parameter lists. " +
            "I found: " +
            "('operation', " +
            "'+', " +
            "SymbolToken(value='aa'), " +
            "NumberToken(value='3'))."
        )
    ):
        parsed("{:(aa + 3, d)};"),


def test_Function_definition_containing_commands_gets_parsed():
    assert (
        parsed('{print(3-4); a = "x"; print(a);};') ==
        [
            (
                "function",
                [],
                [
                    (
                        "call",
                        SymbolToken("print"),
                        [
                            (
                                "operation",
                                '-',
                                NumberToken('3'),
                                NumberToken('4')
                            )
                        ]
                    ),
                    ("assignment", SymbolToken("a"), StringToken("x")),
                    ("call", SymbolToken("print"), [SymbolToken("a")])
                ]
            )
        ]
    )


def test_Function_definition_with_params_and_commands_gets_parsed():
    assert (
        parsed('{:(x,yy)print(3-4); a = "x"; print(a);};') ==
        [
            (
                "function",
                [
                    SymbolToken("x"),
                    SymbolToken("yy")
                ],
                [
                    (
                        "call",
                        SymbolToken("print"),
                        [
                            (
                                "operation",
                                '-',
                                NumberToken('3'),
                                NumberToken('4')
                            )
                        ]
                    ),
                    ("assignment", SymbolToken("a"), StringToken("x")),
                    ("call", SymbolToken("print"), [SymbolToken("a")])
                ]
            )
        ]
    )


def test_A_complex_example_program_parses():
    example = """
        double =
            {:(x)
                2 * x;
            };

        num1 = 3;
        num2 = double( num );

        answer =
            if( greater_than( num2, 5 ),
                {"LARGE!"},
                {"small."}
            );

        print( answer );
    """
    parsed(example)
