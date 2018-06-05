from collections import defaultdict
import math
from typing import Dict, Tuple

import attr

from graftlib.functions import Functions
from graftlib.pt import Pt
from graftlib.nativefunctionvalue import NativeFunctionValue


def graft_env() -> Dict[str, object]:
    """Create a dict of default variable values."""

    def zero():
        return 0.0

    return defaultdict(
        zero,
        {
            "f": 0,      # Fork ID
            "x": 0.0,    # x coord
            "y": 0.0,    # y coord
            "d": 0.0,    # direction in degrees
            "s": 10.0,   # step size
            "r": 0.0,    # red   0-100 (and 0 to -100)
            "g": 0.0,    # green 0-100 (and 0 to -100)
            "b": 0.0,    # blue  0-100 (and 0 to -100)
            "a": 100.0,  # alpha 0-100 (and 0 to -100)
            "z": 5.0,    # brush size
            "D": NativeFunctionValue(Functions.dot),
            "F": NativeFunctionValue(Functions.fork),
            "J": NativeFunctionValue(Functions.jump),
            "L": NativeFunctionValue(Functions.line_to),
            "R": NativeFunctionValue(Functions.random),
            "S": NativeFunctionValue(Functions.step),
        }
    )


def dict2env(inp: Dict[str, object]) -> Dict[str, object]:
    ret = graft_env()
    ret.update(inp)
    return ret


@attr.s
class State:
    env: Dict[str, object] = attr.ib(
        default=attr.Factory(graft_env),
        convert=dict2env
    )

    prev_x: float = attr.ib(default=0, init=False)
    prev_y: float = attr.ib(default=0, init=False)

    def theta(self) -> float:
        """Angle we are facing in radians"""
        return 2 * math.pi * (self.env["d"] / 360.0)

    def prev_pos(self) -> Pt:
        return Pt(self.prev_x, self.prev_y)

    def pos(self) -> Pt:
        return Pt(self.env["x"], self.env["y"])

    def set_pos(self, pos: Pt):
        self.prev_x = self.env["x"]
        self.prev_y = self.env["y"]
        self.env["x"] = pos.x
        self.env["y"] = pos.y

    def step(self) -> float:
        return self.env["s"]

    def color(self) -> Tuple[float, float, float, float]:
        return (self.env["r"], self.env["g"], self.env["b"], self.env["a"])

    def brush_size(self) -> float:
        return self.env["z"]

    def set_fork_id(self, new_id):
        self.env["f"] = new_id

    def set_variable(self, name, value):
        # x and y are magic variables that remember their previous values
        if name == "x":
            self.prev_x = self.env["x"]
        elif name == "y":
            self.prev_y = self.env["y"]
        self.env[name] = value

    def get_variable(self, name):
        return self.env[name]

    def has_variable(self, name):
        return name in self.env
