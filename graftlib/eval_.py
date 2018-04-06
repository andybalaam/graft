from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Tuple
import math
import operator

import attr
from graftlib.parse import (
    FunctionCall,
    FunctionDef,
    Label,
    Modify,
    Number,
    Symbol,
)


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


@attr.s(cmp=True, frozen=True)
class Dot():
    pos: Pt = attr.ib()
    color: Tuple = attr.ib(default=(0.0, 0.0, 0.0, 100.0))
    size: float = attr.ib(default=5.0)


_ops = {
    "=": lambda x, y: y,
    "+": operator.add,
    "-": operator.sub,
    "": operator.mul,
    "/": operator.truediv,
}


def _operator_fn(opstr: str):
    if opstr in _ops:
        return _ops[opstr]
    else:
        raise Exception("Unknown operator '%s'." % opstr)


@attr.s
class BuiltInFn:
    fn = attr.ib()


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
            "S": BuiltInFn(State.fn_step),
            "J": BuiltInFn(State.fn_jump),
            "R": BuiltInFn(State.fn_random),
            "D": BuiltInFn(State.fn_dot),
            "L": BuiltInFn(State.fn_line_to),
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

    prev_x: float = attr.ib(default=0, init=False)
    prev_y: float = attr.ib(default=0, init=False)

    def _theta(self) -> float:
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

    def fn_step(self, _rand):
        th = self._theta()
        s = self.step()
        old_pos = self.pos()
        new_pos = Pt(
            old_pos.x + s * math.sin(th),
            old_pos.y + s * math.cos(th),
        )
        self.set_pos(new_pos)
        return Line(
            old_pos,
            new_pos,
            color=self.color(),
            size=self.brush_size()
        )

    def fn_dot(self, _rand):
        return Dot(self.pos(), self.color(), self.brush_size())

    def fn_line_to(self, _rand):
        return Line(
            self.prev_pos(),
            self.pos(),
            color=self.color(),
            size=self.brush_size(),
        )

    def fn_jump(self, _rand):
        self.fn_step(_rand)
        return None

    def fn_random(self, rand):
        return float(rand(-10, 10))

    def _next_function_call_symbol(self, fn_name, rand):

        if fn_name not in self.env:
            raise Exception("Unknown function %s" % fn_name)

        fnwrap = self.env[fn_name]
        if type(fnwrap) == BuiltInFn:
            return fnwrap.fn.__get__(self)(rand)
        else:
            raise Exception(
                "%s is not a function - it is a %s" % (fn_name, type(fnwrap))
            )

    def _next_function_call_userdefined(self, fn, rand):
        ret = []
        for ln in fn.body:
            ret += self._next_tree(ln, rand, None)
        return ret

    def _next_function_call_once(self, tree, rand):  # -> List(Line)
        if type(tree.fn) == Symbol:
            return [self._next_function_call_symbol(tree.fn.value, rand)]
        elif type(tree.fn) == FunctionDef:
            return self._next_function_call_userdefined(tree.fn, rand)

    def _next_function_call(self, tree, rand):
        ret = []
        for _i in range(tree.repeat):
            ret += self._next_function_call_once(tree, rand)
        return ret

    def _eval_value(self, tree, rand):
        tree_type = type(tree)
        if tree_type == Number:
            return float(tree.value) * (-1.0 if tree.negative else 1.0)
        elif tree_type == FunctionCall:
            return self._next_function_call(tree, rand)[0]
        elif tree_type == Symbol:
            return self.env[tree.value]
        else:
            raise Exception(
                "I don't know how to evaluate a value like %s." %
                str(tree)
            )

    def _next_modify(self, tree, rand):
        var_name = tree.sym
        val = self._eval_value(tree.value, rand)
        op = _operator_fn(tree.op)

        # x and y are magic variables that remember their previous values
        if var_name == "x":
            self.prev_x = self.env["x"]
        elif var_name == "y":
            self.prev_y = self.env["y"]

        self.env[var_name] = op(self.env[var_name], val)
        return None

    def _next_tree(self, tree, rand, set_label):
        if type(tree) == FunctionCall:
            return self._next_function_call(tree, rand)
        elif type(tree) == Modify:
            self._next_modify(tree, rand)
            return [None]
        elif type(tree) == Symbol:
            return [None]
        elif type(tree) == FunctionDef:
            raise Exception(
                "You defined a function but didn't call it: " + str(tree))
        elif type(tree) == Label:
            if set_label is not None:
                set_label()
            else:
                raise Exception(
                    "You cannot (yet?) define labels inside functions.")
            return [None]
        else:
            raise Exception("Unknown tree type: " + str(tree))


@attr.s
class RunningProgram:
    program: List = attr.ib(convert=list)
    rand = attr.ib()

    """
    pc = program counter - the next instruction from program to run
    label = the value to reset program counter to when we finish the program
    """
    pc: int = attr.ib(default=0, init=False)
    label: int = attr.ib(default=0, init=False)

    state: State = attr.ib(default=attr.Factory(State))

    def set_label(self):
        self.label = self.pc

    def next(self) -> List:
        if self.pc >= len(self.program):
            self.pc = self.label
        tree = self.program[self.pc]
        self.pc += 1
        return self.state._next_tree(tree, self.rand, self.set_label)


#: Iterable[Tree], n -> Iterable[(Command, State)]
def eval_debug(trees: Iterable, n: Optional[int], rand) -> Iterable:
    prog = RunningProgram(trees, rand)
    non_frames = 0
    i = 0
    while n is None or i < n:
        commands = prog.next()
        for command in commands:
            yield (command, attr.evolve(prog.state))
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
