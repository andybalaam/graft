from graftlib import cellfunctions
from graftlib import functions
from graftlib.env import Env
from graftlib.nativefunctionvalue import NativeFunctionValue
from graftlib.numbervalue import NumberValue


def _add_standard_functions(env: Env):
    env.set("If", NativeFunctionValue(cellfunctions.if_))
    env.set("T", NativeFunctionValue(cellfunctions.times))


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
    _add_standard_functions(ret)
    _add_graft_symbols(ret)

    return ret
