# The big collapse

The headline of the 2 → 3 transition, shown on one slide:

- **Significant indentation**: braces go; `xs match` takes its cases by indentation.
- **`implicit` → `given`/`using`** (talk stage 4): the companion default is a `given`. `isPalindrome` takes its `Eq`
  through a context bound, `[A: Eq]`, and `palindromize` through a `using` clause.
- **`x === y`**: `Eq` gains an extension method, `===`, inside the trait. An extension defined in a given is
  available wherever that given is in scope, and the context bound's evidence is, so `isPalindrome` compares
  `x === y` with no wrapper class and no name for the `Eq`. Scala 2 would have needed a second implicit class
  for that syntax. The trait still declares `eqv`, the single abstract method, so the `_ == _` lambdas still work.
- **`implicit class` → `extension`** (stage 6), at top level. `object Palindrome` disappears, because Scala 3 has
  top-level definitions. The wrapper class disappears too, because an extension method is also an ordinary method:
  `isPalindrome(xs)` and `xs.isPalindrome` are the same method, so the recursion reads `middle.isPalindrome`.
- **`_ == _` lambdas** for `Eq`.
- **`palindromize` loses its refinement** (stage 5). Scala 3 uses the 2.13 collections, so it's still `IsSeq` plus
  `BuildFrom`. But the extension's `using isSeq: IsSeq[Repr]` clause comes before the method's own `using` clause, so
  `BuildFrom[Repr, isSeq.A, Repr]` can depend on `isSeq` directly. 2.13's `{ type A = A0 }` workaround and extra type
  parameter disappear, and so do its wrapper class, its `seq.type` trick and its `implicitConversions` import: one
  extension provides both `"abc".palindromize` and `palindromize("abc")`.
- **Tests**: `"racecar".isPalindrome` works on the plain `Seq[A]` extension, because an extension's receiver may be
  converted (`String` → `Seq[Char]`). Scala 2 needed 2.13's `IsSeq` wrapper for that; its implicit views don't
  chain. `Eq.caseInsensitive` is passed with `(using …)`, and a local `given` overrides the default.

3.1 and 3.2 are identical.
