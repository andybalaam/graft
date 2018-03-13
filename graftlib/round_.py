from typing import Tuple

from graftlib.eval_ import Line, Pt


def round_float(x: float) -> float:
    """Round to 1 decimal place"""
    return round(x, 1)


def round_pt(pt: Pt) -> Pt:
    return Pt(round_float(pt.x), round_float(pt.y))


def _modulo_100(x: float) -> float:
    ret = ((x + 100.0) % 200.0) - 100.0   # within [-100, 100)
    ret = round_float(ret)
    return 100.0 if ret == -100.0 else ret  # within (-100, 100]


def _modulo_color(rgba: Tuple[float, float, float, float]) -> (
        Tuple[float, float, float, float]
):
    return tuple(_modulo_100(x) for x in rgba)


def round_line(line: Line) -> Line:
    return Line(
        round_pt(line.start),
        round_pt(line.end),
        color=_modulo_color(line.color),
        size=_modulo_100(line.size),
    )
