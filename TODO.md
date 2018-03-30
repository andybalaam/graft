# Graft TODO

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

### Passing arguments to functions
### Local variables
### Macros
