import math

from graftlib.animation import Animation


def cairo_draw(animation: Animation, cairo_cr, win_w, win_h):

    x, y, scale = animation.animate_window(win_w, win_h)
    cairo_cr.translate(x, y)
    cairo_cr.scale(scale, scale)

    cairo_cr.set_source_rgb(1.0, 1.0, 1.0)
    cairo_cr.paint()

    cairo_cr.set_source_rgb(0.0, 0.0, 0.0)
    cairo_cr.set_line_width(3.0)

    for line in animation.lines:
        cairo_cr.move_to(line.start.x, line.start.y)
        cairo_cr.line_to(line.end.x, line.end.y)
    cairo_cr.stroke()

    cairo_cr.arc(
        animation.pos.x,
        animation.pos.y,
        animation.dot_size,
        0,
        2 * math.pi
    )
    cairo_cr.fill()
