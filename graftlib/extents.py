import itertools
import attr

from graftlib.eval_ import Pt


@attr.s
class Extents:
    _x_min: float = attr.ib(0.0, init=False)
    _x_max: float = attr.ib(0.0, init=False)
    _y_min: float = attr.ib(0.0, init=False)
    _y_max: float = attr.ib(0.0, init=False)

    def __attrs_post_init__(self) -> None:
        self.reset()

    def reset(self):
        self._x_min = 1_000_000.0
        self._x_max = -1_000_000.0
        self._y_min = 1_000_000.0
        self._y_max = -1_000_000.0

    def train_on(self, commands, lookahead_steps):
        taken = list(itertools.islice(commands, lookahead_steps))
        for cmd in taken:
            self.add(cmd.start)
            self.add(cmd.end)
        return itertools.chain(taken, commands)

    def centre(self):
        return (
            (self._x_max + self._x_min) / 2,
            (self._y_max + self._y_min) / 2,
        )

    def size(self):
        return (
            self._x_max - self._x_min,
            self._y_max - self._y_min,
        )

    def add(self, pt: Pt):
        if pt.x < self._x_min:
            self._x_min = pt.x
        elif pt.x > self._x_max:
            self._x_max = pt.x

        if pt.y < self._y_min:
            self._y_min = pt.y
        elif pt.y > self._y_max:
            self._y_max = pt.y
