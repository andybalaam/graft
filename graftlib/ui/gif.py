from graftlib.animation import Animation
from graftlib.world import World


class GifUi:
    def __init__(self, animation: Animation, filename: str, world: World):
        self.animation = animation
        self.filename = filename
        self.world = world

    def run(self):
        return 0

# import cairo
# ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, 390, 60)
# cr2 = cairo.Context(ims)
# cr2.arc(
#     self.pos.x,
#     self.pos.y,
#     dot_size,
#     0,
#     2 * math.pi
# )
# cr2.fill()
# # ims.write_to_png("image.png")
# print(dir(ims))
