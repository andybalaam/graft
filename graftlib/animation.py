from typing import Iterable
import typing

from graftlib.eval_ import Pt, Line
from graftlib.lineoptimiser import ElidedLine
from graftlib.extents import Extents
from graftlib.windowanimator import WindowAnimator


List = typing.List  # Silence pylint


class Animation:
    def __init__(
            self,
            commands: Iterable,
            delete_listener,
            lookahead_steps,
            max_lines,
    ):
        self.lines: List[Line] = []
        self.pos: Pt = Pt(0.0, 0.0)
        self.extents = Extents()
        self.window_animator = WindowAnimator(lookahead_steps)
        self.commands = self.extents.train_on(commands, lookahead_steps)
        self.delete_listener = delete_listener
        self.max_lines = max_lines

    def step(self):
        try:
            command = next(self.commands)
            if type(command) == Line:
                self.pos = command.end
                self.lines.append(command)
                if len(self.lines) > self.max_lines:
                    to_delete = self.lines[:-self.max_lines]
                    self.lines = self.lines[-self.max_lines:]
                    for d in to_delete:
                        self.delete_listener.delete_line(d)
            elif type(command) == ElidedLine:
                self.pos = command.end
            else:
                raise Exception("Unknown command: " + str(command))
            return True
        except StopIteration:
            return False

    def animate_window(self, win_w, win_h) -> (float, float, float):
        ret = self.window_animator.animate(
            self.extents,
            (win_w, win_h)
        )
        self.extents.reset()
        for line in self.lines:
            self.extents.add(line.start)
            self.extents.add(line.end)
        return ret
