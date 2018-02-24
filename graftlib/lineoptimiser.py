from typing import Iterator, Set, Tuple, Union
import attr

from graftlib.eval_ import Line, Pt
from graftlib.round_ import round_line


@attr.s
class ElidedLine:
    start: Pt = attr.ib()
    end: Pt = attr.ib()
    color: Tuple = attr.ib(default=(0.0, 0.0, 0.0, 100.0))
    size: float = attr.ib(default=5.0)


@attr.s
class LineOptimiser:
    """
    Adapt a stream of lines into a stream of lines that are
    unique after rounding to 1 decimal place.
    For any lines we are removing because they repeat a previous
    line, we emit an ElidedLine instead.
    """

    lines: Iterator = attr.ib()
    seen_lines: Set[Line] = attr.ib(attr.Factory(set), init=False)

    def __iter__(self):
        return self

    def __next__(self) -> Union[Line, ElidedLine]:
        ln = round_line(next(self.lines))
        if ln in self.seen_lines:
            return ElidedLine(ln.start, ln.end, ln.color, ln.size)
        else:
            self.seen_lines.add(ln)
            return ln

    def delete_line(self, line: Line):
        """
        Forget that this line has been drawn, so if we draw it
        again, it won't be elided.
        """
        self.seen_lines.remove(line)
