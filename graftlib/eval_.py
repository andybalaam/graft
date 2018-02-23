from typing import Iterable, Optional
import math
import operator

import attr
from graftlib.parse import FunctionCall, Modify, Number


@attr.s(cmp=True, frozen=True)
class Pt:
    x: float = attr.ib()
    y: float = attr.ib()


@attr.s(cmp=True, frozen=True)
class Line():
    start: Pt = attr.ib()
    end: Pt = attr.ib()


def _theta(dir_: float) -> float:
    """Angle in hundreds of a circle to Angle in radians"""
    return 2 * math.pi * (dir_ / 360.0)


def _eval_value(tree, rand):
    tree_type = type(tree)
    if tree_type == Number:
        return float(tree.value)
    elif tree_type == FunctionCall:
        if tree.fn == "R":
            return float(rand(-10, 10))
    else:
        raise Exception(
            "I don't know how to evaluate a value like %s." %
            str(tree)
        )


@attr.s
class State:
    pos: Pt = attr.ib()
    dir_: float = attr.ib()
    step: float = attr.ib()

    def _fn_step(self, _tree, _rand):
        th = _theta(self.dir_)
        old_pos = attr.evolve(self.pos)
        new_pos = attr.evolve(
            self.pos,
            x=self.pos.x + self.step * math.sin(th),
            y=self.pos.y + self.step * math.cos(th),
        )
        self.pos = new_pos
        return Line(old_pos, new_pos)

    def _next_function_call(self, tree, rand):
        if tree.fn == "S":
            return self._fn_step(tree, rand)
        elif tree.fn == "R":
            raise Exception(
                "The :R (Random) function does nothing on its own.  " +
                "You must use its value for something by writing " +
                "e.g '~+d' after it."
            )
        else:
            raise Exception("Unknown function %s" % tree.fn)

    def _next_modify(self, tree, rand):
        val = _eval_value(tree.value, rand)

        def operator_fn(opstr: str):
            if tree.op == "=":
                return lambda x, y: y
            elif opstr == "+":
                return operator.add
            elif tree.op == "":
                return operator.mul
            else:
                raise Exception("Unknown operator '%s'." % tree.op)

        op = operator_fn(tree.op)

        if tree.sym == "d":
            self.dir_ = op(self.dir_, val)
        elif tree.sym == "s":
            self.step = op(self.step, val)
        else:
            raise Exception(
                "No support for custom variables yet: " + tree.sym
            )
        return None

    def next(self, tree, rand):  #: Tree
        if type(tree) == FunctionCall:
            return self._next_function_call(tree, rand)
        elif type(tree) == Modify:
            return self._next_modify(tree, rand)
        else:
            raise Exception("Unknown tree type: " + tree)


#: Iterable[Tree], n -> Iterable[(Command, State)]
def eval_debug(trees: Iterable, n: Optional[int], rand) -> Iterable:
    trees_list = list(trees)
    state = State(pos=Pt(0.0, 0.0), dir_=0.0, step=10.0)
    i = 0
    while n is None or i < n:
        i += 1
        for tree in trees_list:
            command = state.next(tree, rand)
            yield (command, attr.evolve(state))


#: Iterable[Tree], n -> Iterable[(Command, State)]
def eval_(trees: Iterable, n: Optional[int], rand) -> Iterable:
    """
    Run the supplied program n times, or for ever if n is None.
    """

    return filter(
        lambda x: x is not None,
        map(
            lambda x: x[0],
            eval_debug(trees, n, rand),
        ),
    )
