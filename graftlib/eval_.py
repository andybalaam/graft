from typing import Iterable
from graftlib.parse import FunctionCall, Modify
import attr
import math


@attr.s
class Pt:
    x: float = attr.ib()
    y: float = attr.ib()


@attr.s
class Line:
    start: Pt = attr.ib()
    end: Pt = attr.ib()


def theta(dir_: float) -> float:
    """Angle in hundreds of a circle to Angle in radians"""
    return 2 * math.pi * (dir_ / 100.0)


@attr.s
class State:
    pos: Pt = attr.ib()
    dir_: float = attr.ib()

    def next(self, tree):  #: Tree
        if type(tree) == FunctionCall:
            old_pos = attr.evolve(self.pos)
            th = theta(self.dir_)
            self.pos.x += 10.0 * math.sin(th)
            self.pos.y += 10.0 * math.cos(th)
            return Line(old_pos, self.pos)
        elif type(tree) == Modify:
            self.dir_ += 10.0
            return None
        else:
            raise Exception("Unknown tree type: " + tree)


#: Iterable[Tree], n -> Iterable[(Command, State)]
def eval_debug(trees: Iterable, n: int) -> Iterable:
    trees_list = list(trees)
    state = State(pos=Pt(0, 0), dir_=0)
    for i in range(n):
        for tree in trees_list:
            command = state.next(tree)
            yield (command, attr.evolve(state))


#: Iterable[Tree], n -> Iterable[(Command, State)]
def eval_(trees: Iterable, n: int) -> Iterable:
    return filter(
        lambda x: x is not None,
        map(
            lambda x: x[0],
            eval_debug(trees, n),
        ),
    )
