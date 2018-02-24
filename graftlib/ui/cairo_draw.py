import math

from typing import Tuple

from graftlib.animation import Animation


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


def cairo_draw(animation: Animation, cairo_cr, win_w, win_h):

    x, y, scale = animation.animate_window(win_w, win_h)
    cairo_cr.translate(x, y)
    cairo_cr.scale(scale, scale)

    cairo_cr.set_source_rgb(1.0, 1.0, 1.0)
    cairo_cr.paint()

    for line in animation.lines:
        cairo_cr.set_line_width(calc_line_size(line.size, scale))
        cairo_cr.set_source_rgba(*divide_by_100(line.color))
        # Minus signs on y coords because we are reversing the y axis.
        # See the same thing in extents too (but nowhere else).
        cairo_cr.move_to(line.start.x, -line.start.y)
        cairo_cr.line_to(line.end.x, -line.end.y)
        cairo_cr.stroke()

    cairo_cr.arc(
        animation.pos.x,
        -animation.pos.y,
        animation.dot_size,
        0,
        2 * math.pi
    )
    cairo_cr.fill()
