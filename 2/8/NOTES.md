# `@tailrec` makes the loop's promise checkable

- **`@tailrec`** (talk stage 2): the compiler now rejects `loop` if it ever stops being tail-recursive. The generated
  code is unchanged: it was already a loop.
- **`x.toLower`**: the 2.8 library adds `toLower` to `Char`, replacing `Character.toLowerCase`.
- **Tests**: `Vector` arrives with the 2.8 collections redesign, so the tests use `Seq(...)` and `Vector(...)`. Before
  2.8 they use `List` throughout (2.5 and 2.6 have no `Seq(...)` factory either).

2.9 is identical.
