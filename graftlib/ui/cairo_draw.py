import math

from typing import Tuple

import cairo
from graftlib.animation import Animation
from graftlib.eval_ import Dot, Line


min_visible_line_width = 1.0
default_line_width = 3.0


def calc_line_size(s: float, scale: float) -> float:
    width = (abs(s) / 5.0) * default_line_width
    if width * scale < min_visible_line_width:
        return min_visible_line_width / scale
    else:
        return width


def divide_by_100(rgba: Tuple[float, float, float, float]) -> (
        Tuple[float, float, float, float]
):
    return tuple(abs(x) / 100.0 for x in rgba)


def draw_line(cairo_cr, line: Line, scale):
    cairo_cr.set_line_width(calc_line_size(line.size, scale))
    cairo_cr.set_source_rgba(*divide_by_100(line.color))
    # Minus signs on y coords because we are reversing the y axis.
    # See the same thing in extents too (but nowhere else).
    cairo_cr.move_to(line.start.x, -line.start.y)
    cairo_cr.line_to(line.end.x, -line.end.y)
    cairo_cr.stroke()


def draw_dot(cairo_cr, dot: Dot, scale):
    cairo_cr.set_line_width(0)
    cairo_cr.set_source_rgba(*divide_by_100(dot.color))
    # Minus signs on y coords because we are reversing the y axis.
    # See the same thing in extents too (but nowhere else).
    cairo_cr.arc(dot.pos.x, -dot.pos.y, dot.size / 2, 0.0, 2 * math.pi)
    cairo_cr.fill()
    cairo_cr.stroke()


def cairo_draw(animation: Animation, cairo_cr, win_w, win_h):

    x, y, scale = animation.animate_window(win_w, win_h)
    cairo_cr.translate(x, y)
    cairo_cr.scale(scale, scale)

    cairo_cr.set_source_rgb(1.0, 1.0, 1.0)
    cairo_cr.paint()

    cairo_cr.set_line_cap(cairo.LINE_CAP_ROUND)

    for stroke in animation.strokes:
        if type(stroke) == Line:
            draw_line(cairo_cr, stroke, scale)
        else:  # Dot
            draw_dot(cairo_cr, stroke, scale)

    cairo_cr.arc(
        animation.pos.x,
        -animation.pos.y,
        animation.dot_size,
        0,
        2 * math.pi
    )
    cairo_cr.fill()
