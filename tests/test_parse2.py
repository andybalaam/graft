import pytest
from graftlib.lex2 import (
    lex,
)
from graftlib.parse2 import (
    parse,
    FunctionCallTree,
    NumberTree,
    OperationTree,
    StringTree,
    SymbolTree,
)

# --- Utils ---


def parsed(inp):
    return list(parse(lex(inp)))


# --- Parsing ---


def test_Empty_file_produces_nothing():
    assert parsed("") == []


def test_Number_is_parsed_as_expression():
    assert parsed("56;") == [NumberTree("56")]


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
            OperationTree("+", NumberTree("32"), NumberTree("44"))
        ]
    )


def test_Difference_of_symbol_and_number_is_parsed_as_expression():
    assert (
        parsed("foo - 44;") ==
        [
            OperationTree("-", SymbolTree("foo"), NumberTree("44"))
        ]
    )


def test_Multiplication_of_symbols_is_parsed_as_expression():
    assert (
        parsed("foo * bar;") ==
        [
            OperationTree("*", SymbolTree("foo"), SymbolTree("bar"))
        ]
    )


def test_Variable_assignment_gets_parsed():
    assert (
        parsed("x = 3;") ==
        [
            ("assignment", SymbolTree("x"), NumberTree("3"))
        ]
    )


def test_Function_call_with_no_args_gets_parsed():
    assert (
        parsed("print();") ==
        [
            FunctionCallTree(SymbolTree("print"), [])
        ]
    )


def test_Function_call_with_various_args_gets_parsed():
    assert (
        parsed("print( 'a', 3, 4 / 12 );") ==
        [
            FunctionCallTree(
                SymbolTree("print"),
                [
                    StringTree("a"),
                    NumberTree("3"),
                    OperationTree("/", NumberTree("4"), NumberTree("12"))
                ]
            )
        ]
    )


def test_Multiple_function_calls_with_no_args_get_parsed():
    assert (
        parsed("print()();") ==
        [
            FunctionCallTree(FunctionCallTree(SymbolTree("print"), []), [])
        ]
    )


def test_Multiple_function_calls_with_various_args_get_parsed():
    assert (
        parsed("print( 'a', 3, 4 / 12 )(512)();") ==
        [
            FunctionCallTree(
                FunctionCallTree(
                    FunctionCallTree(
                        SymbolTree("print"),
                        [
                            StringTree("a"),
                            NumberTree("3"),
                            OperationTree(
                                "/",
                                NumberTree("4"),
                                NumberTree("12")
                            )
                        ]
                    ),
                    [
                        NumberTree("512")
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
            ("assignment", SymbolTree('x'), NumberTree('3')),
            (
                "assignment",
                SymbolTree('func'),
                (
                    "function",
                    [SymbolTree('a')],
                    [
                        FunctionCallTree(
                            SymbolTree('print'), [SymbolTree('a')])
                    ]
                )
            ),
            FunctionCallTree(SymbolTree('func'), [SymbolTree('x')])
        ]
    )


def test_Empty_function_definition_with_params_gets_parsed():
    assert (
        parsed("{:(aa, bb, cc, dd)};") ==
        [
            (
                "function",
                [
                    SymbolTree("aa"),
                    SymbolTree("bb"),
                    SymbolTree("cc"),
                    SymbolTree("dd")
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
            "SymbolTree(value='aa'), " +
            "NumberTree(value='3'))."
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
                    FunctionCallTree(
                        SymbolTree("print"),
                        [
                            OperationTree(
                                '-',
                                NumberTree('3'),
                                NumberTree('4')
                            )
                        ]
                    ),
                    ("assignment", SymbolTree("a"), StringTree("x")),
                    FunctionCallTree(SymbolTree("print"), [SymbolTree("a")])
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
                    SymbolTree("x"),
                    SymbolTree("yy")
                ],
                [
                    FunctionCallTree(
                        SymbolTree("print"),
                        [
                            OperationTree(
                                '-',
                                NumberTree('3'),
                                NumberTree('4')
                            )
                        ]
                    ),
                    ("assignment", SymbolTree("a"), StringTree("x")),
                    FunctionCallTree(SymbolTree("print"), [SymbolTree("a")])
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
