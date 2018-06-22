import inspect
from typing import List
import attr

from graftlib.parse_cell import (
    AssignmentTree,
    FunctionCallTree,
    FunctionDefTree,
    ModifyTree,
    NumberTree,
    OperationTree,
    StringTree,
    SymbolTree,
)

from graftlib.env import Env
from graftlib.nativefunctionvalue import NativeFunctionValue
from graftlib.numbervalue import NumberValue


@attr.s
class NoneValue:
    pass


@attr.s
class StringValue:
    value: str = attr.ib()


@attr.s
class UserFunctionValue:
    params: List = attr.ib()
    body: List = attr.ib()
    env: Env = attr.ib()


def _operation(expr, env):
    arg1 = _eval(env, expr.left)
    arg2 = _eval(env, expr.right)
    if expr.operation == "+":
        return NumberValue(arg1.value + arg2.value)
    elif expr.operation == "-":
        return NumberValue(arg1.value - arg2.value)
    elif expr.operation == "*":
        return NumberValue(arg1.value * arg2.value)
    elif expr.operation == "/":
        return NumberValue(arg1.value / arg2.value)
    else:
        raise Exception("Unknown operation: " + expr.operation)


def _modify(expr: ModifyTree, env):
    var_name = expr.symbol.value
    val = _eval(env, expr.value).value
    prev_val = env.get(var_name).value

    if expr.operation == "+=":
        new_val = prev_val + val
    elif expr.operation == "-=":
        new_val = prev_val - val
    elif expr.operation == "*=":
        new_val = prev_val * val
    elif expr.operation == "/=":
        new_val = prev_val / val
    else:
        raise Exception("Unknown modify operation: " + expr.operation)

    env.set(var_name, NumberValue(new_val))
    return env.get(var_name)


def fail_if_wrong_number_of_args(fn_name, params, args):
    if len(params) != len(args):
        raise Exception((
            "%d arguments passed to function %s, but it " +
            "requires %d arguments."
        ) % (len(args), fn_name, len(params)))


def _function_call(expr, env):
    fn = _eval(env, expr.fn)
    args = list((_eval(env, a) for a in expr.args))
    typ = type(fn)

    if typ == UserFunctionValue:
        fail_if_wrong_number_of_args(expr.fn, fn.params, args)
        new_env = fn.env.make_child()
        for p, a in zip(fn.params, args):
            new_env.set(p.value, a)
        return eval_cell_list(fn.body, new_env)
    elif typ == NativeFunctionValue:
        params = inspect.getargspec(fn.py_fn).args
        fail_if_wrong_number_of_args(expr.fn, params[1:], args)
        return fn.py_fn(env, *args)
    else:
        raise Exception(
            "Attempted to call something that is not a function: %s" %
            str(fn)
        )


def eval_cell(env, expr):
    ret = _eval(env, expr)
    # Wrap values in [] if they are not already
    # a list of strokes.
    return ret if type(ret) is list else [ret]


def _eval(env, expr):
    typ = type(expr)
    if typ == NumberTree:
        return NumberValue(float(expr.value))
    elif typ == StringTree:
        return StringValue(expr.value)
    elif typ == NoneValue:
        return expr
    elif typ == OperationTree:
        return _operation(expr, env)
    elif typ == SymbolTree:
        ret = env.get(expr.value)
        if ret is None:
            raise Exception("Unknown symbol '%s'." % expr.value)
        else:
            return ret
    elif typ == AssignmentTree:
        var_name = expr.symbol.value
        val = _eval(env, expr.value)
        env.set(var_name, val)
        return val
    elif typ == ModifyTree:
        return _modify(expr, env)
    elif typ == FunctionCallTree:
        return _function_call(expr, env)
    elif typ == FunctionDefTree:
        return UserFunctionValue(
            expr.params,
            expr.body,
            env.make_child()
        )
    elif typ == UserFunctionValue:
        return expr
    else:
        raise Exception("Unknown expression type: " + str(expr))


def _eval_iter(exprs, env):
    for expr in exprs:
        yield _eval(env, expr)


def eval_cell_list(exprs, env):
    ret = NoneValue()
    for expr in _eval_iter(exprs, env):
        ret = expr
    return ret
