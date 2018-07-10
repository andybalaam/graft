from graftlib.parse_cell import FunctionCallTree


def times(env, reps, fn):
    # TODO: when we have "for" this should be written
    #       in Cell, not Python.
    ret = None
    for i in range(int(reps.value)):
        ret = env.eval_expr(env, FunctionCallTree(fn, []))
    return ret


def if_(env, condition, then_fn, else_fn):
    if env.eval_expr(env, condition).value != 0:
        return env.eval_expr(env, FunctionCallTree(then_fn, []))
    else:
        return env.eval_expr(env, FunctionCallTree(else_fn, []))
