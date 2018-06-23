from graftlib.parse_cell import FunctionCallTree

def times(env, reps, fn):
    # TODO: when we have "for" this should be written
    #       in Cell, not Python.
    ret = []
    ret.extend(env.eval_expr(env, FunctionCallTree(fn, [])))
    return ret
