from graftlib.lex2 import lex

# --- Utils ---


def lexed(inp):
    return list(lex(inp))


# --- Lexing ---


def test_Empty_file_produces_nothing():
    assert lexed("") == []


def test_Open_bracket_produces_open_bracket_token():
    assert lexed("(") == [("(", "")]


def test_Close_bracket_produces_close_bracket_token():
    assert lexed(")") == [(")", "")]


def test_Open_brace_produces_open_brace_token():
    assert lexed("{") == [("{", "")]


def test_Close_brace_produces_close_brace_token():
    assert lexed("}") == [("}", "")]


def test_Multiple_brackets_become_multiple_tokens():
    assert lexed("()") == [("(", ""), (")", "")]


def test_Single_letter_becomes_a_symbol_token():
    assert lexed("a") == [("symbol", "a")]


def test_Multiple_letters_become_a_symbol_token():
    assert lexed("foo") == [("symbol", "foo")]


def test_A_symbol_followed_by_a_bracket_becomes_two_tokens():
    assert lexed("foo(") == [("symbol", "foo"), ("(", "")]


def test_Items_separated_by_spaces_become_separate_tokens():
    assert (
        lexed("foo bar ( ") ==
        [
            ("symbol", "foo"),
            ("symbol", "bar"),
            ("(", "")
        ]
    )


def test_Items_separated_by_newlines_become_separate_tokens():
    assert (
        lexed("foo\nbar") ==
        [
            ("symbol", "foo"),
            ("symbol", "bar")
        ]
    )


def test_Symbols_may_contain_numbers_and_underscores():
    assert (
        lexed("foo2_bar ( ") ==
        [
            ("symbol", "foo2_bar"),
            ("(", "")
        ]
    )


def test_Symbols_may_start_with_underscores():
    assert (
        lexed("_foo2_bar ( ") ==
        [
            ("symbol", "_foo2_bar"),
            ("(", "")
        ]
    )


def test_Integers_are_parsed_into_number_tokens():
    assert lexed("128") == [("number", "128")]


def test_Floating_points_are_parsed_into_number_tokens():
    assert lexed("12.8") == [("number", "12.8")]


def test_Leading_decimal_point_produces_number_token():
    assert lexed(".812") == [("number", ".812")]


def test_Double_quoted_values_produce_string_tokens():
    assert lexed('"foo"') == [("string", 'foo')]


def test_Single_quoted_values_produce_string_tokens():
    assert lexed("'foo'") == [("string", 'foo')]


def test_Different_quote_types_allow_the_other_type_inside():
    assert lexed("'f\"oo'") == [("string", 'f"oo')]
    assert lexed('"f\'oo"') == [("string", "f'oo")]


def test_Empty_quotes_produce_an_empty_string_token():
    assert lexed('""') == [("string", '')]


def test_An_unfinished_string_is_an_error():
    try:
        lexed('"foo')
        fail("Should throw")
    except Exception as e:
        assert str(e) == "A string ran off the end of the program."


def test_Commas_produce_comma_tokens():
    assert lexed(",") == [(",", "")]


def test_Equals_produces_an_equals_token():
    assert lexed("=") == [("=", "")]


def test_Semicolons_produce_semicolon_tokens():
    assert lexed(";") == [(";", "")]


def test_Colons_produce_colon_tokens():
    assert lexed(":") == [(":", "")]


def test_Arithmetic_operators_produce_operation_tokens():
    assert lexed("+") == [("operation", "+")]
    assert lexed("-") == [("operation", "-")]
    assert lexed("*") == [("operation", "*")]
    assert lexed("/") == [("operation", "/")]


def test_Multiple_token_types_can_be_combined():
    assert (
        lexed('frobnicate( "Hello" + name, 4 / 5.0);') ==
        [
            ("symbol", "frobnicate"),
            ("(", ""),
            ("string", "Hello"),
            ("operation", "+"),
            ("symbol", "name"),
            (",", ""),
            ("number", "4"),
            ("operation", "/"),
            ("number", "5.0"),
            (")", ""),
            (";", "")
        ]
    )


def test_A_complex_example_program_lexes():
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
    lexed(example)


def test_Tabs_are_an_error():
    try:
        lexed("aaa\tbbb")
        fail("Should throw")
    except Exception as e:
        assert str(e) == "Tab characters are not allowed in Cell."
