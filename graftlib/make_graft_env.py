import math

from graftlib import cellfunctions
from graftlib import cellstdlib
from graftlib import functions
from graftlib.env import Env
from graftlib.endofloopvalue import EndOfLoopValue
from graftlib.eval_cell import eval_cell_list
from graftlib.lex_cell import lex_cell
from graftlib.nativefunctionvalue import NativeFunctionValue
from graftlib.numbervalue import NumberValue
from graftlib.parse_cell import parse_cell


def exec_cell(code, env):
    eval_cell_list(parse_cell(lex_cell(code)), env)


def wrap_math(fn):
    def impl(env, num):
        return NumberValue(fn(num.value))
    return NativeFunctionValue(impl)


def wrap_math_radinp(fn):
    def impl(env, num):
        return NumberValue(fn(math.radians(num.value)))
    return NativeFunctionValue(impl)


def wrap_math_radout(fn):
    def impl(env, num):
        return NumberValue(math.degrees(fn(num.value)))
    return NativeFunctionValue(impl)


def wrap_math2_radout(fn):
    def impl(env, num1, num2):
        return NumberValue(math.degrees(fn(num1.value, num2.value)))
    return NativeFunctionValue(impl)


def wrap_math2(fn):
    def impl(env, num1, num2):
        return NumberValue(fn(num1.value, num2.value))
    return NativeFunctionValue(impl)


def add_cell_symbols(env: Env):
    env.set("endofloop", EndOfLoopValue)
    env.set("Add", NativeFunctionValue(cellfunctions.add))
    env.set("Get", NativeFunctionValue(cellfunctions.get))
    env.set("For", NativeFunctionValue(cellfunctions.for_))
    env.set("If", NativeFunctionValue(cellfunctions.if_))
    env.set("Len", NativeFunctionValue(cellfunctions.len_))
    env.set("T", NativeFunctionValue(cellfunctions.times))
    env.set("Sin", wrap_math_radinp(math.sin))
    env.set("Cos", wrap_math_radinp(math.cos))
    env.set("Tan", wrap_math_radinp(math.tan))
    env.set("ASin", wrap_math_radout(math.asin))
    env.set("ACos", wrap_math_radout(math.acos))
    env.set("ATan", wrap_math_radout(math.atan))
    env.set("ATan2", wrap_math2_radout(math.atan2))
    env.set("Sqrt", wrap_math(math.sqrt))
    env.set("Pow", wrap_math2(math.pow))
    env.set("Hypot", wrap_math2(math.hypot))

    exec_cell(cellstdlib.cellstdlib, env)


def _add_graft_symbols(env: Env):
    env.set("f", NumberValue(0))      # Fork ID
    env.set("x", NumberValue(0.0))    # x coord
    env.set("y", NumberValue(0.0))    # y coord
    env.set("d", NumberValue(0.0))    # direction in degrees
    env.set("s", NumberValue(10.0))   # step size
    env.set("r", NumberValue(0.0))    # red   0-100 (and 0 to -100)
    env.set("g", NumberValue(0.0))    # green 0-100 (and 0 to -100)
    env.set("b", NumberValue(0.0))    # blue  0-100 (and 0 to -100)
    env.set("a", NumberValue(100.0))  # alpha 0-100 (and 0 to -100)
    env.set("z", NumberValue(5.0))    # brush size
    env.set("D", NativeFunctionValue(functions.dot))
    env.set("F", NativeFunctionValue(functions.fork))
    env.set("J", NativeFunctionValue(functions.jump))
    env.set("L", NativeFunctionValue(functions.line_to))
    env.set("R", NativeFunctionValue(functions.random))
    env.set("S", NativeFunctionValue(functions.step))


def make_graft_env() -> Env:
    """Create an environment with all the default Graft values"""

    ret = Env()
    add_cell_symbols(ret)
    _add_graft_symbols(ret)

    return ret
