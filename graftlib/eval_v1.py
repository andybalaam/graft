from typing import List
import operator

from graftlib.env import Env
from graftlib import functions
from graftlib.labeltree import LabelTree
from graftlib.nativefunctionvalue import NativeFunctionValue
from graftlib.numbervalue import NumberValue
from graftlib.parse_v1 import (
    FunctionCall,
    FunctionDef,
    Modify,
    Number,
    Symbol,
)


_ops = {
    "=": lambda x, y: y,
    "+": operator.add,
    "-": operator.sub,
    "": operator.mul,
    "/": operator.truediv,
}


def _operator_fn(opstr: str):
    if opstr in _ops:
        return _ops[opstr]
    else:
        raise Exception("Unknown operator '%s'." % opstr)


class Evaluator:
    def __init__(self, env):
        self.env: Env = env

    def _function_call_symbol(self, fn_name):
        fnwrap = self.env.get(fn_name)
        if type(fnwrap) == NativeFunctionValue:
            return fnwrap.py_fn(self.env)
        else:
            raise Exception(
                "%s is not a function - it is a %s" % (fn_name, type(fnwrap))
            )

    def _function_call_userdefined(self, fn_def: FunctionDef) -> List:
        ret = None
        for stmt in fn_def.body:
            ret = self.statement(stmt)
        return ret

    def _function_call_once(self, function_call_stmt: FunctionCall) -> List:
        fn = function_call_stmt.fn
        if type(fn) == Symbol:
            return self._function_call_symbol(fn.value)
        elif type(fn) == FunctionDef:
            return self._function_call_userdefined(fn)

    def _function_call(self, function_call_stmt: FunctionCall) -> List:
        ret = None
        for _i in range(function_call_stmt.repeat):
            ret = self._function_call_once(function_call_stmt)
        return ret

    def _value(self, value_expr):
        type_ = type(value_expr)
        if type_ == Number:
            neg = -1.0 if value_expr.negative else 1.0
            return NumberValue(float(value_expr.value) * neg)
        elif type_ == FunctionCall:
            return self._function_call(value_expr)
        elif type_ == Symbol:
            return self.env.get(value_expr.value)
        else:
            raise Exception(
                "I don't know how to evaluate a value like %s." %
                str(value_expr)
            )

    def _modify(self, modify_stmt: Modify):
        var_name = modify_stmt.sym
        val = self._value(modify_stmt.value)
        op = _operator_fn(modify_stmt.op)

        self.env.set(
            var_name,
            NumberValue(op(self.env.get(var_name).value, val.value))
        )
        return None

    def statement(self, statement):
        stmt_type = type(statement)
        if stmt_type == FunctionCall:
            return self._function_call(statement)
        elif stmt_type == Modify:
            self._modify(statement)
        elif stmt_type == Symbol:
            pass
        elif stmt_type == Number:
            pass
        elif stmt_type == LabelTree:
            raise Exception(
                "You cannot (yet?) define labels inside functions.")
        elif stmt_type == FunctionDef:
            raise Exception(
                "You defined a function but didn't call it: " + str(statement))
        else:
            raise Exception("Unknown statement type: " + str(statement))


def eval_v1(env, statement):
    evaluator = Evaluator(env)
    return evaluator.statement(statement)
