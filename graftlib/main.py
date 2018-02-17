from typing import List, Iterable
import attr

from graftlib.lex import lex


@attr.s
class World:
    argv: List[str] = attr.ib()
    stdin: Iterable[str] = attr.ib()
    stdout = attr.ib()
    stderr = attr.ib()


def main(world: World):
    """Run the main program and return the status code to emit"""
    for token in lex(world.stdin):
        world.write("{}\n".format(token))
    return 0
