from typing import Iterable, Optional, Tuple
from graftlib.eval_ import (
    Line,
    Pt,
    State,
    eval_,
    eval_debug,
)
from graftlib.lex import lex
from graftlib.parse import parse
from graftlib.round_ import round_line


def round_lines(lines: Iterable[Line]) -> Iterable[Line]:
    for ln in lines:
        yield round_line(ln)


def round_debug(lines: Iterable[Tuple[Optional[Line], State]]) -> (
        Iterable[Tuple[Optional[Line], State]]):
    for (ln, state) in lines:
        yield (
            None if ln is None else round_line(ln.start),
            state
        )


def do_eval(chars: Iterable[str], n: int = 1, rand=None):
    return list(round_lines(eval_(parse(lex(chars)), n, rand)))


def do_eval_debug(chars: Iterable[str], n: int = 1, rand=None):
    return list(round_debug(eval_debug(parse(lex(chars)), n, rand)))


def test_calling_s_moves_forward():
    assert (
        do_eval(":S:S") ==
        [
            Line(Pt(0.0, 0.0), Pt(0.0, 10.0)),
            Line(Pt(0.0, 10.0), Pt(0.0, 20.0)),
        ]
    )


def test_incrementing_a_variable_adds_ten():
    assert do_eval("+d") == []

    assert (
        do_eval_debug("+d") ==
        [(None, State(pos=Pt(0.0, 0.0), dir_=10.0, step=10.0))]
    )


def test_multiplying_a_variable():
    assert (
        do_eval_debug("2=d3.1d") ==
        [
            (None, State(pos=Pt(0.0, 0.0), dir_=2.0, step=10.0)),
            (None, State(pos=Pt(0.0, 0.0), dir_=6.2, step=10.0)),
        ]
    )


def test_turn_right_and_move():
    assert do_eval("90+d25=s:S") == [Line(Pt(0, 0), Pt(25, 0))]


def test_turn_random_and_move():
    def r(_a, _b):
        return 90
    assert do_eval(":R~+d:S", rand=r) == [Line(Pt(0, 0), Pt(10, 0))]


def test_move_in_a_circle():
    assert (
        do_eval(":S+d", 36) ==
        [
            Line(Pt(0.0, 0.0), Pt(0.0, 10.0)),
            Line(start=Pt(x=0.0, y=10.0), end=Pt(x=1.7, y=19.8)),
            Line(start=Pt(x=1.7, y=19.8), end=Pt(x=5.2, y=29.2)),
            Line(start=Pt(x=5.2, y=29.2), end=Pt(x=10.2, y=37.9)),
            Line(start=Pt(x=10.2, y=37.9), end=Pt(x=16.6, y=45.6)),
            Line(start=Pt(x=16.6, y=45.6), end=Pt(x=24.2, y=52.0)),
            Line(start=Pt(x=24.2, y=52.0), end=Pt(x=32.9, y=57.0)),
            Line(start=Pt(x=32.9, y=57.0), end=Pt(x=42.3, y=60.4)),
            Line(start=Pt(x=42.3, y=60.4), end=Pt(x=52.2, y=62.2)),
            Line(start=Pt(x=52.2, y=62.2), end=Pt(x=62.2, y=62.2)),
            Line(start=Pt(x=62.2, y=62.2), end=Pt(x=72.0, y=60.4)),
            Line(start=Pt(x=72.0, y=60.4), end=Pt(x=81.4, y=57.0)),
            Line(start=Pt(x=81.4, y=57.0), end=Pt(x=90.1, y=52.0)),
            Line(start=Pt(x=90.1, y=52.0), end=Pt(x=97.7, y=45.6)),
            Line(start=Pt(x=97.7, y=45.6), end=Pt(x=104.1, y=37.9)),
            Line(start=Pt(x=104.1, y=37.9), end=Pt(x=109.1, y=29.2)),
            Line(start=Pt(x=109.1, y=29.2), end=Pt(x=112.6, y=19.8)),
            Line(start=Pt(x=112.6, y=19.8), end=Pt(x=114.3, y=10.0)),
            Line(start=Pt(x=114.3, y=10.0), end=Pt(x=114.3, y=0.0)),
            Line(start=Pt(x=114.3, y=0.0), end=Pt(x=112.6, y=-9.8)),
            Line(start=Pt(x=112.6, y=-9.8), end=Pt(x=109.1, y=-19.2)),
            Line(start=Pt(x=109.1, y=-19.2), end=Pt(x=104.1, y=-27.9)),
            Line(start=Pt(x=104.1, y=-27.9), end=Pt(x=97.7, y=-35.6)),
            Line(start=Pt(x=97.7, y=-35.6), end=Pt(x=90.1, y=-42.0)),
            Line(start=Pt(x=90.1, y=-42.0), end=Pt(x=81.4, y=-47.0)),
            Line(start=Pt(x=81.4, y=-47.0), end=Pt(x=72.0, y=-50.4)),
            Line(start=Pt(x=72.0, y=-50.4), end=Pt(x=62.2, y=-52.2)),
            Line(start=Pt(x=62.2, y=-52.2), end=Pt(x=52.2, y=-52.2)),
            Line(start=Pt(x=52.2, y=-52.2), end=Pt(x=42.3, y=-50.4)),
            Line(start=Pt(x=42.3, y=-50.4), end=Pt(x=32.9, y=-47.0)),
            Line(start=Pt(x=32.9, y=-47.0), end=Pt(x=24.2, y=-42.0)),
            Line(start=Pt(x=24.2, y=-42.0), end=Pt(x=16.6, y=-35.6)),
            Line(start=Pt(x=16.6, y=-35.6), end=Pt(x=10.2, y=-27.9)),
            Line(start=Pt(x=10.2, y=-27.9), end=Pt(x=5.2, y=-19.2)),
            Line(start=Pt(x=5.2, y=-19.2), end=Pt(x=1.7, y=-9.8)),
            Line(start=Pt(x=1.7, y=-9.8), end=Pt(x=-0.0, y=-0.0))
        ]
    )
