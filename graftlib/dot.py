from typing import Tuple

import attr

from graftlib.pt import Pt


@attr.s(cmp=True, frozen=True)
class Dot():
    pos = attr.ib()
    color = attr.ib(default=(0.0, 0.0, 0.0, 100.0))
    size = attr.ib(default=5.0)
