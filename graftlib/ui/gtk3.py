# pragma pylint: disable=wrong-import-position
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject  # nopep8
from typing import Iterable, Optional   # nopep8
import math                             # nopep8


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
        self.lines = []

    def run(self):
        self.win.show_all()
        Gtk.main()

    def on_draw(self, win, cr, user_data):
        last_line: Optional = None
        for line in self.lines:
            last_line = line
            cr.move_to(50 + line.start.x, 50 + line.start.y)
            cr.line_to(50 + line.end.x, 50 + line.end.y)
        cr.stroke()
        if last_line is not None:
            cr.arc(
                50 + last_line.end.x,
                50 + last_line.end.y,
                5,
                0,
                2 * math.pi
            )
        cr.fill()

    def on_timeout(self, user_data):
        try:
            self.lines.append(next(self.commands))
            self.canvas.queue_draw()
            return True
        except StopIteration:
            return False
