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
- **Making a palindrome** (stage 5b): `palindromize(xs)`, or `xs.palindromize` through the wrapper, returns the
  shortest palindrome that starts with `xs`. It finds the longest suffix that's already a palindrome, using our own
  `isPalindrome`, and appends the reverse of what comes before it: `"abcb"` gives `"abcba"`, and `"racecar"` stays as
  it is. Because it calls `isPalindrome`, it takes an `Eq` too; with `Eq.caseInsensitive`, `"abA"` needs nothing
  added. The suffix search (`palindromicSuffixStart`) is the same in every version, so the diffs below only show
  how the result gets built.
- **Generic code can't build "the same kind of collection"**, so `palindromize` promises only a `Seq`.
  `palindromize("abcb")` is a `Seq[Char]`, not a `String`, and in 2.5 even
  `palindromize(List(1, 2, 3)) == List(1, 2, 3, 2, 1)` is `false`. The tests compare with `.toList` and `.mkString`.

Things that look odd today, and why:
- **`PalindromeResult.Palindrome` is qualified**: importing it would clash with `object Palindrome`.
- **The wrapper calls `Palindrome.checkPalindrome(xs)`**: unqualified, the call would resolve to its own method.
- **`Character.toLowerCase`**: `Char` has no `toLower` before 2.8.
- **Elements are compared pairwise, never `xs == xs.reverse`**: before 2.8, `==` on collections isn't content-based,
  so `"racecar".reverse == "racecar"` is `false`. That's also why the talk's stage 0 one-liner has no version here.

2.6 and 2.7 are identical.
