from graftlib.numbervalue import NumberValue


class Env:
    def __init__(
        self,
        parent=None,
        stdin=None,
        stdout=None,
        stderr=None
    ):
        """
        Supply _either_ std{in,out,err} _or_ parent, not both.
        """
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self._parent = parent
        if parent is not None:
            assert stdin is None
            assert stdout is None
            assert stderr is None
            self.stdin = parent.stdin
            self.stdout = parent.stdout
            self.stderr = parent.stderr
        self._items = {}

    def parent(self):
        return self._parent

    def clone(self):
        parent = None if self._parent is None else self._parent.clone()
        ret = Env(
            parent=parent,
            stdin=self.stdin,
            stdout=self.stdout,
            stderr=self.stderr,
        )
        for k, v in self._items.items():
            ret.set(k, v)
        return ret

    def make_child(self):
        return Env(parent=self)

    def get(self, name):
        if name in self._items:
            return self._items[name]
        elif self._parent is not None:
            return self._parent.get(name)
        else:
            self._items[name] = NumberValue(0.0)
            return self._items[name]

    def set(self, name, value):
        self._items[name] = value

    def contains(self, name):
        return name in self._items

    def local_items(self):
        return self._items

    def __str__(self):
        ret = ""
        for k, v in self.items.items():
            ret += "%s=%s\n" % (k, v)
        ret += ".\n" + str(self._parent)
        return ret
