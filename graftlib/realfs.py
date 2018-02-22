from tempfile import TemporaryDirectory


class RealFs:
    def tmpdir(self):
        return TemporaryDirectory()
