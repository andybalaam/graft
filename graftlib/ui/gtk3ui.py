# pragma pylint: disable=wrong-import-position,wrong-import-order
import gi
gi.require_version('Gtk', '3.0')  # nopep8
from gi.repository import Gtk, GObject

import math
from typing import Optional

from graftlib.animation import Animation


ms_per_frame = 50


class Gtk3Ui:
    def __init__(self, animation: Animation):
        self.win = Gtk.Window(resizable=True)
        self.canvas = Gtk.DrawingArea()
        self.canvas.set_size_request(300, 300)
        self.win.add(self.canvas)
        self.win.connect("delete-event", Gtk.main_quit)
        self.canvas.connect("draw", self.on_draw, None)
        self.timeout_id = GObject.timeout_add(
            ms_per_frame, self.on_timeout, None)
        self.animation = animation

    def run(self):
        self.win.show_all()
        Gtk.main()
        return 0

    def on_draw(self, _win, cr, _user_data: Optional):
        x, y, scale = self.animation.animate_window(
            self.canvas.get_allocated_width(),
            self.canvas.get_allocated_height(),
        )
        cr.translate(x, y)
        cr.scale(scale, scale)

        for line in self.animation.lines:
            cr.move_to(line.start.x, line.start.y)
            cr.line_to(line.end.x, line.end.y)
        cr.stroke()

        cr.arc(
            self.animation.pos.x,
            self.animation.pos.y,
            self.animation.dot_size,
            0,
            2 * math.pi
        )
        cr.fill()

    def on_timeout(self, _user_data):
        more_frames = self.animation.step()
        self.canvas.queue_draw()
        return more_frames
