# The collections redesign again: `CanBuildFrom` gives way to `IsSeq` and `BuildFrom`

2.13 rewrote the collections a second time, and `palindromize` has to change with it (talk stage 5):

- **The 2.8 version stops working.** `StringOps` is no longer a collection, so a `String` only becomes a `SeqLike` by
  wrapping it in a `WrappedString`, and `Repr` is inferred as `WrappedString`. `val s: String = palindromize("abc")` then
  fails with "found: WrappedString, required: String". `SeqLike` itself survives only as a deprecated alias of
  `SeqOps`, and `CanBuildFrom` as an alias of `BuildFrom`.
- **`IsSeq[Repr]`** is the new way to accept "anything that can be read as a `Seq`", `String` and `Array` included:
  `isSeq(xs)` gives its `SeqOps`. **`BuildFrom[Repr, A, Repr]`** replaces `CanBuildFrom`. In the body,
  `isSeq(xs).toSeq` replaces `xs.toSeq`, and `bf.fromSpecific(xs)(seq.iterator ++ seq.take(start).reverseIterator)`
  builds the result in one call, straight from the two iterators, replacing the builder chain on `bf(xs.repr)`.
- **The `{ type A = A0 }` refinement** is the awkward part. The element type is a type member of `IsSeq`, and Scala
  2 can't write `BuildFrom[Repr, isSeq.A, Repr]` in the same parameter list as `isSeq`. So the element type gets an
  extra type parameter, `A0`, tied to it by a refinement. Scala 3 removes this (see 3.0).
- **The wrapper is rebuilt on `IsSeq` too**, following the pattern the 2.13 documentation gives for custom collection
  operations: an `implicit def` from any `Repr` that has an `IsSeq`, to `PalindromeOps[Repr, seq.type]`. The
  singleton type `seq.type` keeps `seq.A` known at the call site, so `xs.palindromize` returns `Repr`. Two things are
  lost: it's no longer a value class (it holds `xs` and `seq`), and delegating to the function needs
  `palindromize[Repr, seq.A](xs)(seq: seq.type, eq, bf)` to satisfy the refinement.
- **Method syntax works on a `String`.** The conversion starts from `String` itself rather than from a `Seq`, so
  there's no chain of views: `"racecar".isPalindrome` and `"abc".palindromize` both compile. The tests switch to
  them. Scala 2 could do this before: a wrapper for `String` alone works in any version, and 2.10's
  `IsTraversableLike` and 2.11's `IsSeqLike` support the same pattern as `IsSeq`. The code waits for 2.13 because
  those add a third mechanism without a new language feature (see `DESIGN.md`).
- **`import scala.language.implicitConversions`**: since 2.10, defining an `implicit def` conversion without this
  feature import draws a warning (implicit classes don't). That's part of why implicit classes became the idiom, and the 2.13
  pattern brings the conversion method back.

`CanBuildFrom` mostly disappeared from user code in 2.13. Ordinary operations now get their result type from the
collection's own type parameters (`SeqOps[A, CC, C]`), so a `List(...).map` needs no implicit. The machinery is
still needed where the source type isn't a collection class, as with `String` here.
