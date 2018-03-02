# Graft TODO

### Repeat command
```
assert do_eval("{:S},2:L") == [...]
```

### Co-ordinate built-ins, :D to write a Dot, :J to jump, :L for a line to x,y
```
assert do_eval("20=x15=y:D") == [Dot(Pt(20, 15))]
# :L to draw a line to x, y
assert do_eval("20=x15=y:L") == [Line(Pt(0, 0), Pt(20, 15))]
```

### Variables
```
assert do_eval("180=_a_a+d:S") == [Line(Pt(0, 0), Pt(0, -10))]
```

## Later

* Line and character numbers in lex/parse/eval errors
* Original code you typed in lex/parse/eval errors
* Command line control of number of frames, max lines etc.
* Use Generic types in lots of places including Peekable

## To define

```
### "Stamps" - different brush shapes

### If
assert do_eval("1+_a_a<10~:I+d-d:S") == ?

### Labels and goto
assert (
    do_eval("90=d.90+d:S", 2) ==
    [
        Line(Pt(0, 0), Pt(0, -10)),      # d == 180 (90+90)
        Line(Pt(0, -10), Pt(-10, -10)),  # d == 270 (90+90+90)
    ]
)
assert (
    do_eval("90=d.90+d:S", 2) ==
    [
        Line(Pt(0, 0), Pt(0, -10)),      # d == 180 (90+90)
        Line(Pt(0, -10), Pt(-10, -10)),  # d == 270 (90+90+90)
    ]
)

### Forking
assert (
    do_eval(:F^=_f._f==0~:I90+d90-d:S) ==
    [
        [Line(Pt(0, 0), Pt(10, 0)), Line(Pt(0, 0), Pr(-10, 0))],
    ]
)

### Defining your own macros/functions
