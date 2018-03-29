from collections import defaultdict
from typing import Dict, Iterable, Optional, Tuple
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
        return float(tree.value) * (-1.0 if tree.negative else 1.0)
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


def zero():
    return 0.0


def new_env() -> Dict[str, object]:
    """Create a dict of default variable values."""

    return defaultdict(
        zero,
        {
            "x": 0.0,    # x coord
            "y": 0.0,    # y coord
            "d": 0.0,    # direction in degrees
            "s": 10.0,   # step size
            "r": 0.0,    # red   0-100 (and 0 to -100)
            "g": 0.0,    # green 0-100 (and 0 to -100)
            "b": 0.0,    # blue  0-100 (and 0 to -100)
            "a": 100.0,  # alpha 0-100 (and 0 to -100)
            "z": 5.0,    # brush size
        }
    )


def dict2env(inp: Dict[str, object]) -> Dict[str, object]:
    ret = new_env()
    ret.update(inp)
    return ret


@attr.s
class State:
    env: Dict[str, object] = attr.ib(
        default=attr.Factory(new_env),
        convert=dict2env
    )

    def _fn_step(self, _rand):
        th = _theta(self.env["d"])
        old_pos = Pt(self.env["x"], self.env["y"])
        new_pos = Pt(
            self.env["x"] + self.env["s"] * math.sin(th),
            self.env["y"] + self.env["s"] * math.cos(th),
        )
        self.env["x"] = new_pos.x
        self.env["y"] = new_pos.y
        color = (self.env["r"], self.env["g"], self.env["b"], self.env["a"])
        return Line(old_pos, new_pos, color=color, size=self.env["z"])

    def _fn_jump(self, _rand):
        th = _theta(self.env["d"])
        new_pos = Pt(
            self.env["x"] + self.env["s"] * math.sin(th),
            self.env["y"] + self.env["s"] * math.cos(th),
        )
        self.env["x"] = new_pos.x
        self.env["y"] = new_pos.y
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

    def _next_function_call_once(self, tree, rand):  # -> List(Line)
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
            self.env["d"] = op(self.env["d"], val)
        elif tree.sym == "s":
            self.env["s"] = op(self.env["s"], val)
        elif tree.sym == "r":
            self.env["r"] = op(self.env["r"], val)
        elif tree.sym == "g":
            self.env["g"] = op(self.env["g"], val)
        elif tree.sym == "b":
            self.env["b"] = op(self.env["b"], val)
        elif tree.sym == "a":
            self.env["a"] = op(self.env["a"], val)
        elif tree.sym == "z":
            self.env["z"] = op(self.env["z"], val)
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
    program = list(trees)
    state = State()
    non_frames = 0
    i = 0
    while n is None or i < n:
        for statement in program:
            commands = state.next(statement, rand)
            for command in commands:
                yield (command, attr.evolve(state))
                if command is None:
                    non_frames += 1
                if command is not None or non_frames > 10:
                    # Count how many frames (we add one after 10 blanks)
                    i += 1
                    non_frames = 0
                if n is not None and i >= n:
                    raise StopIteration()


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
