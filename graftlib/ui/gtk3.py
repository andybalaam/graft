# pragma pylint: disable=wrong-import-position,wrong-import-order
import gi
gi.require_version('Gtk', '3.0')  # nopep8
from gi.repository import Gtk, GObject

import attr
import itertools
from typing import Iterable, Optional
import typing
import math

from graftlib.eval_ import Pt, Line
from graftlib.lineoptimiser import ElidedLine
List = typing.List          # Silence pylint


max_lines = 500
ms_per_frame = 50
dot_size = 5

# How far to run the animation initially to decide what
# out initial zoom level should be.
lookahead_steps = 100


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

    def train_on(self, commands):
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


def limit(val, r):
    if val < -r:
        return -r
    elif val > r:
        return r
    else:
        return val


@attr.s
class SmoothValue:
    value: float = attr.ib()
    _v: float = attr.ib(0, init=False)

    def set_target(self, target: float):
        self._v += 0.3 * (target - self.value)  # Acceleration
        self._v = limit(self._v, 10.0) * 0.2     # Limit + damping
        self.value += self._v


@attr.s
class WindowAnimator:
    """
    Given the translation and scale we _want_ to be at,
    provide actual translation and scale that smoothly
    animate towards that.
    """

    x: Optional[SmoothValue] = attr.ib(None, init=False)
    y: Optional[SmoothValue] = attr.ib(None, init=False)
    w: Optional[SmoothValue] = attr.ib(None, init=False)
    h: Optional[SmoothValue] = attr.ib(None, init=False)

    counter: int = attr.ib(0, init=False)

    def animate(self, cr, extents, window_size):
        centre = extents.centre()
        size = extents.size()
        if self.x is None:
            self.x = SmoothValue(centre[0])
            self.y = SmoothValue(centre[1])
            self.w = SmoothValue(size[0])
            self.h = SmoothValue(size[1])
        self.move(cr, centre, size, window_size)

    def move(self, cr, centre, size, window_size):

        if self.counter >= lookahead_steps:
            self.x.set_target(centre[0])
            self.y.set_target(centre[1])
            self.w.set_target(size[0])
            self.h.set_target(size[1])
        self.counter += 1

        scale = (
            0.8 *
            min(
                window_size[0] / self.w.value,
                window_size[1] / self.h.value
            )
        )
        if scale > 2.0:
            scale = 2.0
        x = -self.x.value * scale + (window_size[0] / 2)
        y = -self.y.value * scale + (window_size[1] / 2)

        cr.translate(x, y)
        cr.scale(scale, scale)


class Ui:
    def __init__(self, commands: Iterable, delete_listener):
        self.delete_listener = delete_listener
        self.win = Gtk.Window(resizable=True)
        self.canvas = Gtk.DrawingArea()
        self.canvas.set_size_request(300, 300)
        self.win.add(self.canvas)
        self.win.connect("delete-event", Gtk.main_quit)
        self.canvas.connect("draw", self.on_draw, None)
        self.timeout_id = GObject.timeout_add(
            ms_per_frame, self.on_timeout, None)
        self.lines: List[Line] = []
        self.pos: Pt = Pt(0.0, 0.0)
        self.extents = Extents()
        self.window_animator = WindowAnimator()
        self.commands = self.extents.train_on(commands)

    def run(self):
        self.win.show_all()
        Gtk.main()

    def on_draw(self, _win, cr, _user_data: Optional):
        self.window_animator.animate(
            cr,
            self.extents,
            (
                self.canvas.get_allocated_width(),
                self.canvas.get_allocated_height(),
            )
        )

        self.extents.reset()
        for line in self.lines:
            cr.move_to(line.start.x, line.start.y)
            cr.line_to(line.end.x, line.end.y)
            self.extents.add(line.start)
            self.extents.add(line.end)
        cr.stroke()

        cr.arc(
            self.pos.x,
            self.pos.y,
            dot_size,
            0,
            2 * math.pi
        )
        cr.fill()

    def on_timeout(self, _user_data):
        try:
            command = next(self.commands)
            if type(command) == Line:
                self.pos = command.end
                self.lines.append(command)
                if len(self.lines) > max_lines:
                    to_delete = self.lines[:-max_lines]
                    self.lines = self.lines[-max_lines:]
                    for d in to_delete:
                        self.delete_listener.delete_line(d)
                self.canvas.queue_draw()
            elif type(command) == ElidedLine:
                self.pos = command.end
                self.canvas.queue_draw()
            else:
                raise Exception("Unknown command: " + str(command))
            return True
        except StopIteration:
            return False
