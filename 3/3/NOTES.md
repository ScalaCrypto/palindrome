# Fewer braces in the tests

- **Colon block arguments**: from 3.3, a method's last argument can be an indented block after a `:`, so
  `test("…") { … }` becomes `test("…"):` with the body indented below it. The suites are now brace-free, like the
  source. 3.0 has no such syntax, and 3.1 and 3.2 have it only behind `language.experimental.fewerBraces`.

The source is unchanged. 3.4 and 3.5 are identical.
