# Sequence extractors and implicit value classes

- **`case x +: middle :+ y`** (talk stage 2): the index arithmetic becomes one pattern that peels off the first and
  the last element. It parses as `(x +: middle) :+ y`, because an operator's first character sets its precedence and
  `+` binds tighter than `:`. On a `List`, `:+` (`init`/`last`) is O(n), which makes the loop O(n²); an
  `IndexedSeq` such as `Vector` keeps it linear.
- **`implicit class … extends AnyVal`** (stage 6): the wrapper class plus conversion become one declaration, and as a
  value class it usually needs no allocation. In 2.10 a value class's field must be public, hence `val xs`.
