from graftlib.parse_cell import FunctionCallTree
from graftlib.eval_cell import ArrayValue


def times(env, reps, fn):
    # TODO: when we have "for" this should be written
    #       in Cell, not Python.
    ret = None
    for i in range(int(reps.value)):
        ret = env.eval_expr(env, FunctionCallTree(fn, []))
    return ret


def for_(env, arr, fn):
    return ArrayValue(
        [
            env.eval_expr(env, FunctionCallTree(fn, [arr.value[i]]))
            for i in range(len(arr.value))
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
