# The big collapse

The headline of the 2 → 3 transition, shown on one slide:

- **Significant indentation**: braces go, `if … then … else`.
- **`implicit` → `given`/`using`** (talk stage 4): the companion default is a `given`, and the `Eq` arrives through a
  `using` clause.
- **`sealed trait` + cases → `enum`** (stage 5).
- **`implicit class` → `extension`** (stage 6), at top level. `object Palindrome` disappears, because Scala 3 has
  top-level definitions. The wrapper class disappears too, because an extension method is also an ordinary method:
  `isPalindrome(xs)` and `xs.isPalindrome` are the same method.
- **`_ == _` lambdas** for `Eq`, and `import PalindromeResult.*` (the qualification workaround is gone with the object).
- **Tests**: `"racecar".isPalindrome` now works, because an extension's receiver may be converted
  (`String` → `Seq[Char]`). Scala 2 couldn't do this, since implicit views don't chain, so its tests needed
  `isPalindrome("racecar")` or `"racecar".toList.isPalindrome`. `Eq.caseInsensitive` is passed with
  `(using …)`, and a local `given` overrides the default.

3.1 to 3.5 are identical.
