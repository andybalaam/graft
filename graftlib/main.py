from typing import Optional
from argparse import ArgumentParser

from graftlib.animation import Animation
from graftlib.eval_ import eval_  # , eval_debug
from graftlib.lex import lex
from graftlib.lineoptimiser import LineOptimiser
from graftlib.parse import parse
from graftlib.world import World
from graftlib.ui.gtk3ui import Gtk3Ui
from graftlib.ui.gifui import GifUi


# How far to run the animation initially to decide what
# our initial zoom level should be.
lookahead_steps = 100


# How many lines we allowed before we start deleting old ones.
max_lines = 500


# Size of the dot indicating where we are.
dot_size = 5


def main_gif(
        animation: Animation,
        frames: Optional[int],
        filename: str,
        world: World,
) -> int:
    if frames is None:
        world.stderr.write(
            "You must supply a --frames=n argument to use --gif.  " +
            "(Otherwise we'd make an infinite-sized gif?)\n"
        )
        return 3

    return GifUi(animation, filename, world).run()


def main_gtk3(animation) -> int:
    return Gtk3Ui(animation).run()


def make_animation(program: str, frames: Optional[int], rand):
    """
    Given a program, return an iterator that lexes, parses,
    evaluates and optimises it, yielding actual lines to draw on
    the screen, limited to the number of frames supplied, and using
    the random number generator supplied.
    """
    opt = LineOptimiser(eval_(parse(lex(program)), frames, rand))
    return Animation(opt, opt, lookahead_steps, max_lines, dot_size)


def main(world: World) -> int:
    """Run the main program and return the status code to emit"""
    # for command in eval_debug(parse(lex(world.argv[1])), 10):
    #     world.stdout.write("{}\n".format(command))

    argparser = ArgumentParser(prog='graft')
    argparser.add_argument(
        '--frames',
        metavar="NUMBER_OF_FRAMES",
        default=-1,
        type=int,
        help=(
            "How many frames of the animation to draw, " +
            "or -1 to play forever."
        ),
    )
    argparser.add_argument(
        '--gif',
        metavar="GIF_FILENAME",
        help=(
            "Make an animated GIF instead of displaying on screen.  " +
            "(Requires --frames=n where n > 0.)"
        ),
    )
    argparser.add_argument(
        'program',
        help="The actual graft program to run, e.g. '+d:S' to draw a circle."
    )

    args = argparser.parse_args(world.argv[1:])

    frames = None if args.frames < 0 else args.frames
    animation = make_animation(args.program, frames, world.random.uniform)

    if args.gif:
        return main_gif(animation, frames, args.gif, world)
    else:
        return main_gtk3(animation)
