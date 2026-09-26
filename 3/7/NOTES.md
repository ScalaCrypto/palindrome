# Named pattern matching (tests only)

- **`case BreaksAt(index = i)`**: with named tuples stable in 3.7, patterns can bind case class fields by name. The
  implementation has no pattern that benefits, so only the tests use it. 3.6 rejects it.

3.8 and 3.9 are identical.
