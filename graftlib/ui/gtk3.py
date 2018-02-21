# pragma pylint: disable=wrong-import-position,wrong-import-order
import gi
gi.require_version('Gtk', '3.0')  # nopep8
from gi.repository import Gtk, GObject
from typing import Iterable, Optional
import typing
import math

from graftlib.eval_ import Pt, Line
from graftlib.lineoptimiser import ElidedLine
List = typing.List          # Silence pylint


max_lines = 500
ms_per_frame = 50
dot_size = 5


class Ui:
    def __init__(self, commands: Iterable, delete_listener):
        self.commands = commands
        self.delete_listener = delete_listener
        self.win = Gtk.Window()
        self.canvas = Gtk.DrawingArea()
        self.canvas.set_size_request(640, 480)
        self.win.add(self.canvas)
        self.win.connect("delete-event", Gtk.main_quit)
        self.canvas.connect("draw", self.on_draw, None)
        self.timeout_id = GObject.timeout_add(
            ms_per_frame, self.on_timeout, None)
        self.lines: List[Line] = []
        self.pos: Pt = Pt(0.0, 0.0)

    def run(self):
        self.win.show_all()
        Gtk.main()

    def on_draw(self, _win, cr, _user_data: Optional):
        cr.translate(100, 100)

        for line in self.lines:
            cr.move_to(line.start.x, line.start.y)
            cr.line_to(line.end.x, line.end.y)
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
