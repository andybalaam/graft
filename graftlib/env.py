from graftlib.numbervalue import NumberValue


class Env:
    def __init__(
        self,
        rand,
        fork_callback,
        parent=None,
        stdin=None,
        stdout=None,
        stderr=None
    ):
        """
        Supply _either_ std{in,out,err} _or_ parent, not both.
        """
        self.rand = rand
        self.fork_callback = fork_callback
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.parent = parent
        if parent is not None:
            assert stdin is None
            assert stdout is None
            assert stderr is None
            self.stdin = parent.stdin
            self.stdout = parent.stdout
            self.stderr = parent.stderr
        self.items = {}

    def clone(self):
        parent = None if self.parent is None else self.parent.clone()
        ret = Env(
            self.rand,
            self.fork_callback,
            parent=parent,
            stdin=self.stdin,
            stdout=self.stdout,
            stderr=self.stderr,
        )
        for k, v in self.items.items():
            ret.set(k, v)
        return ret

    def make_child(self):
        return Env(
            self.rand,
            self.fork_callback,
            parent=self,
        )

    def get(self, name):
        if name in self.items:
            return self.items[name]
        elif self.parent is not None:
            return self.parent.get(name)
        else:
            self.items[name] = NumberValue(0.0)
            return self.items[name]

    def set(self, name, value):
        self.items[name] = value

    def contains(self, name):
        return name in self.items

    def __str__(self):
        ret = ""
        for k, v in self.items.items():
            ret += "%s=%s\n" % (k, v)
        ret += ".\n" + str(self.parent)
        return ret
