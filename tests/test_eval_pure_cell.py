import pytest
from graftlib.lex_cell import lex
from graftlib.parse_cell import FunctionCallTree, parse
from graftlib.eval_cell import (
    NativeFunctionValue,
    NoneValue,
    NumberValue,
    StringValue,
    eval2_expr,
    eval_list,
)
from graftlib.env import Env


# --- Utils ---


def evald(inp, env=None):
    if env is None:
        env = Env(None, None)
    return eval_list(parse(lex(inp)), env)


def assert_prog_fails(program, error, env=None):
    with pytest.raises(
        Exception,
        match=error
    ):
        evald(program, env)


# --- Evaluating ---


def test_Evaluating_an_empty_program_gives_none():
    assert evald("") == NoneValue()


def test_Evaluating_a_primitive_returns_itself():
    assert evald("3") == NumberValue(3)
    assert evald("3.1") == NumberValue(3.1)
    assert evald("'foo'") == StringValue("foo")


def test_Arithmetic_expressions_come_out_correct():
    assert evald("3+4") == NumberValue(7)
    assert evald("3-4") == NumberValue(-1)
    assert evald("3*4") == NumberValue(12)
    assert evald("3/4") == NumberValue(0.75)


def test_Referring_to_an_unknown_symbol_yields_0():
    assert evald("unkn") == NumberValue(0.0)


def test_Can_define_a_value_and_retrieve_it():
    assert evald("x=30 x ") == NumberValue(30)
    assert evald("y='foo' y") == StringValue("foo")


def test_Modifying_a_value_is_an_error():
    assert_prog_fails("x=30 x=10", "Not allowed to re-assign symbol 'x'.")


def test_Value_of_an_assignment_is_the_value_assigned():
    assert evald("x=31") == NumberValue(31)


def test_None_evaluates_to_None():
    assert eval2_expr(Env(None, None), NoneValue()) == NoneValue()


def test_Calling_a_function_returns_its_last_value():
    assert (
        evald("{10 11}()") ==
        NumberValue(11)
    )


def test_Body_of_a_function_can_use_arg_values():
    assert (
        evald("{:(x,y)x+y}(100,1)") ==
        NumberValue(101)
    )


def test_Can_hold_a_reference_to_a_function_and_call_it():
    assert (
        evald(
            """
            add={:(x,y)x+y}
            add(20,2.2)
            """
        ) ==
        NumberValue(22.2)
    )


def test_A_symbol_has_different_life_inside_and_outside_a_function():
    """Define a symbol outside a function, redefine inside,
       then evaluate outside.  What happened inside the
       function should not affect the value outside."""

    assert (
        evald(
            """
            foo="bar"
            {foo=3}()
            foo
            """
        ) ==
        StringValue("bar")
    )


def test_A_symbol_within_a_function_has_the_local_value():
    assert (
        evald(
            """
            foo=3
            bar={foo=77 foo}()
            bar
            """
        ) ==
        NumberValue(77)
    )


def test_Native_function_gets_called():
    def native_fn(_env, x, y):
        return NumberValue(x.value + y.value)
    env = Env(None, None)
    env.set("native_fn", NativeFunctionValue(native_fn))
    assert evald("native_fn(2,8)", env) == NumberValue(10)


def test_Wrong_number_of_arguments_to_a_function_is_an_error():
    assert_prog_fails(
        "{}(3)",
        (
            "1 arguments passed to function " +
            r"FunctionDefTree\(params=\[\], body=\[\]\), " +
            "but it requires 0 arguments."
        ),
    )
    assert_prog_fails(
        "x={:(a,b,c)} x(3,2)",
        (
            r"2 arguments passed to function SymbolTree\(value='x'\), " +
            "but it requires 3 arguments."
        ),
    )


def test_Wrong_number_of_arguments_to_a_native_function_is_an_error():
    def native_fn0(_env):
        return NumberValue(12)

    def native_fn3(_env, _x, _y, _z):
        return NumberValue(12)
    env = Env(None, None)
    env.set("native_fn0", NativeFunctionValue(native_fn0))
    env.set("native_fn3", NativeFunctionValue(native_fn3))
    assert_prog_fails(
        "native_fn0(3)",
        (
            "1 arguments passed to function " +
            r"SymbolTree\(value='native_fn0'\), " +
            "but it requires 0 arguments."
        ),
        env
    )
    assert_prog_fails(
        "native_fn3(3,2)",
        (
            "2 arguments passed to function " +
            r"SymbolTree\(value='native_fn3'\), " +
            "but it requires 3 arguments."
        ),
        env
    )


def test_Function_arguments_are_independent():
    assert (
        evald(
            """
            fn={:(x){x}}
            a=fn("a")
            b=fn("b")
            a()
            """
        ) ==
        evald("'a'")
    )
    assert (
        evald(
            """
            fn={:(x){x}}
            a=fn("a")
            b=fn("b")
            b()
            """
        ) ==
        evald("'b'")
    )


def test_A_native_function_can_edit_the_environment():
    def mx3(env):
        env.set("x", NumberValue(3))
    env = Env(None, None)
    env.set("make_x_three", NativeFunctionValue(mx3))
    assert (
        evald("x=1 make_x_three() x", env) ==
        NumberValue(3)
    )


def test_A_closure_holds_updateable_values():
    def dumb_set(env, sym, val):
        env.parent().parent().parent().set(sym.value, val)

    def dumb_if_equal(env, val1, val2, then_fn, else_fn):
        if val1 == val2:
            ret = then_fn
        else:
            ret = else_fn
        return eval2_expr(env, FunctionCallTree(ret, []))
    env = Env(None, None)
    env.set("dumb_set", NativeFunctionValue(dumb_set))
    env.set("dumb_if_equal", NativeFunctionValue(dumb_if_equal))
    assert (
        evald(
            """
            counter={
                x=0
                {:(meth)
                    dumb_if_equal(
                        meth,
                        "get",
                        {x},
                        {dumb_set("x",x+1)}
                    )
                }
            }()
            counter("inc")
            counter("inc")
            counter("get")
            """,
            env
        ) ==
        NumberValue(2)
    )
