# The collections redesign: `CanBuildFrom` keeps the collection type, `@tailrec` checks the loop

- **`CanBuildFrom`** (talk stage 5): 2.8 rebuilt the collections library so that operations return the type they
  were called on. Generic code gets the same power by taking the source collection as `SeqLike[A, Repr]` (`Repr` is
  its concrete type) and an implicit `CanBuildFrom[Repr, A, Repr]`, a factory for builders of `Repr`s.
  `bf(xs.repr)` gives a builder, and `palindromize` fills it. Now `palindromize("abc")` is the `String` `"abcba"`,
  and a `List` or `Vector` gives back a `List` or `Vector`. The `String` case works because 2.8's `StringOps` is
  itself a `SeqLike[Char, String]`.
- **The wrapper carries `Repr` too.** For `xs.palindromize` to return `Repr`, `PalindromeOps` now wraps a
  `SeqLike[A, Repr]` instead of a `Seq[A]`, and `isPalindrome` passes it on with `xs.toSeq`. Method syntax on a
  `String` still doesn't work (views don't chain), so strings use the function form: `palindromize("abc")`.
- **`@tailrec`** (stage 2): the compiler now rejects `loop` if it ever stops being tail-recursive. The generated code
  is unchanged: it was already a loop.
- **`x.toLower`**: the 2.8 library adds `toLower` to `Char`, replacing `Character.toLowerCase`.
- **Tests**: `Vector` arrives with the redesign, so the tests use `Seq(...)` and `Vector(...)`. Before 2.8 they use
  `List` throughout (2.5 and 2.6 have no `Seq(...)` factory either). The `palindromize` test now checks the static
  result types (`val s: String = palindromize("abc")`), and plain `==` works on the results.

2.9 is identical, and the `palindromize` code stays the same through 2.12.
