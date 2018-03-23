from typing import Iterable, Optional, Tuple
import math
import operator

import attr
from graftlib.parse import FunctionCall, FunctionDef, Modify, Number, Symbol


@attr.s(cmp=True, frozen=True)
class Pt:
    x: float = attr.ib()
    y: float = attr.ib()


@attr.s(cmp=True, frozen=True)
class Line():
    start: Pt = attr.ib()
    end: Pt = attr.ib()
    color: Tuple = attr.ib(default=(0.0, 0.0, 0.0, 100.0))
    size: float = attr.ib(default=5.0)


def _theta(dir_: float) -> float:
    """Angle in hundreds of a circle to Angle in radians"""
    return 2 * math.pi * (dir_ / 360.0)


def _eval_value(tree, rand):
    tree_type = type(tree)
    if tree_type == Number:
        return float(tree.value) * (-1.0 if tree.negate else 1.0)
    elif tree_type == FunctionCall:
        if tree.fn.value == "R":
            return float(rand(-10, 10))
    else:
        raise Exception(
            "I don't know how to evaluate a value like %s." %
            str(tree)
        )


def _operator_fn(opstr: str):
    if opstr == "=":
        return lambda x, y: y
    elif opstr == "+":
        return operator.add
    elif opstr == "-":
        return operator.sub
    elif opstr == "":
        return operator.mul
    elif opstr == "/":
        return operator.truediv
    else:
        raise Exception("Unknown operator '%s'." % opstr)


@attr.s
class State:
    pos: Pt = attr.ib()
    dir_: float = attr.ib()
    step: float = attr.ib()
    red: float = attr.ib(0.0)
    green: float = attr.ib(0.0)
    blue: float = attr.ib(0.0)
    alpha: float = attr.ib(100.0)
    size: float = attr.ib(5.0)

    def _fn_step(self, _rand):
        th = _theta(self.dir_)
        old_pos = attr.evolve(self.pos)
        new_pos = attr.evolve(
            self.pos,
            x=self.pos.x + self.step * math.sin(th),
            y=self.pos.y + self.step * math.cos(th),
        )
        self.pos = new_pos
        color = (self.red, self.green, self.blue, self.alpha)
        return Line(old_pos, new_pos, color=color, size=self.size)

    def _fn_jump(self, _rand):
        th = _theta(self.dir_)
        new_pos = attr.evolve(
            self.pos,
            x=self.pos.x + self.step * math.sin(th),
            y=self.pos.y + self.step * math.cos(th),
        )
        self.pos = new_pos
        return None

    def _next_function_call_symbol(self, fn_name, rand):
        if fn_name == "S":
            return [self._fn_step(rand)]
        elif fn_name == "J":
            return [self._fn_jump(rand)]
        elif fn_name == "R":
            raise Exception(
                "The :R (Random) function does nothing on its own.  " +
                "You must use its value for something by writing " +
                "e.g '~+d' after it."
            )
        else:
            raise Exception("Unknown function %s" % fn_name)

    def _next_function_call_userdefined(self, fn, rand):
        ret = []
        for ln in fn.body:
            ret += self.next(ln, rand)
        return ret

    def _next_function_call_once(self, tree, rand): #-> List(Line)
        if type(tree.fn) == Symbol:
            return self._next_function_call_symbol(tree.fn.value, rand)
        elif type(tree.fn) == FunctionDef:
            return self._next_function_call_userdefined(tree.fn, rand)

    def _next_function_call(self, tree, rand):
        ret = []
        for _i in range(tree.repeat):
            ret += self._next_function_call_once(tree, rand)
        return ret

    def _next_modify(self, tree, rand):
        val = _eval_value(tree.value, rand)
        op = _operator_fn(tree.op)

        if tree.sym == "d":
            self.dir_ = op(self.dir_, val)
        elif tree.sym == "s":
            self.step = op(self.step, val)
        elif tree.sym == "r":
            self.red = op(self.red, val)
        elif tree.sym == "g":
            self.green = op(self.green, val)
        elif tree.sym == "b":
            self.blue = op(self.blue, val)
        elif tree.sym == "a":
            self.alpha = op(self.alpha, val)
        elif tree.sym == "z":
            self.size = op(self.size, val)
        else:
            raise Exception(
                "No support for custom variables yet: " + tree.sym
            )
        return None

    def next(self, tree, rand):  #: List(Tree)
        if type(tree) == FunctionCall:
            return self._next_function_call(tree, rand)
        elif type(tree) == Modify:
            return [self._next_modify(tree, rand)]
        elif type(tree) == FunctionDef:
            raise Exception(
                "You defined a function but didn't call it: " + str(tree))
        else:
            raise Exception("Unknown tree type: " + str(tree))


#: Iterable[Tree], n -> Iterable[(Command, State)]
def eval_debug(trees: Iterable, n: Optional[int], rand) -> Iterable:
    trees_list = list(trees)
    state = State(pos=Pt(0.0, 0.0), dir_=0.0, step=10.0)
    i = 0
    while n is None or i < n:
        i += 1
        for tree in trees_list:
            commands = state.next(tree, rand)
            for command in commands:
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
