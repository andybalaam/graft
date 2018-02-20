# pragma pylint: disable=wrong-import-position,wrong-import-order
import gi
gi.require_version('Gtk', '3.0')  # nopep8
from gi.repository import Gtk, GObject
from typing import Iterable, Optional
import typing
import math

import graftlib
Line = graftlib.eval_.Line  # Silence pylint
List = typing.List          # Silence pylint


class Ui:
    def __init__(self, commands: Iterable):
        self.commands = commands
        self.win = Gtk.Window()
        self.canvas = Gtk.DrawingArea()
        self.canvas.set_size_request(640, 480)
        self.win.add(self.canvas)
        self.win.connect("delete-event", Gtk.main_quit)
        self.canvas.connect("draw", self.on_draw, None)
        self.timeout_id = GObject.timeout_add(50, self.on_timeout, None)
        self.lines: List[Line] = []

    def run(self):
        self.win.show_all()
        Gtk.main()

    def on_draw(self, _win, cr, _user_data: Optional):
        for line in self.lines:
            last_line = line
            cr.move_to(50 + line.start.x, 50 - line.start.y)
            cr.line_to(50 + line.end.x, 50 - line.end.y)
        cr.stroke()

        if self.lines:
            last_line: Line = self.lines[-1]
            cr.arc(
                50 + last_line.end.x,
                50 - last_line.end.y,
                5,
                0,
                2 * math.pi
            )
        cr.fill()

    def on_timeout(self, _user_data):
        try:
            self.lines.append(next(self.commands))
            self.canvas.queue_draw()
            return True
        except StopIteration:
            return False
