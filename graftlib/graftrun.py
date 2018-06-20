from typing import Iterable, List, Optional

import attr

from graftlib import functions
from graftlib.dot import Dot
from graftlib.line import Line
from graftlib.make_graft_env import make_graft_env
from graftlib.parse import Label
from graftlib.programenv import ProgramEnv


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
            env,
            eval_expr,
            pc=None,
            label=None,
    ):
        self.program: List = program
        self.rand = rand
        self.fork_callback = fork_callback
        self.env = ProgramEnv(env, rand, self.fork)
        self.eval_expr = eval_expr

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
                self.statement(statement)
            )
        )

    def statement(self, statement):
        stmt_type = type(statement)
        if stmt_type == Label:
            self.set_label()
            return [None]
        else:
            return self.eval_expr(self.env, statement)

    def fork(self):
        return self.fork_callback.__call__(
            RunningProgram(
                list(self.program),
                self.rand,
                self.fork_callback,
                self.env.clone(),
                self.eval_expr,
                self.pc,
                self.label,
            )
        )


def empty(queue: List) -> bool:
    return len(queue) == 0


class MultipleRunningPrograms:
    def __init__(self, program: List, rand, max_forks: int, eval_expr):
        # programs is a list of (RunningProgram, queue)
        # where queue is a list of commands already returned by that program,
        # waiting to be returned.
        initial_program = RunningProgram(
            program,
            rand,
            self.fork,
            make_graft_env(),
            eval_expr,
        )
        self.programs = [(initial_program, [])]
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
            # Note: return a reference to env.  In eval_debug we
            # will copy it if needed.
            ret.append((queue.pop(0), prog.env))

        self.programs.extend(self.new_programs)
        self.new_programs = []
        if len(self.programs) > self.max_forks:
            self.programs = self.programs[
                len(self.programs) - self.max_forks:
            ]

        return ret

    def fork(self, cloned_running_program: RunningProgram):
        functions.set_fork_id(cloned_running_program.env, self.next_fork_id())
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


def _run_program(program: Iterable, rand, max_forks, eval_expr) -> Iterable:
    progs = MultipleRunningPrograms(list(program), rand, max_forks, eval_expr)
    while True:
        # Run a line of code, and get back the animation frame(s) that result
        yield progs.next()


def copy_envs(parallel_commands):
    return [
        (stroke, env.clone()) for (stroke, env) in parallel_commands
    ]


#: Iterable[Tree], n -> Iterable[(Command, Env)]
def graftrun_debug(
        program: Iterable,
        n: Optional[int],
        rand,
        max_forks,
        eval_expr,
) -> Iterable:
    frames_counter = FramesCounter(n)
    for parallel_commands in _run_program(program, rand, max_forks, eval_expr):
        yield copy_envs(parallel_commands)
        frames_counter.next_frame(parallel_commands)


#: Iterable[Tree], n -> Iterable[Command]
def graftrun(
    program: Iterable,
    n: Optional[int],
    rand,
    max_forks,
    eval_expr
) -> Iterable:
    """
    Run the supplied program for n steps, or forever if n is None.
    """

    frames_counter = FramesCounter(n)
    for cmds_envs in _run_program(program, rand, max_forks, eval_expr):
        commands = [x[0] for x in cmds_envs]
        if any(commands):
            yield commands
        frames_counter.next_frame(cmds_envs)
