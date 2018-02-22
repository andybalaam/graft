from typing import Optional
import attr


def _limit(val, r):
    if val < -r:
        return -r
    elif val > r:
        return r
    else:
        return val


@attr.s
class _SmoothValue:
    value: float = attr.ib()
    _v: float = attr.ib(0, init=False)

    def set_target(self, target: float):
        self._v += 0.5 * (target - self.value)  # Acceleration
        self._v = _limit(self._v, 200.0) * 0.2     # Limit + damping
        self.value += self._v


@attr.s
class WindowAnimator:
    """
    Given the translation and scale we _want_ to be at,
    provide actual translation and scale that smoothly
    animate towards that.
    """

    lookahead_steps = attr.ib()

    x: Optional[_SmoothValue] = attr.ib(None, init=False)
    y: Optional[_SmoothValue] = attr.ib(None, init=False)
    w: Optional[_SmoothValue] = attr.ib(None, init=False)
    h: Optional[_SmoothValue] = attr.ib(None, init=False)

    counter: int = attr.ib(0, init=False)

    def animate(self, extents, window_size) -> (float, float, float):
        centre = extents.centre()
        size = extents.size()
        if self.x is None:
            self.x = _SmoothValue(centre[0])
            self.y = _SmoothValue(centre[1])
            self.w = _SmoothValue(size[0])
            self.h = _SmoothValue(size[1])
        return self.move(centre, size, window_size)

    def move(self, centre, size, window_size) -> (float, float, float):

        if self.counter >= self.lookahead_steps:
            self.x.set_target(centre[0])
            self.y.set_target(centre[1])
            self.w.set_target(size[0])
            self.h.set_target(size[1])
        self.counter += 1

        scale = (
            0.8 *
            min(
                window_size[0] / self.w.value if self.w.value != 0 else 1,
                window_size[1] / self.h.value if self.h.value != 0 else 1,
            )
        )
        if scale > 2.0:
            scale = 2.0
        x = -self.x.value * scale + (window_size[0] / 2)
        y = -self.y.value * scale + (window_size[1] / 2)

        return (x, y, scale)
