from typing import List, Iterable
import attr

from graftlib.eval_ import eval_debug
from graftlib.lex import lex
from graftlib.parse import parse


@attr.s
class World:
    argv: List[str] = attr.ib()
    stdin: Iterable[str] = attr.ib()
    stdout = attr.ib()
    stderr = attr.ib()


def main(world: World):
    """Run the main program and return the status code to emit"""
    for command in eval_debug(parse(lex(world.argv[1])), 10):
        world.stdout.write("{}\n".format(command))
    return 0
