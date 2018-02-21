# pragma pylint: disable=wrong-import-position,wrong-import-order
import gi
gi.require_version('Gtk', '3.0')  # nopep8
from gi.repository import Gtk, GObject

from typing import Iterable, Optional
import attr
import typing
import math

from graftlib.eval_ import Pt, Line
from graftlib.lineoptimiser import ElidedLine
List = typing.List          # Silence pylint


max_lines = 500
ms_per_frame = 50
dot_size = 5


@attr.s
class Extents:
    _x_min: float = attr.ib(0.0, init=False)
    _x_max: float = attr.ib(0.0, init=False)
    _y_min: float = attr.ib(0.0, init=False)
    _y_max: float = attr.ib(0.0, init=False)

    def __attrs_post_init__(self) -> None:
        self.reset()

    def reset(self):
        self._x_min = -100.0
        self._x_max = 100.0
        self._y_min = -100.0
        self._y_max = 100.0

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


class Ui:
    def __init__(self, commands: Iterable, delete_listener):
        self.commands = commands
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

    def run(self):
        self.win.show_all()
        Gtk.main()

    def _centre_on_drawing(self, cr):
        win_w = self.canvas.get_allocated_width()
        win_h = self.canvas.get_allocated_height()
        x, y = self.extents.centre()
        w, h = self.extents.size()
        scale = 0.9 * min(win_w / w, win_h / h)
        cr.translate(-x * scale + (win_w / 2), -y * scale + (win_h / 2))
        cr.scale(scale, scale)

        # cr.arc(x, y, 10, 0, 2 * math.pi)
        # cr.stroke()
        # cr.arc(self.extents._x_min, self.extents._y_min, 2, 0, 2 * math.pi)
        # cr.stroke()
        # cr.arc(self.extents._x_min, self.extents._y_max, 4, 0, 2 * math.pi)
        # cr.stroke()
        # cr.arc(self.extents._x_max, self.extents._y_min, 2, 0, 2 * math.pi)
        # cr.stroke()
        # cr.arc(self.extents._x_max, self.extents._y_max, 4, 0, 2 * math.pi)
        # cr.stroke()

    def on_draw(self, _win, cr, _user_data: Optional):
        self._centre_on_drawing(cr)

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
