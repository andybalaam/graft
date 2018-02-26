from tempfile import TemporaryDirectory


class RealFs:
    def tmpdir(self):
        return TemporaryDirectory()

    def read_file_or_none(self, file_name):
        try:
            with open(file_name) as f:
                return f.read()
        except FileNotFoundError:
            return None

    def write_file(self, file_name, file_contents):
        with open(file_name, "w") as f:
            f.write(file_contents)
