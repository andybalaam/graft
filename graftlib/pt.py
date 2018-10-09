import attr


@attr.s(cmp=True, frozen=True)
class Pt:
    x = attr.ib()
    y = attr.ib()
