from typing import Tuple

import attr

from graftlib.pt import Pt


@attr.s(cmp=True, frozen=True)
class Dot():
    pos: Pt = attr.ib()
    color: Tuple = attr.ib(default=(0.0, 0.0, 0.0, 100.0))
    size: float = attr.ib(default=5.0)
