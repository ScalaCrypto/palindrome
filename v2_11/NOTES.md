# The value class may hide its field

- **`private val xs`**: 2.11 allows a private field in a value class, so the wrapped `Seq` no longer leaks as a public
  member of every `Seq`.
- **Tests**: 2.10 uses ScalaTest 3.0.9; from 2.11 the tests use ScalaTest 3.2, where `FunSuite` is
  `org.scalatest.funsuite.AnyFunSuite`. This is a library change, not a language one.
