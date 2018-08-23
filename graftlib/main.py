from typing import Optional, Tuple
from argparse import ArgumentParser

from graftlib.animation import Animation
from graftlib.env import Env
from graftlib.eval_cell import eval_cell
from graftlib.eval_v1 import eval_v1
from graftlib.graftrun import graftrun
from graftlib.lex_cell import lex_cell
from graftlib.lex_v1 import lex_v1
from graftlib.strokeoptimiser import StrokeOptimiser
from graftlib.parse_cell import parse_cell
from graftlib.parse_v1 import parse_v1
from graftlib.world import World
from graftlib.ui.gtk3ui import Gtk3Ui
from graftlib.ui.gifui import GifUi


# How many strokes we are allowed before we start deleting old ones.
max_strokes = 200


# Size of the dot indicating where we are.
dot_size = 5


# Default screen size in pixels if not overridden by --width, --height
default_width = 200
default_height = 200


# Default number of parallel forks if not overridden by --max-forks
default_max_forks = 20


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
        program_values,
        frames: Optional[int],
        lookahead_steps: int,
):
    """
    Given the values from evaluating a program, return an iterator that
    optimises it, yielding actual strokes to draw on the screen, limited to the
    number of frames supplied, and using the random number generator supplied.
    """
    opt = StrokeOptimiser(program_values)
    frames = lookahead_steps if frames is None else frames
    lookahead = min(frames, lookahead_steps)
    return Animation(opt, opt, lookahead, max_strokes, dot_size)


def main(world: World) -> int:
    """Run the main program and return the status code to emit"""

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
        '--syntax',
        choices=["v1", "cell"],
        default="cell",
        help=(
            "Choose which code style you want to use - v1 syntax uses " +
            "e.g. :R to call the R function, whereas cell syntax uses " +
            "the more familiar R().  For more info on the v1 syntax, " +
            "see SYNTAX_V1.md in the source repository."
        ),
    )
    argparser.add_argument(
        'program',
        help=(
            "The actual graft program to run, e.g. 'd+=10 S()' " +
            "to draw a circle."
        )
    )

    args = argparser.parse_args(world.argv[1:])

    frames = None if args.frames < 0 else args.frames

    if args.syntax == "v1":
        lex = lex_v1
        parse = parse_v1
        eval_expr = eval_v1
    else:
        lex = lex_cell
        parse = parse_cell
        eval_expr = eval_cell

    program_values = graftrun(
        parse(lex(args.program)),
        frames,
        world.random.uniform,
        args.max_forks,
        eval_expr,
    )

    animation = make_animation(program_values, frames, args.lookahead_steps)
    image_size = (args.width, args.height)

    if args.gif:
        return main_gif(animation, frames, args.gif, world, image_size)
    else:
        return main_gtk3(animation, image_size)
