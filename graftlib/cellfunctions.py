from graftlib.parse_cell import FunctionCallTree
from graftlib.eval_cell import ArrayValue
from graftlib.eval_cell import UserFunctionValue
from graftlib.nativefunctionvalue import NativeFunctionValue


def times(env, reps, fn):
    # TODO: when we have "for" this should be written
    #       in Cell, not Python.
    ret = None
    for i in range(int(reps.value)):
        ret = env.eval_expr(env, FunctionCallTree(fn, []))
    return ret


def until_endofloop(env, fn):
    while True:
        y = env.eval_expr(env, FunctionCallTree(fn, []))
        if y == env.get("endofloop"):
            break
        else:
            yield y


def for_(env, arr, fn):

    if type(arr) == ArrayValue:
        inp = arr.value
    elif type(arr) in (UserFunctionValue, NativeFunctionValue):
        inp = until_endofloop(env, arr)
    else:
        raise Exception(
            "Unexpected first argument to For: expected an array or a " +
            "function that eventually returns endofloop, but got: " +
            "%s." % arr
        )

    return ArrayValue(
        [
            env.eval_expr(env, FunctionCallTree(fn, [item]))
            for item in inp
        ]
    )


def if_(env, condition, then_fn, else_fn):
    if env.eval_expr(env, condition).value != 0:
        return env.eval_expr(env, FunctionCallTree(then_fn, []))
    else:
        return env.eval_expr(env, FunctionCallTree(else_fn, []))


def get(env, array, index):
    return array.value[int(index.value) % len(array.value)]


def add(env, array, item):
    array.value.append(item)
    return array
