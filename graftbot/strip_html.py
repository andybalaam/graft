from html.parser import HTMLParser


# Credit: https://stackoverflow.com/a/925630/22610
class MLStripper(HTMLParser):  # pylint: disable=abstract-method
    def __init__(self):
        HTMLParser.__init__(self)
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, data):
        self.fed.append(data)

    def get_data(self):
        return ''.join(self.fed)


def strip_html(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
