from collections import defaultdict
import math
from typing import Dict, Tuple

import attr

from graftlib.env import Env
from graftlib.functions import Functions
from graftlib.pt import Pt
from graftlib.nativefunctionvalue import NativeFunctionValue


def graft_env() -> Env:
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
    ret.set("D", NativeFunctionValue(Functions.dot))
    ret.set("F", NativeFunctionValue(Functions.fork))
    ret.set("J", NativeFunctionValue(Functions.jump))
    ret.set("L", NativeFunctionValue(Functions.line_to))
    ret.set("R", NativeFunctionValue(Functions.random))
    ret.set("S", NativeFunctionValue(Functions.step))

    return ret


def clone_env(from_: Env):
    return from_.clone()


@attr.s
class State:
    env: Env = attr.ib(
        default=attr.Factory(graft_env),
        convert=clone_env
    )

    prev_x: float = attr.ib(default=0, init=False)
    prev_y: float = attr.ib(default=0, init=False)

    def theta(self) -> float:
        """Angle we are facing in radians"""
        return 2 * math.pi * (self.env.get("d") / 360.0)

    def prev_pos(self) -> Pt:
        return Pt(self.prev_x, self.prev_y)

    def pos(self) -> Pt:
        return Pt(self.env.get("x"), self.env.get("y"))

    def set_pos(self, pos: Pt):
        self.prev_x = self.env.get("x")
        self.prev_y = self.env.get("y")
        self.env.set("x", pos.x)
        self.env.set("y", pos.y)

    def step(self) -> float:
        return self.env.get("s")

    def color(self) -> Tuple[float, float, float, float]:
        return (
            self.env.get("r"),
            self.env.get("g"),
            self.env.get("b"),
            self.env.get("a"),
        )

    def brush_size(self) -> float:
        return self.env.get("z")

    def set_fork_id(self, new_id):
        self.env.set("f", new_id)

    def set_variable(self, name, value):
        # x and y are magic variables that remember their previous values
        if name == "x":
            self.prev_x = self.env.get("x")
        elif name == "y":
            self.prev_y = self.env.get("y")
        self.env.set(name, value)

    def get_variable(self, name):
        return self.env.get(name)

    def has_variable(self, name):
        return self.env.get(name) is not None
