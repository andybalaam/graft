from graftlib.eval_ import Line, Pt


def _round_float(x: float) -> float:
    """Round to 1 decimal place"""
    return round(x, 1)


def _round_pt(pt: Pt) -> Pt:
    return Pt(_round_float(pt.x), _round_float(pt.y))


def round_line(line: Line) -> Line:
    return Line(_round_pt(line.start), _round_pt(line.end))
