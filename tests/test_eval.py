import itertools
from typing import Iterable, List, Optional, Tuple, Union
from graftlib.eval_ import (
    Dot,
    Line,
    Pt,
    State,
    eval_,
    eval_debug,
)
from graftlib.lex import lex
from graftlib.parse import parse
from graftlib.round_ import round_float, round_stroke


def round_strokes(strokes: Iterable[List[Union[Dot, Line]]]) -> (
        Iterable[List[Union[Dot, Line]]]):
    for par_strokes in strokes:
        yield [round_stroke(stroke) for stroke in par_strokes]


def round_if_float(v):
    if type(v) == float:
        return round_float(v)
    else:
        return v


def round_state(state: State):
    return State(
        env={k: round_if_float(v) for k, v in state.env.items()}
    )


def round_debug(strokes: Iterable[List[Tuple[Optional[Line], State]]]) -> (
        Iterable[List[Tuple[Optional[Union[Dot, Line]], State]]]):
    for par_strokes in strokes:
        yield [
            (
                None if stroke is None else round_stroke(stroke),
                round_state(state)
            ) for (stroke, state) in par_strokes
        ]


def do_eval(chars: Iterable[str], n: int, rand=None):
    return list(round_strokes(eval_(parse(lex(chars)), n, rand)))


def do_eval_debug(chars: Iterable[str], n: int, rand=None):
    return list(
        itertools.islice(
            round_debug(eval_debug(parse(lex(chars)), n, rand)),
            0,
            n
        )
    )


def test_calling_s_moves_forward():
    assert (
        do_eval(":S:S", 2) ==
        [
            [Line(Pt(0.0, 0.0), Pt(0.0, 10.0))],
            [Line(Pt(0.0, 10.0), Pt(0.0, 20.0))],
        ]
    )


def test_incrementing_a_variable_adds_ten():
    assert do_eval("+d", 100) == []  # Does terminate even though no strokes

    assert (
        do_eval_debug("+d", 1) ==
        [[(None, State(env={"x": 0.0, "y": 0.0, "d": 10.0, "s": 10.0}))]]
    )


def test_subtracting_a_variable_removes_ten():
    assert do_eval("-d", 1) == []

    assert (
        do_eval_debug("-d", 1) ==
        [[(None, State(env={"x": 0.0, "y": 0.0, "d": -10.0, "s": 10.0}))]]
    )


def test_subtracting():
    assert (
        do_eval_debug("2-d", 1) ==
        [[(None, State(env={"x": 0.0, "y": 0.0, "d": -2.0, "s": 10.0}))]]
    )
    assert (
        do_eval_debug("-2-d", 1) ==
        [[(None, State(env={"x": 0.0, "y": 0.0, "d": 2.0, "s": 10.0}))]]
    )


def test_dividing():
    assert (
        do_eval_debug("2/s", 1) ==
        [[(None, State(env={"x": 0.0, "y": 0.0, "d": 0.0, "s": 5.0}))]]
    )
    assert (
        do_eval_debug("-2/s", 1) ==
        [[(None, State(env={"x": 0.0, "y": 0.0, "d": 0.0, "s": -5.0}))]]
    )


def test_adding_a_negative_subtracts():
    assert (
        do_eval_debug("-2+d", 1) ==
        [[(None, State(env={"x": 0.0, "y": 0.0, "d": -2.0, "s": 10.0}))]]
    )


def test_multiplying_a_variable():
    assert (
        do_eval_debug("2=d3.1d", 2) ==
        [
            [(None, State(env={"x": 0.0, "y": 0.0, "d": 2.0, "s": 10.0}))],
            [(None, State(env={"x": 0.0, "y": 0.0, "d": 6.2, "s": 10.0}))],
        ]
    )


def test_turn_right_and_move():
    assert do_eval("90+d25=s:S", 1) == [[Line(Pt(0, 0), Pt(25, 0))]]


def test_turn_right_and_jump():
    assert (
        do_eval_debug("90+d25=s:J:S", 4) ==
        [
            [(
                None,
                State(env={"x": 0.0, "y": 0.0, "d": 90.0, "s": 10.0}),
            )],
            [(
                None,
                State(env={"x": 0.0, "y": 0.0, "d": 90.0, "s": 25.0}),
            )],
            [(
                None,
                State(env={"x": 25.0, "y": 0.0, "d": 90.0, "s": 25.0}),
            )],
            [(
                Line(Pt(25.0, 0.0), Pt(50.0, 0.0)),
                State(env={"x": 50.0, "y": 0.0, "d": 90.0, "s": 25.0}),
            )],
        ]
    )


def test_turn_random_and_move():
    def r(_a, _b):
        return 90
    assert do_eval(":R~+d:S", n=1, rand=r) == [[Line(Pt(0, 0), Pt(10, 0))]]


def test_draw_in_different_colour():
    assert (
        do_eval("0.9=r0.5=g0.1=b0.5=a:S0.1=a:S", 2) ==
        [
            [Line(Pt(0.0, 0.0), Pt(0, 10.0), color=(0.9, 0.5, 0.1, 0.5))],
            [Line(Pt(0.0, 10.0), Pt(0, 20.0), color=(0.9, 0.5, 0.1, 0.1))],
        ]
    )


def test_draw_in_different_size():
    assert (
        do_eval("20=z:S5=r:S", 2) ==
        [
            [Line(Pt(0.0, 0.0), Pt(0, 10.0), size=20.0)],
            [Line(
                Pt(0.0, 10.0),
                Pt(0, 20.0),
                size=20.0,
                color=(5.0, 0.0, 0.0, 100.0),
            )],
        ]
    )


def test_repeating_commands():
    assert (
        do_eval("3:S", 3) ==
        [
            [Line(Pt(0.0, 0.0), Pt(0.0, 10.0))],
            [Line(Pt(0.0, 10.0), Pt(0.0, 20.0))],
            [Line(Pt(0.0, 20.0), Pt(0.0, 30.0))],
        ]
    )


def test_repeating_multiple_commands():
    assert (
        do_eval("3:{:S90+d}", 3) ==
        [
            [Line(Pt(0.0, 0.0), Pt(0.0, 10.0))],
            [Line(Pt(0.0, 10.0), Pt(10.0, 10.0))],
            [Line(Pt(10.0, 10.0), Pt(10.0, 0.0))],
        ]
    )


def test_semicolon_to_separate_statements():
    assert do_eval("s;s:S", 1) == [[Line(Pt(0, 0), Pt(0, 10))]]


def test_pass_symbol_to_operator():
    assert do_eval("90=s;s~+d:S", 1) == [[Line(Pt(0, 0), Pt(90, 0))]]


def test_define_custom_variable():
    assert do_eval("180=aa;aa~+d:S", 1) == [[Line(Pt(0, 0), Pt(0, -10))]]


def test_multiply_by_variable():
    assert do_eval("2=aa;aa~s:S", 1) == [[Line(Pt(0, 0), Pt(0, 20))]]


def test_move_in_a_circle():
    assert (
        do_eval(":S+d", 36) ==
        [
            [Line(Pt(0.0, 0.0), Pt(0.0, 10.0))],
            [Line(start=Pt(x=0.0, y=10.0), end=Pt(x=1.7, y=19.8))],
            [Line(start=Pt(x=1.7, y=19.8), end=Pt(x=5.2, y=29.2))],
            [Line(start=Pt(x=5.2, y=29.2), end=Pt(x=10.2, y=37.9))],
            [Line(start=Pt(x=10.2, y=37.9), end=Pt(x=16.6, y=45.6))],
            [Line(start=Pt(x=16.6, y=45.6), end=Pt(x=24.2, y=52.0))],
            [Line(start=Pt(x=24.2, y=52.0), end=Pt(x=32.9, y=57.0))],
            [Line(start=Pt(x=32.9, y=57.0), end=Pt(x=42.3, y=60.4))],
            [Line(start=Pt(x=42.3, y=60.4), end=Pt(x=52.2, y=62.2))],
            [Line(start=Pt(x=52.2, y=62.2), end=Pt(x=62.2, y=62.2))],
            [Line(start=Pt(x=62.2, y=62.2), end=Pt(x=72.0, y=60.4))],
            [Line(start=Pt(x=72.0, y=60.4), end=Pt(x=81.4, y=57.0))],
            [Line(start=Pt(x=81.4, y=57.0), end=Pt(x=90.1, y=52.0))],
            [Line(start=Pt(x=90.1, y=52.0), end=Pt(x=97.7, y=45.6))],
            [Line(start=Pt(x=97.7, y=45.6), end=Pt(x=104.1, y=37.9))],
            [Line(start=Pt(x=104.1, y=37.9), end=Pt(x=109.1, y=29.2))],
            [Line(start=Pt(x=109.1, y=29.2), end=Pt(x=112.6, y=19.8))],
            [Line(start=Pt(x=112.6, y=19.8), end=Pt(x=114.3, y=10.0))],
            [Line(start=Pt(x=114.3, y=10.0), end=Pt(x=114.3, y=0.0))],
            [Line(start=Pt(x=114.3, y=0.0), end=Pt(x=112.6, y=-9.8))],
            [Line(start=Pt(x=112.6, y=-9.8), end=Pt(x=109.1, y=-19.2))],
            [Line(start=Pt(x=109.1, y=-19.2), end=Pt(x=104.1, y=-27.9))],
            [Line(start=Pt(x=104.1, y=-27.9), end=Pt(x=97.7, y=-35.6))],
            [Line(start=Pt(x=97.7, y=-35.6), end=Pt(x=90.1, y=-42.0))],
            [Line(start=Pt(x=90.1, y=-42.0), end=Pt(x=81.4, y=-47.0))],
            [Line(start=Pt(x=81.4, y=-47.0), end=Pt(x=72.0, y=-50.4))],
            [Line(start=Pt(x=72.0, y=-50.4), end=Pt(x=62.2, y=-52.2))],
            [Line(start=Pt(x=62.2, y=-52.2), end=Pt(x=52.2, y=-52.2))],
            [Line(start=Pt(x=52.2, y=-52.2), end=Pt(x=42.3, y=-50.4))],
            [Line(start=Pt(x=42.3, y=-50.4), end=Pt(x=32.9, y=-47.0))],
            [Line(start=Pt(x=32.9, y=-47.0), end=Pt(x=24.2, y=-42.0))],
            [Line(start=Pt(x=24.2, y=-42.0), end=Pt(x=16.6, y=-35.6))],
            [Line(start=Pt(x=16.6, y=-35.6), end=Pt(x=10.2, y=-27.9))],
            [Line(start=Pt(x=10.2, y=-27.9), end=Pt(x=5.2, y=-19.2))],
            [Line(start=Pt(x=5.2, y=-19.2), end=Pt(x=1.7, y=-9.8))],
            [Line(start=Pt(x=1.7, y=-9.8), end=Pt(x=-0.0, y=-0.0))],
        ]
    )


def test_draw_a_dot():
    assert do_eval(":D", 1) == [[Dot(Pt(0.0, 0.0))]]
    assert do_eval("20=x15=y:D", 1) == [[Dot(Pt(20.0, 15.0))]]


def test_go_then_line():
    assert (
        do_eval("10=x15=y20=x16=y:L", 1) ==
        [[Line(Pt(10.0, 15.0), Pt(20.0, 16.0))]]
    )


def test_repeat_starts_at_beginning_if_no_label():
    assert (
        do_eval("90=d90+d:S", 2) ==
        [
            [Line(Pt(0, 0), Pt(0, -10.0))],
            [Line(Pt(0, -10), Pt(0, -20.0))],
        ]
    )


def test_repeat_starts_at_label_if_present():
    assert (
        do_eval("90=d^90+d:S", 2) ==
        [
            [Line(Pt(0, 0), Pt(0, -10.0))],
            [Line(Pt(0, -10), Pt(-10.0, -10.0))],
        ]
    )


def test_fork_draws_lines_in_parallel():
    assert (
        do_eval(":F:S", 1) ==
        [
            [Line(Pt(0, 0), Pt(0, 10.0)), Line(Pt(0, 0), Pt(0, 10.0))],
        ]
    )


def test_fork_increments_the_f_variable():
    expected_state_0 = State()
    expected_state_1 = State()
    expected_state_1.set_variable("f", 1)
    result = do_eval_debug(":F0+d", 2)  # Fork, then add zero to d
    print(result)

    assert len(result) == 2
    assert len(result[1]) == 2
    state_0 = result[1][0][1]
    state_1 = result[1][1][1]
    assert state_0.get_variable("f") == 0
    assert state_1.get_variable("f") == 1
