import math

import attr

from graftlib.dot import Dot
from graftlib.line import Line
from graftlib.pt import Pt
from graftlib.state import State


@attr.s
class Functions:
    rand = attr.ib()
    fork_callback = attr.ib()

    def step(self, env):
        state = State(env)
        th = state.theta()
        s = state.step()
        old_pos = state.pos()
        new_pos = Pt(
            old_pos.x + s * math.sin(th),
            old_pos.y + s * math.cos(th),
        )
        state.set_pos(new_pos)
        return [Line(
            old_pos,
            new_pos,
            color=state.color(),
            size=state.brush_size()
        )]

    def dot(self, env):
        state = State(env)
        return [Dot(
            state.pos(),
            state.color(),
            state.brush_size()
        )]

    def line_to(self, env):
        state = State(env)
        return [Line(
            state.prev_pos(),
            state.pos(),
            color=state.color(),
            size=state.brush_size(),
        )]

    def jump(self, env):
        self.step(env)
        return [None]

    def random(self, env):
        return [float(self.rand.__call__(-10, 10))]

    def fork(self, env):
        return [self.fork_callback.__call__()]
