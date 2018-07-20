cellstdlib="""
Range={:(max) i=-1 {i+=1 If(i<max,{i},{endofloop})}}
Not={:(val) If(val,{0},{1})}
While={:(cond_fn,body_fn)
    For(
        {If(cond_fn(),{1},{endofloop})},
        {:(i) body_fn()}
    )
}
"""
