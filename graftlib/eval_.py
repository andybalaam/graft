from typing import Iterable
import math
import attr
from graftlib.parse import FunctionCall, Modify


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
    return 2 * math.pi * (dir_ / 360.0)


@attr.s
class State:
    pos: Pt = attr.ib()
    dir_: float = attr.ib()
    step: float = attr.ib()

    def next(self, tree):  #: Tree
        if type(tree) == FunctionCall:
            th = theta(self.dir_)
            old_pos = attr.evolve(self.pos)
            new_pos = attr.evolve(self.pos)
            new_pos.x += self.step * math.sin(th)
            new_pos.y += self.step * math.cos(th)
            self.pos = new_pos
            return Line(old_pos, new_pos)
        elif type(tree) == Modify:
            val = float(tree.value.value)
            sym = tree.sym.value
            op = tree.op.value
            if sym == "d":
                if op == "+":
                    self.dir_ += val
                else:
                    self.dir_ = val
            elif sym == "s":
                if op == "+":
                    self.step += val
                else:
                    self.step = val
            else:
                raise Exception("No suppprt for custom variables yet: " + sym)
            return None
        else:
            raise Exception("Unknown tree type: " + tree)


#: Iterable[Tree], n -> Iterable[(Command, State)]
def eval_debug(trees: Iterable, n: int) -> Iterable:
    trees_list = list(trees)
    state = State(pos=Pt(0, 0), dir_=0, step=10)
    for _ in range(n):
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
