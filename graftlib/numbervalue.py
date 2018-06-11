import attr


@attr.s
class NumberValue:
    value: float = attr.ib()
