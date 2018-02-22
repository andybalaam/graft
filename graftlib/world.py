from typing import List, Iterable
import attr


@attr.s
class World:
    argv: List[str] = attr.ib()
    stdin: Iterable[str] = attr.ib()
    stdout = attr.ib()
    stderr = attr.ib()
    random = attr.ib()
    fs = attr.ib()
