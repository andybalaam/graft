from graftlib.parse_cell import FunctionCallTree


def times(env, reps, fn):
    # TODO: when we have "for" this should be written
    #       in Cell, not Python.
    ret = []
    for i in range(int(reps.value)):
        val = env.eval_expr(env, FunctionCallTree(fn, []))
        ret.extend(val)
    return ret


def if_(env, condition, then_fn):
    if env.eval_expr(env, condition)[0].value != 0:
        return env.eval_expr(env, FunctionCallTree(then_fn, []))
    else:
        return []
