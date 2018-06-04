from typing import Optional, Tuple
from argparse import ArgumentParser

from graftlib.animation import Animation
from graftlib.env import Env
from graftlib.eval_ import eval_
from graftlib.eval2 import eval_ as eval2
from graftlib.lex import lex
from graftlib.lex2 import lex as lex2
from graftlib.strokeoptimiser import StrokeOptimiser
from graftlib.parse import parse
from graftlib.parse2 import parse as parse2
from graftlib.world import World
from graftlib.ui.gtk3ui import Gtk3Ui
from graftlib.ui.gifui import GifUi


# How many strokes we are allowed before we start deleting old ones.
max_strokes = 500


# Size of the dot indicating where we are.
dot_size = 5


# Default screen size in pixels if not overridden by --width, --height
default_width = 200
default_height = 200


# Default number of parallel forks if not overridden by --max-forks
default_max_forks = 100


# How far to run the animation initially to decide what
# our initial zoom level should be.
default_lookahead_steps = 80


def main_gif(
        animation: Animation,
        frames: Optional[int],
        filename: str,
        world: World,
        image_size: Tuple[int, int],
) -> int:
    if frames is None:
        world.stderr.write(
            "You must supply a --frames=n argument to use --gif.  " +
            "(Otherwise we'd make an infinite-sized gif?)\n"
        )
        return 3

    return GifUi(animation, filename, world, image_size).run()


def main_gtk3(animation: Animation, image_size: Tuple[int, int]) -> int:
    return Gtk3Ui(animation, image_size).run()


def make_animation(
        program: str,
        frames: Optional[int],
        rand,
        max_forks: int,
        lookahead_steps: int,
):
    """
    Given a program, return an iterator that lexes, parses,
    evaluates and optimises it, yielding actual strokes to draw on
    the screen, limited to the number of frames supplied, and using
    the random number generator supplied.
    """
    opt = StrokeOptimiser(
        eval_(parse(lex(program)), frames, rand, max_forks)
    )
    frames = lookahead_steps if frames is None else frames
    lookahead = min(frames, lookahead_steps)
    return Animation(opt, opt, lookahead, max_strokes, dot_size)


def make_animation2(
        program: str,
        frames: Optional[int],
        rand,
        max_forks: int,
        lookahead_steps: int,
):
    """
    Given a program, return an iterator that lexes, parses,
    evaluates and optimises it, yielding actual strokes to draw on
    the screen, limited to the number of frames supplied, and using
    the random number generator supplied.
    """
    opt = StrokeOptimiser(
        eval2(parse2(lex2(program)), Env())
    )
    # , frames, rand, max_forks
    frames = lookahead_steps if frames is None else frames
    lookahead = min(frames, lookahead_steps)
    return Animation(opt, opt, lookahead, max_strokes, dot_size)


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
        '--width',
        default=default_width,
        type=int,
        help="The width in pixels of the animation.",
    )
    argparser.add_argument(
        '--height',
        default=default_height,
        type=int,
        help="The height in pixels of the animation.",
    )
    argparser.add_argument(
        '--max-forks',
        default=default_max_forks,
        type=int,
        help="The number of forked lines that can run in parallel.",
    )
    argparser.add_argument(
        '--lookahead-steps',
        default=default_lookahead_steps,
        type=int,
        help="How many steps to use to calculate the initial zoom level.",
    )
    argparser.add_argument(
        '--cell',
        action="store_true",
        help="Write programs in Cell, instead of normal Graft syntax.",
    )
    argparser.add_argument(
        'program',
        help="The actual graft program to run, e.g. '+d:S' to draw a circle."
    )

    args = argparser.parse_args(world.argv[1:])

    frames = None if args.frames < 0 else args.frames

    if args.cell:
        animation = make_animation2(
            args.program,
            frames,
            world.random.uniform,
            args.max_forks,
            args.lookahead_steps,
        )
    else:
        animation = make_animation(
            args.program,
            frames,
            world.random.uniform,
            args.max_forks,
            args.lookahead_steps,
        )
    image_size = (args.width, args.height)

    if args.gif:
        return main_gif(animation, frames, args.gif, world, image_size)
    else:
        return main_gtk3(animation, image_size)
