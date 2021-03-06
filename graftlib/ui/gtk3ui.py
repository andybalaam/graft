# pragma pylint: disable=wrong-import-position,wrong-import-order
import gi
gi.require_version('Gtk', '3.0')  # nopep8
from gi.repository import Gtk, GObject

from typing import Optional, Tuple

from graftlib.animation import Animation
from graftlib.ui.cairo_draw import cairo_draw


ms_per_frame = 50


class Gtk3Ui:
    def __init__(self, animation: Animation, image_size: Tuple[int, int]):
        self.win = Gtk.Window(resizable=True)
        self.canvas = Gtk.DrawingArea()
        self.canvas.set_size_request(*image_size)
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
        cairo_draw(
            self.animation,
            cr,
            self.canvas.get_allocated_width(),
            self.canvas.get_allocated_height(),
        )

    def on_timeout(self, _user_data):
        more_frames = self.animation.step()
        self.canvas.queue_draw()
        while Gtk.events_pending():
            Gtk.main_iteration_do(True)
        return more_frames
