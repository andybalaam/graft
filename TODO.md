# Graft TODO

## Unnamed label
assert (
    do_eval("90=d.90+d:S", 2) ==
    [
        [Line(Pt(0, 0), Pt(0, -10.0))],
        [Line(Pt(0, -10), Pt(-10.0, -10.0))],
    ]
)

## Forking
assert (
    do_eval(":F~=_f;_f=d10d.+d:S", 1) ==
    [
        [Line(Pt(0, 0), Pt(0, 10.0)), Line(Pt(0, 0), Pr(10, 0))],
    ]
)

## Later

* Line and character numbers in lex/parse/eval errors
* Original code you typed in lex/parse/eval errors
* Command line control of max lines etc.
* Use Generic types in lots of places including Peekable
* Make GIF generate with interesting first image

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


### Passing arguments to functions
### Local variables
### Macros
