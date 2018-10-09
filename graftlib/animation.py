from typing import Iterable, List, Union

from graftlib.dot import Dot
from graftlib.extents import Extents
from graftlib.line import Line
from graftlib.pt import Pt
from graftlib.strokeoptimiser import Elided
from graftlib.windowanimator import WindowAnimator


class Animation:
    def __init__(
            self,
            commands: Iterable[List[Union[Dot, Line, Elided]]],
            delete_listener,
            lookahead_steps,
            max_strokes,
            dot_size,
    ):
        self.strokes = []
        self.poss = []
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
            if len(self.poss) < len(parallel_commands):
                increase_by = len(parallel_commands) - len(self.poss)
                self.poss += [Pt(0, 0) for _ in range(increase_by)]
            for i, command in enumerate(parallel_commands):
                if command is None:
                    continue
                if type(command) == Line:
                    self.poss[i] = command.end
                    self.strokes.append(command)
                elif type(command) == Dot:
                    self.poss[i] = command.pos
                    self.strokes.append(command)
                elif type(command) == Elided:
                    if type(command.item) == Line:
                        self.poss[i] = command.item.end
                    else:  # Dot
                        self.poss[i] = command.item.pos
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
