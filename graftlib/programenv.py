import attr


@attr.s
class ProgramEnv:
    """
    Wraps an Env, holding onto a random number generator
    and a fork_callback.  These are both specific to Graft
    whereas Env is general to Graft's variant of the Cell
    syntax.

    Allows adding strokes to the output by calling stroke().
    """

    env = attr.ib()
    rand = attr.ib()
    fork_callback = attr.ib()
    eval_expr = attr.ib()
    _strokes = attr.ib(default=attr.Factory(list))

    def parent(self):
        return self.env.parent()

    def clone(self):
        return ProgramEnv(
            self.env.clone(),
            self.rand,
            self.fork_callback,
            self.eval_expr,
        )

    def make_child(self):
        return ProgramEnv(
            self.env.make_child(),
            self.rand,
            self.fork_callback,
            self.eval_expr,
            self._strokes,
        )

    def stroke(self, st):
        self._strokes.append(st)

    def clear_strokes(self):
        """
        Returns the collected strokes and clears
        the list so more may be added.
        """
        ret = self._strokes
        self._strokes = []
        return ret

    def get(self, name):
        return self.env.get(name)

    def set(self, name, value):
        # x and y are magic variables that remember their previous values
        if name == "x":
            self.env.set("xprev", self.env.get("x"))
        elif name == "y":
            self.env.set("yprev", self.env.get("y"))
        return self.env.set(name, value)

    def set_new(self, name, value):
        return self.env.set_new(name, value)

    def contains(self, name):
        return self.env.contains(name)

    def local_items(self):
        return self.env.local_items()

    def __str__(self):
        return str(self.env)
