from graftlib.env import Env
from graftlib import functions
from graftlib.nativefunctionvalue import NativeFunctionValue


def make_graft_env() -> Env:
    """Create an environment with all the default Graft values"""

    ret = Env()
    ret.set("f", 0)      # Fork ID
    ret.set("x", 0.0)    # x coord
    ret.set("y", 0.0)    # y coord
    ret.set("d", 0.0)    # direction in degrees
    ret.set("s", 10.0)   # step size
    ret.set("r", 0.0)    # red   0-100 (and 0 to -100)
    ret.set("g", 0.0)    # green 0-100 (and 0 to -100)
    ret.set("b", 0.0)    # blue  0-100 (and 0 to -100)
    ret.set("a", 100.0)  # alpha 0-100 (and 0 to -100)
    ret.set("z", 5.0)    # brush size
    ret.set("D", NativeFunctionValue(functions.dot))
    ret.set("F", NativeFunctionValue(functions.fork))
    ret.set("J", NativeFunctionValue(functions.jump))
    ret.set("L", NativeFunctionValue(functions.line_to))
    ret.set("R", NativeFunctionValue(functions.random))
    ret.set("S", NativeFunctionValue(functions.step))

    return ret
