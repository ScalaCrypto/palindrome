# The whole design with 2007 machinery

Every idea of the talk is already expressible in 2.5. What's missing is only the convenient syntax:

- **Generic over `Seq[A]`** (talk stage 1). A `String` is accepted through Predef's `String` → `Seq[Char]` conversion.
- **Equality as a type class** (stage 3): `Eq[A]` taken as an `implicit` parameter. The default, `universal`, sits in
  `Eq`'s companion and is found through the implicit scope. Instances are anonymous classes, because lambdas can't
  implement a trait yet.
- **An answer that says where it breaks** (stage 5): a `sealed trait` with a `case object` and a `case class`.
- **Method syntax** (stage 6): an `implicit def` converts any `Seq` to a `PalindromeOps` wrapper.
- **An index-based loop.** There are no `+:`/`:+` extractors yet. The loop is tail-recursive, so scalac already
  compiles it to a jump, but nothing checks that.

Things that look odd today, and why:
- **`PalindromeResult.Palindrome` is qualified**: importing it would clash with `object Palindrome`.
- **The wrapper calls `Palindrome.checkPalindrome(xs)`**: unqualified, the call would resolve to its own method.
- **`Character.toLowerCase`**: `Char` has no `toLower` before 2.8.
- **Elements are compared pairwise, never `xs == xs.reverse`**: before 2.8, `==` on collections isn't content-based,
  so `"racecar".reverse == "racecar"` is `false`. That's also why the talk's stage 0 one-liner has no version here.

2.6 and 2.7 are identical.
