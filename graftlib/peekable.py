from typing import Iterator, Optional
import attr


@attr.s
class Peekable:
    _it: Iterator = attr.ib()
    _nxt = attr.ib(None, init=False)

    def __attrs_post_init__(self) -> None:
        self._nxt = self._move_next()

    def _move_next(self) -> Optional:
        try:
            return next(self._it)
        except StopIteration:
            return None

    def peek(self) -> str:
        if self._nxt is None:
            raise StopIteration()
        else:
            return self._nxt

    def __iter__(self) -> Iterator:
        return self

    def __next__(self) -> str:
        if self._nxt is None:
            raise StopIteration()
        else:
            ret = self._nxt
            self._nxt = self._move_next()
            return ret
