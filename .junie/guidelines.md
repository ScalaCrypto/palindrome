# Junie Project Guidelines & State

See `STATE.md` in the project root for the complete state, module matrix, and architecture of this repository.

## Key Facts Summary
- **19 Subprojects**: `2/5` to `2/13` and `3/0` to `3/9`.
- **Build Tool**: Mill 1.1.10 (`./mill`, `build.mill.yaml`, `mill-build/src/VersionModule.scala`).
- **Scala 2 vs 3**:
  - `2.5`-`2.7`: `object Palindrome` with method overloading.
  - `2.8`-`2.13`: `object Palindrome` with default arguments (`ignore = Nil`).
  - `3.0`-`3.9`: Significant indentation (optional braces), `extension (s: String)`, and `object Palindrome` wrapper.
- **Header comment**: `// Scala <version>` at the top of every `Palindrome.scala`.
- **Branching & PRs**: Feature branches `feature/<name>` targeting `main` with commit trailer `--trailer "Co-authored-by: Junie <junie@jetbrains.com>"`.
