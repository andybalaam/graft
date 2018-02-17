from typing import Iterable
from graftlib.eval_ import (
    Line,
    Pt,
    State,
    eval_,
    eval_debug,
)
from graftlib.lex import lex
from graftlib.parse import parse


def do_eval(chars: Iterable[str], n: int = 1):
    return list(eval_(parse(lex(chars)), n))


def do_eval_debug(chars: Iterable[str], n: int = 1):
    return list(eval_debug(parse(lex(chars)), n))


def test_calling_s_moves_forward():
    assert do_eval(":s") == [Line(Pt(0, 0), Pt(0, 10))]


def test_incrementing_a_variable_does_nothing():
    assert do_eval("+d") == []
    assert do_eval_debug("+d") == [(None, State(pos=Pt(0, 0), dir_=10))]


def test_move_in_a_circle():
    assert (
        do_eval(":s+d", 10) ==
        [
            Line(Pt(0, 0), Pt(0, 10)),
        ]
    )
