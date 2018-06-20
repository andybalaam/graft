import inspect
from typing import List
import attr

from graftlib.parse_cell import (
    AssignmentTree,
    FunctionCallTree,
    FunctionDefTree,
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
    arg1 = eval2_expr(env, expr.left)
    arg2 = eval2_expr(env, expr.right)
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


def fail_if_wrong_number_of_args(fn_name, params, args):
    if len(params) != len(args):
        raise Exception((
            "%d arguments passed to function %s, but it " +
            "requires %d arguments."
        ) % (len(args), fn_name, len(params)))


def _function_call(expr, env):
    fn = eval2_expr(env, expr.fn)
    args = list((eval2_expr(env, a) for a in expr.args))
    typ = type(fn)
    if typ == UserFunctionValue:
        fail_if_wrong_number_of_args(expr.fn, fn.params, args)
        new_env = fn.env.make_child()
        for p, a in zip(fn.params, args):
            new_env.set(p.value, a)
        return eval_list(fn.body, new_env)
    elif typ == NativeFunctionValue:
        params = inspect.getargspec(fn.py_fn).args
        fail_if_wrong_number_of_args(expr.fn, params[1:], args)
        return fn.py_fn(env, *args)
    else:
        raise Exception(
            "Attempted to call something that is not a function: %s" %
            str(fn)
        )


def eval2_expr(env, expr):
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
        if var_name in env.local_items():
            raise Exception("Not allowed to re-assign symbol '%s'." % var_name)
        val = eval2_expr(env, expr.value)
        env.set(var_name, val)
        return val
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


def eval_(exprs, env):
    for expr in exprs:
        yield eval2_expr(env, expr)


def eval_list(exprs, env):
    ret = NoneValue()
    for expr in eval_(exprs, env):
        ret = expr
    return ret
