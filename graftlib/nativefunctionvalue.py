import attr


@attr.s
class NativeFunctionValue:
    py_fn = attr.ib()
