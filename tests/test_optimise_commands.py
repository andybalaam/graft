from graftlib.eval_ import Line, Pt
from graftlib.lineoptimiser import ElidedLine, LineOptimiser


n = Line
p = Pt
e = ElidedLine


def opt(lines):
    return [ln for ln in LineOptimiser(iter(lines))]


def test_lines_are_rounded_to_1_decimal_place():
    bef = [n(p(0.12, 0.56), p(0.5, 2.91))]
    aft = [n(p(0.1, 0.6), p(0.5, 2.9))]
    assert opt(bef) == aft


def test_distinct_lines_are_preserved():
    bef = [n(p(0.12, 0.56), p(0.5, 0.91)), n(p(2.31, 1.4), p(0.5, 0.91))]
    aft = [n(p(0.1, 0.6), p(0.5, 0.9)), n(p(2.3, 1.4), p(0.5, 0.9))]
    assert opt(bef) == aft


def test_lines_identical_after_rounding_are_elided():
    bef = [n(p(0.12, 0.56), p(0.5, 0.91)), n(p(0.09, 0.61), p(0.46, 0.91))]
    aft = [n(p(0.1, 0.6), p(0.5, 0.9)), e(p(0.1, 0.6), p(0.5, 0.9))]
    assert opt(bef) == aft


def test_lines_that_were_removed_from_optimiser_do_not_cause_elision():
    def some_lines_that_then_get_removed():
        yield n(p(1, 1), p(1, 1))
        yield n(p(2, 2), p(2, 2))
        yield n(p(3, 3), p(3, 3))
        yield n(p(2, 2), p(2, 2))
        optimiser.delete_line(n(p(2, 2), p(2, 2)))
        yield n(p(2, 2), p(2, 2))
        yield n(p(3, 3), p(3, 3))

    optimiser = LineOptimiser(some_lines_that_then_get_removed())

    assert (
        [ln for ln in optimiser] ==
        [
            n(p(1, 1), p(1, 1)),
            n(p(2, 2), p(2, 2)),
            n(p(3, 3), p(3, 3)),
            e(p(2, 2), p(2, 2)),  # Elided, but then we delete it ...
            n(p(2, 2), p(2, 2)),  # ... so not elided when it comes again.
            e(p(3, 3), p(3, 3)),  # Elided because it was never deleted.
        ]
    )
