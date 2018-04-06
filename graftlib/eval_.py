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
            "S": BuiltInFn(Functions.step),
            "J": BuiltInFn(Functions.jump),
            "R": BuiltInFn(Functions.random),
            "D": BuiltInFn(Functions.dot),
            "L": BuiltInFn(Functions.line_to),
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


@attr.s
class Functions:
    state: State = attr.ib()
    rand = attr.ib()

    def step(self):
        th = self.state._theta()
        s = self.state.step()
        old_pos = self.state.pos()
        new_pos = Pt(
            old_pos.x + s * math.sin(th),
            old_pos.y + s * math.cos(th),
        )
        self.state.set_pos(new_pos)
        return Line(
            old_pos,
            new_pos,
            color=self.state.color(),
            size=self.state.brush_size()
        )

    def dot(self):
        return Dot(
            self.state.pos(),
            self.state.color(),
            self.state.brush_size()
        )

    def line_to(self):
        return Line(
            self.state.prev_pos(),
            self.state.pos(),
            color=self.state.color(),
            size=self.state.brush_size(),
        )

    def jump(self):
        self.step()
        return None

    def random(self):
        return float(self.rand(-10, 10))


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


class Evaluator:
    def __init__(self, state, rand):
        self.rand = rand
        self.state: State = state
        self.functions: Functions = Functions(state, rand)

    def _function_call_symbol(self, fn_name):
        if not self.state.has_variable(fn_name):
            raise Exception("Unknown function %s" % fn_name)

        fnwrap = self.state.get_variable(fn_name)
        if type(fnwrap) == BuiltInFn:
            return fnwrap.fn.__get__(self.functions)()
        else:
            raise Exception(
                "%s is not a function - it is a %s" % (fn_name, type(fnwrap))
            )

    def _function_call_userdefined(self, fn_def: FunctionDef) -> List:
        ret = []
        for stmt in fn_def.body:
            ret += self.statement(stmt, None)
        return ret

    def _function_call_once(self, function_call_stmt: FunctionCall) -> List:
        fn = function_call_stmt.fn
        if type(fn) == Symbol:
            return [self._function_call_symbol(fn.value)]
        elif type(fn) == FunctionDef:
            return self._function_call_userdefined(fn)

    def _function_call(self, function_call_stmt: FunctionCall) -> List:
        ret = []
        for _i in range(function_call_stmt.repeat):
            ret += self._function_call_once(function_call_stmt)
        return ret

    def _value(self, value_expr):
        type_ = type(value_expr)
        if type_ == Number:
            neg = -1.0 if value_expr.negative else 1.0
            return float(value_expr.value) * neg
        elif type_ == FunctionCall:
            return self._function_call(value_expr)[0]
        elif type_ == Symbol:
            return self.state.get_variable(value_expr.value)
        else:
            raise Exception(
                "I don't know how to evaluate a value like %s." %
                str(value_expr)
            )

    def _modify(self, modify_stmt: Modify):
        var_name = modify_stmt.sym
        val = self._value(modify_stmt.value)
        op = _operator_fn(modify_stmt.op)

        self.state.set_variable(
            var_name,
            op(self.state.get_variable(var_name), val)
        )

        return None

    def statement(self, statement, set_label):
        stmt_type = type(statement)
        if stmt_type == FunctionCall:
            return self._function_call(statement)
        elif stmt_type == Modify:
            self._modify(statement)
            return [None]
        elif stmt_type == Symbol:
            return [None]
        elif stmt_type == Label:
            if set_label is not None:
                set_label()
                return [None]
            else:
                raise Exception(
                    "You cannot (yet?) define labels inside functions.")
        elif stmt_type == FunctionDef:
            raise Exception(
                "You defined a function but didn't call it: " + str(statement))
        else:
            raise Exception("Unknown statement type: " + str(statement))


class RunningProgram:
    def __init__(self, program: Iterable, rand):
        self.program: List = list(program)
        self.state: State = State()
        self.evaluator = Evaluator(self.state, rand)
        """
        pc = program counter - the next instruction from program to run
        label = the value to reset pc to when we finish the program
        """
        self.pc = 0
        self.label = 0

    def set_label(self):
        self.label = self.pc

    def next(self) -> List:
        if self.pc >= len(self.program):
            self.pc = self.label
        statement = self.program[self.pc]
        self.pc += 1
        return self.evaluator.statement(statement, self.set_label)


@attr.s
class FramesCounter:
    max_count: int = attr.ib()
    non_frames: int = attr.ib(default=0, init=False)
    count: int = attr.ib(default=0, init=False)

    def next_frame(self, command):
        """
        Raise StopIteration if we have done enough frames already
        """

        # Keep track of how many blank frames we have seen
        if command is None:
            self.non_frames += 1

        # If we get a normal frame, or have seen 10 blank, increase the count
        if command is not None or self.non_frames > 10:
            self.count += 1
            self.non_frames = 0

        # If we have gone over the max, raise a StopIteration
        if self.max_count is not None and self.count >= self.max_count:
            raise StopIteration()


#: Iterable[Tree], n -> Iterable[(Command, State)]
def eval_debug(program: Iterable, n: Optional[int], rand) -> Iterable:
    prog = RunningProgram(program, rand)
    frames_counter = FramesCounter(n)
    while True:
        # Run a line of code, and get back the animation frame(s) that result
        commands = prog.next()
        for command in commands:
            yield (command, attr.evolve(prog.state))
            frames_counter.next_frame(command)


#: Iterable[Tree], n -> Iterable[(Command, State)]
def eval_(program: Iterable, n: Optional[int], rand) -> Iterable:
    """
    Run the supplied program n times, or for ever if n is None.
    """

    return filter(
        lambda x: x is not None,
        map(
            lambda x: x[0],
            eval_debug(program, n, rand),
        ),
    )
