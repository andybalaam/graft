import math

import attr
from typing import Tuple

from graftlib.dot import Dot
from graftlib.line import Line
from graftlib.pt import Pt


def step(env):
    th = theta(env)
    s = step_size(env)
    old_pos = pos(env)
    new_pos = Pt(
        old_pos.x + s * math.sin(th),
        old_pos.y + s * math.cos(th),
    )
    set_pos(env, new_pos)
    return [Line(
        old_pos,
        new_pos,
        color=color(env),
        size=brush_size(env)
    )]


def dot(env):
    return [Dot(
        pos(env),
        color(env),
        brush_size(env)
    )]


def line_to(env):
    return [Line(
        prev_pos(env),
        pos(env),
        color=color(env),
        size=brush_size(env),
    )]


def jump(env):
    step(env)
    return [None]


def random(env):
    return [float(env.rand.__call__(-10, 10))]


def fork(env):
    return [env.fork_callback.__call__()]


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


def step_size(self) -> float:
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


def set_variable(env, name, value):
    # x and y are magic variables that remember their previous values
    if name == "x":
        env.set("xprev", env.get("x"))
    elif name == "y":
        env.set("yprev", env.get("y"))
    env.set(name, value)


def has_variable(self, name):
    return self.env.get(name) is not None
