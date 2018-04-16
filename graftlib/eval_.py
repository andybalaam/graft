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
            "f": 0,      # Fork ID
            "x": 0.0,    # x coord
            "y": 0.0,    # y coord
            "d": 0.0,    # direction in degrees
            "s": 10.0,   # step size
            "r": 0.0,    # red   0-100 (and 0 to -100)
            "g": 0.0,    # green 0-100 (and 0 to -100)
            "b": 0.0,    # blue  0-100 (and 0 to -100)
            "a": 100.0,  # alpha 0-100 (and 0 to -100)
            "z": 5.0,    # brush size
            "D": BuiltInFn(Functions.dot),
            "F": BuiltInFn(Functions.fork),
            "J": BuiltInFn(Functions.jump),
            "L": BuiltInFn(Functions.line_to),
            "R": BuiltInFn(Functions.random),
            "S": BuiltInFn(Functions.step),
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

    def theta(self) -> float:
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

    def set_fork_id(self, new_id):
        self.env["f"] = new_id

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
    fork_callback = attr.ib()

    def step(self):
        th = self.state.theta()
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
        return float(self.rand.__call__(-10, 10))
        # TODO: return Number

    def fork(self):
        self.fork_callback.__call__()


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
    def __init__(self, state, rand, fork_callback):
        self.rand = rand
        self.state: State = state
        self.functions: Functions = Functions(state, rand, fork_callback)

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
            return self._function_call(value_expr)[-1]
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
        elif stmt_type == Number:
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


def strip_non_strokes(maybe_strokes):
    def sns(maybe_stroke):
        if type(maybe_stroke) in (Line, Dot):
            return maybe_stroke
        else:
            return None
    return [sns(item) for item in maybe_strokes]


class RunningProgram:
    def __init__(
            self,
            program: List,
            rand,
            fork_callback,
            state=None,
            evaluator=None,
            pc=None,
            label=None,
    ):
        self.program: List = program
        self.rand = rand
        self.fork_callback = fork_callback
        self.state: State = state if state else State()
        self.evaluator = (
            evaluator if evaluator else Evaluator(self.state, rand, self.fork)
        )

        """
        pc = program counter - the next instruction from program to run
        label = the value to reset pc to when we finish the program
        """
        self.pc = pc if pc is not None else 0
        self.label = label if label is not None else 0

    def set_label(self):
        self.label = self.pc

    def next(self) -> List:
        if self.pc >= len(self.program):
            self.pc = self.label
        statement = self.program[self.pc]
        self.pc += 1
        return strip_non_strokes(
            self.evaluator.statement(statement, self.set_label)
        )

    def fork(self):

        new_state = attr.evolve(self.state)
        new_evaluator = Evaluator(new_state, self.rand, self.fork)

        self.fork_callback.__call__(
            RunningProgram(
                list(self.program),
                self.rand,
                self.fork,
                new_state,
                new_evaluator,
                self.pc,
                self.label,
            )
        )


def empty(queue: List) -> bool:
    return len(queue) == 0


class MultipleRunningPrograms:
    def __init__(self, program: List, rand, max_parallel: int):
        # programs is a list of (RunningProgram, queue)
        # where queue is a list of commands already returned by that program,
        # waiting to be returned.
        self.programs = [(RunningProgram(program, rand, self.fork), [])]
        self.max_parallel = max_parallel
        self.new_programs = []
        self._fork_id_counter = 0

    def next_fork_id(self):
        self._fork_id_counter += 1
        return self._fork_id_counter

    def next(self):
        # Ensure each queue has at least 1 thing in it

        for prog, queue in self.programs:
            if empty(queue):
                queue.extend(prog.next())

        ret = []
        for prog, queue in self.programs:
            ret.append((queue.pop(0), attr.evolve(prog.state)))

        self.programs.extend(self.new_programs)
        self.new_programs = []
        if len(self.programs) > self.max_parallel:
            self.programs = self.programs[
                len(self.programs) - self.max_parallel:
            ]

        return ret

    def fork(self, cloned_running_program: RunningProgram):
        cloned_running_program.state.set_fork_id(self.next_fork_id())
        self.new_programs.append((cloned_running_program, []))


@attr.s
class FramesCounter:
    max_count: int = attr.ib()
    non_frames: int = attr.ib(default=0, init=False)
    count: int = attr.ib(default=0, init=False)

    def next_frame(self, parallel_commands):
        """
        Raise StopIteration if we have done enough frames already
        """

        is_real_frame = any(x[0] for x in parallel_commands)

        # Keep track of how many blank frames we have seen
        if not is_real_frame:
            self.non_frames += 1

        # If we get a normal frame, or have seen 10 blank, increase the count
        if is_real_frame or self.non_frames > 10:
            self.count += 1
            self.non_frames = 0

        # If we have gone over the max, raise a StopIteration
        if self.max_count is not None and self.count >= self.max_count:
            raise StopIteration()


def _run_program(program: Iterable, rand, max_parallel) -> Iterable:
    progs = MultipleRunningPrograms(list(program), rand, max_parallel)
    while True:
        # Run a line of code, and get back the animation frame(s) that result
        yield progs.next()


#: Iterable[Tree], n -> Iterable[(Command, State)]
def eval_debug(
        program: Iterable,
        n: Optional[int],
        rand,
        max_parallel
) -> Iterable:
    frames_counter = FramesCounter(n)
    for parallel_commands in _run_program(program, rand, max_parallel):
        yield parallel_commands
        frames_counter.next_frame(parallel_commands)


#: Iterable[Tree], n -> Iterable[(Command, State)]
def eval_(program: Iterable, n: Optional[int], rand, max_parallel) -> Iterable:
    """
    Run the supplied program n times, or for ever if n is None.
    """

    for cmds_states in eval_debug(program, n, rand, max_parallel):
        commands = [x[0] for x in cmds_states]
        if any(commands):
            yield commands
