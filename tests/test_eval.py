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
        do_eval_debug("2=d3d") ==
        [
            (None, State(pos=Pt(0.0, 0.0), dir_=2.0, step=10.0)),
            (None, State(pos=Pt(0.0, 0.0), dir_=6.0, step=10.0)),
        ]
    )


def test_turn_right_and_move():
    assert do_eval("90+d25=s:S") == [Line(Pt(0, 0), Pt(25, 0))]


def test_turn_random_and_move():
    def r(_a, _b):
        return 90
    assert do_eval(":R~+d:S", rand=r) == [Line(Pt(0, 0), Pt(10, 0))]


def tIGNOREest_move_in_a_circle():
    """Waiting for the optimiser to make this readable"""
    assert (
        do_eval(":S+d", 10) ==
        [
            Line(Pt(0, 0), Pt(0, 10.0)),
        ]
    )
