from typing import Iterable, List, Optional
import operator

import attr

from graftlib.dot import Dot
from graftlib.functions import Functions
from graftlib.line import Line
from graftlib.make_graft_env import make_graft_env
from graftlib.parse import (
    FunctionCall,
    FunctionDef,
    Label,
    Modify,
    Number,
    Symbol,
)
from graftlib.nativefunctionvalue import NativeFunctionValue
from graftlib.state import State


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
        if type(fnwrap) == NativeFunctionValue:
            return fnwrap.py_fn.__get__(self.functions)()
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
            return self._function_call_symbol(fn.value)
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


SKIPPED = object()


def consolidate_skipped(maybe_skipped):
    """
    If the supplied iterable contains SKIPPED,
    filter all of them out, but emit a None
    instead of the first one.

    This allows us to return many SKIPPED
    from fork() and get just one None out
    at the end - this happens in the main
    fork, and each new fork also emits just
    one None, so they are in sync.
    """
    done_none = False
    for item in maybe_skipped:
        if item == SKIPPED:
            if not done_none:
                yield None
                done_none = True
        else:
            yield item


def non_strokes_to_none(maybe_strokes):
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
        self.state: State = state if state else State(make_graft_env())
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
        return non_strokes_to_none(
            consolidate_skipped(
                self.evaluator.statement(statement, self.set_label)
            )
        )

    def fork(self):
        return self.fork_callback.__call__(
            RunningProgram(
                list(self.program),
                self.rand,
                self.fork_callback,
                State(self.state.env.clone()),
                None,
                self.pc,
                self.label,
            )
        )


def empty(queue: List) -> bool:
    return len(queue) == 0


class MultipleRunningPrograms:
    def __init__(self, program: List, rand, max_forks: int):
        # programs is a list of (RunningProgram, queue)
        # where queue is a list of commands already returned by that program,
        # waiting to be returned.
        self.programs = [(RunningProgram(program, rand, self.fork), [])]
        self.max_forks = max_forks
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
            # Note: return a reference to state.  In eval_debug we
            # will copy it if needed.
            ret.append((queue.pop(0), prog.state.env))

        self.programs.extend(self.new_programs)
        self.new_programs = []
        if len(self.programs) > self.max_forks:
            self.programs = self.programs[
                len(self.programs) - self.max_forks:
            ]

        return ret

    def fork(self, cloned_running_program: RunningProgram):
        cloned_running_program.state.set_fork_id(self.next_fork_id())
        self.new_programs.append((cloned_running_program, []))
        # If we fork many times, we return SKIPPED many times,
        # so the output of the main fork would be lots of
        # SKIPPED, but we merge them all together into a
        # single None in consolidate_skipped().
        return SKIPPED


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


def _run_program(program: Iterable, rand, max_forks) -> Iterable:
    progs = MultipleRunningPrograms(list(program), rand, max_forks)
    while True:
        # Run a line of code, and get back the animation frame(s) that result
        yield progs.next()


def copy_envs(parallel_commands):
    return [
        (stroke, env.clone()) for (stroke, env) in parallel_commands
    ]


#: Iterable[Tree], n -> Iterable[(Command, Env)]
def eval_debug(
        program: Iterable,
        n: Optional[int],
        rand,
        max_forks
) -> Iterable:
    frames_counter = FramesCounter(n)
    for parallel_commands in _run_program(program, rand, max_forks):
        yield copy_envs(parallel_commands)
        frames_counter.next_frame(parallel_commands)


#: Iterable[Tree], n -> Iterable[Command]
def eval_(program: Iterable, n: Optional[int], rand, max_forks) -> Iterable:
    """
    Run the supplied program for n steps, or forever if n is None.
    """

    frames_counter = FramesCounter(n)
    for cmds_envs in _run_program(program, rand, max_forks):
        commands = [x[0] for x in cmds_envs]
        if any(commands):
            yield commands
        frames_counter.next_frame(cmds_envs)
