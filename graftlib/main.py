from typing import List, Iterable
import attr

from graftlib.eval_ import eval_  # , eval_debug
from graftlib.lex import lex
from graftlib.lineoptimiser import LineOptimiser
from graftlib.parse import parse
from graftlib.ui.gtk3 import Ui


@attr.s
class World:
    argv: List[str] = attr.ib()
    stdin: Iterable[str] = attr.ib()
    stdout = attr.ib()
    stderr = attr.ib()
    random = attr.ib()


def main(world: World):
    """Run the main program and return the status code to emit"""
    # for command in eval_debug(parse(lex(world.argv[1])), 10):
    #     world.stdout.write("{}\n".format(command))

    opt = LineOptimiser(
        eval_(
            parse(
                lex(world.argv[1])
            ),
            None,
            world.random.uniform
        )
    )

    ui = Ui(opt, opt)
    ui.run()

    return 0
