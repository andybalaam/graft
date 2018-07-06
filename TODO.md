# Graft TODO

= Cell syntax
  + Import Cell lexer, parser, evaluator
  + Convert it to space-separated commands
  + Break out classes from eval_
  + Share Env between syntaxes
  + Break out code that will be re-used from eval_
  + Break out syntax-1-specific code from eval_
  + Create Graft execution environment
  + Switch between 2 syntaxes on command line
  + Default to new syntax
  + Update README
  + Update all examples

- Cell improvements
  + Add negative numbers (add back in to README, including the *= example)
  - Add <, == etc
  - Add If
  - Add lists
  - Add While, For
  - Add Map, Reduce?

- Run mypy and fix type errors
- Add type annotations

- Vector operations

## Later

* Warning when you throw away a value?
* Line and character numbers in lex/parse/eval errors
* Original code you typed in lex/parse/eval errors
* Make GIF generate with interesting first image
* Command line control of max lines etc.
* Use Generic types in lots of places including Peekable

## To define

### "Stamps" - different brush shapes
### If
### goto
### Passing arguments to functions
### Local variables
### Macros
