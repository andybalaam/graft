from typing import Tuple

from graftlib.eval_ import Line, Pt


def _round_float(x: float) -> float:
    """Round to 1 decimal place"""
    return round(x, 1)


def _round_pt(pt: Pt) -> Pt:
    return Pt(_round_float(pt.x), _round_float(pt.y))


def _big_100(x: float) -> float:
    return x if x != -100 else 100


def _modulo_color(rgba: Tuple[float, float, float, float]) -> (
        Tuple[float, float, float, float]
):
    return tuple(
        _big_100(_round_float(((x + 100.0) % 200.0) - 100.0))
        for x in rgba
    )


def round_line(line: Line) -> Line:
    return Line(
        _round_pt(line.start),
        _round_pt(line.end),
        color=_modulo_color(line.color)
    )
