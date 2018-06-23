import attr


@attr.s
class ProgramEnv:
    """
    Wraps an Env, holding onto a random number generator
    and a fork_callback.  These are both specific to Graft
    whereas Env is general to Graft's variant of the Cell
    syntax
    """

    env = attr.ib()
    rand = attr.ib()
    fork_callback = attr.ib()
    eval_expr = attr.ib()

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
        )

    def get(self, name):
        return self.env.get(name)

    def set(self, name, value):
        return self.env.set(name, value)

    def set_new(self, name, value):
        return self.env.set_new(name, value)

    def contains(self, name):
        return self.env.contains(name)

    def local_items(self):
        return self.env.local_items()

    def __str__(self):
        return str(self.env)
