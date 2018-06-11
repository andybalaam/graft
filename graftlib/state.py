from collections import defaultdict
import math
from typing import Dict, Tuple

import attr

from graftlib.env import Env
from graftlib.pt import Pt
from graftlib.make_graft_env import make_graft_env


def clone_env(from_: Env):
    return from_.clone()


@attr.s
class State:
    env: Env = attr.ib(
        default=attr.Factory(make_graft_env),
        convert=clone_env
    )

    def theta(self) -> float:
        """Angle we are facing in radians"""
        return 2 * math.pi * (self.env.get("d") / 360.0)

    def prev_pos(self) -> Pt:
        return Pt(self.env.get("xprev"), self.env.get("yprev"))

    def pos(self) -> Pt:
        return Pt(self.env.get("x"), self.env.get("y"))

    def set_pos(self, pos: Pt):
        self.env.set("xprev", self.env.get("x"))
        self.env.set("yprev", self.env.get("y"))
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
            self.env.set("xprev", self.env.get("x"))
        elif name == "y":
            self.env.set("yprev", self.env.get("y"))
        self.env.set(name, value)

    def get_variable(self, name):
        return self.env.get(name)

    def has_variable(self, name):
        return self.env.get(name) is not None
