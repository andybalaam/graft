import re
import attr

from graftlib.peekablestream import PeekableStream


@attr.s
class AssignmentToken:
    pass


@attr.s
class EndFunctionDefToken:
    @staticmethod
    def code():
        return "}"


@attr.s
class EndParamListToken:
    @staticmethod
    def code():
        return ")"


@attr.s
class ListSeparatorToken:
    pass


@attr.s
class NumberToken:
    value: str = attr.ib()


@attr.s
class OperatorToken:
    value: str = attr.ib()


@attr.s
class ParamListPreludeToken:
    pass


@attr.s
class StartParamListToken:
    pass


@attr.s
class StartFunctionDefToken:
    pass


@attr.s
class StatementSeparatorToken:
    pass


@attr.s
class StringToken:
    value: str = attr.ib()


@attr.s
class SymbolToken:
    value: str = attr.ib()


def _scan(first_char, chars, allowed):
    ret = first_char
    p = chars.next
    while p is not None and re.match(allowed, p):
        ret += chars.move_next()
        p = chars.next
    return ret


def _scan_string(delim, chars):
    ret = ""
    while chars.next != delim:
        c = chars.move_next()
        if c is None:
            raise Exception("A string ran off the end of the program.")
        ret += c
    chars.move_next()
    return ret


def is_whitespace(c):
    if c is None:
        return False
    else:
        return c in " \n"


def lex(chars_iter):
    chars = PeekableStream(chars_iter)

    while True:
        if is_whitespace(chars.next):
            chars.move_next()
            yield StatementSeparatorToken()
            while is_whitespace(chars.next):
                chars.move_next()

        if chars.next is None:
            break

        c = chars.move_next()

        if c == "(":
            yield StartParamListToken()
        elif c == ")":
            yield EndParamListToken()
        elif c == "{":
            yield StartFunctionDefToken()
        elif c == "}":
            yield EndFunctionDefToken()
        elif c == ",":
            yield ListSeparatorToken()
        elif c == ":":
            yield ParamListPreludeToken()
        elif c == "=":
            yield AssignmentToken()

        elif c in "+-*/":
            yield OperatorToken(c)

        elif c in ("'", '"'):
            yield StringToken(_scan_string(c, chars))

        elif re.match("[.0-9]", c):
            yield NumberToken(_scan(c, chars, "[.0-9]"))

        elif re.match("[_a-zA-Z]", c):
            yield SymbolToken(_scan(c, chars, "[_a-zA-Z0-9]"))

        elif c == "\t":
            raise Exception("Tab characters are not allowed in Graft.")

        else:
            raise Exception("Unrecognised character: '" + c + "'.")
