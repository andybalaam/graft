from typing import List, Iterable
import attr


@attr.s
class World:
    argv = attr.ib()
    stdin = attr.ib()
    stdout = attr.ib()
    stderr = attr.ib()
    random = attr.ib()
    fs = attr.ib()
