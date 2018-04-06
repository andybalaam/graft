from typing import Iterable, Union
import typing

from graftlib.eval_ import Dot, Pt, Line
from graftlib.strokeoptimiser import Elided
from graftlib.extents import Extents
from graftlib.windowanimator import WindowAnimator


List = typing.List  # Silence pylint


class Animation:
    def __init__(
            self,
            commands: Iterable,
            delete_listener,
            lookahead_steps,
            max_strokes,
            dot_size,
    ):
        self.strokes: List[Union[Line, Dot]] = []
        self.pos: Pt = Pt(0.0, 0.0)
        self.extents = Extents()
        self.window_animator = WindowAnimator(lookahead_steps)
        self.commands = self.extents.train_on(commands, lookahead_steps)
        self.delete_listener = delete_listener
        self.max_strokes = max_strokes
        self.dot_size = dot_size

    def _prune(self):
        if len(self.strokes) > self.max_strokes:
            to_delete = self.strokes[:-self.max_strokes]
            self.strokes = self.strokes[-self.max_strokes:]
            for d in to_delete:
                self.delete_listener.delete_stroke(d)

    def step(self):
        try:
            parallel_commands = next(self.commands)
            for command in parallel_commands:
                if command is None:
                    continue
                if type(command) == Line:
                    self.pos = command.end
                    self.strokes.append(command)
                elif type(command) == Dot:
                    self.pos = command.pos
                    self.strokes.append(command)
                elif type(command) == Elided:
                    if type(command.item) == Line:
                        self.pos = command.item.end
                    else:  # Dot
                        self.pos = command.item.pos
                else:
                    raise Exception("Unknown command: " + str(command))
            self._prune()
            return True
        except StopIteration:
            return False

    def _add_extents(self, stroke: Union[Line, Dot]):
        if type(stroke) == Elided:
            self._add_extents(stroke.item)
        elif type(stroke) == Line:
            self.extents.add(stroke.start)
            self.extents.add(stroke.end)
        else:  # Dot
            self.extents.add(stroke.pos)

    def animate_window(self, win_w, win_h) -> (float, float, float):
        ret = self.window_animator.animate(
            self.extents,
            (win_w, win_h)
        )
        self.extents.reset()
        for stroke in self.strokes:
            self._add_extents(stroke)
        return ret
