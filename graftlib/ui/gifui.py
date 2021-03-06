import subprocess
from typing import Tuple
import cairo

from graftlib.animation import Animation
from graftlib.world import World
from graftlib.ui.cairo_draw import cairo_draw


class GifUi:
    def __init__(
            self,
            animation: Animation,
            filename: str,
            world: World,
            image_size: Tuple[int, int],
    ):
        self.animation = animation
        self.filename = filename
        self.world = world
        self.image_size = image_size

    def run(self):
        with self.world.fs.tmpdir() as tmpdir:
            n = 0
            more_frames = self.animation.step()
            while more_frames:
                n += 1
                self._draw_frame(n, tmpdir)
                more_frames = self.animation.step()

            # Copy the frame images so we can examine them
            # args = [
            #      "cp",
            #      "-r",
            #      "{dir_}/".format(dir_=tmpdir),
            #      "./",
            # ]
            # self.world.stdout.write("$ %s\n" % (" ".join(args)))
            # subprocess.run(args)

            # Create gif using ffmpeg
            # args = [
            #     "ffmpeg",
            #     "-loglevel",
            #     "warning",
            #     "-y",
            #     "-i",
            #     "{dir_}/frame_%d.png".format(dir_=tmpdir),
            #     self.filename
            # ]
            # self.world.stdout.write("$ %s\n" % (" ".join(args)))
            # subprocess.run(args)

            args = [
                "convert",
                "-delay",
                "5",
                "{dir_}/frame_*.png".format(dir_=tmpdir),
                self.filename
            ]
            # self.world.stdout.write("$ %s\n" % (" ".join(args)))
            subprocess.run(args)

    def _draw_frame(self, frame_number, tmpdir):
        ims = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, self.image_size[0], self.image_size[1])

        cairo_cr = cairo.Context(ims)

        cairo_draw(
            self.animation,
            cairo_cr,
            ims.get_width(),
            ims.get_height(),
        )

        ret = "{dir_}/frame_{num:04}.png".format(dir_=tmpdir, num=frame_number)

        ims.write_to_png(ret)
        return ret
