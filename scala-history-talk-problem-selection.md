# Scala Days 2026 — History Talk: Choosing the Running Example

Reference notes for the "history of Scala" talk. The talk shows **one small program**
implemented idiomatically for each major Scala version (2.0 → 3.8), so the audience can
watch the *same* code improve as language features arrive (and occasionally leave).

## Requirements the example must satisfy

- Solvable idiomatically in every major version from 2.0 to 3.8.
- Exercises as many major features as possible (added *and* later removed).
- As short and elegant as possible while staying easily understood live.
- Emphasis on the parts that **change** version to version, and how each new feature
  improves the code.

## Selection principle

"Maximum features" and "shortest/clearest" pull against each other. Resolve the tension by
optimizing **feature density per line**: pick a problem whose tiny, natural solution already
*wants* an ADT, a typeclass, pattern matching, recursion, and a failure path — so each
version improves the same code instead of bolting on new concerns.

## Assessment: `isPalindrome` (current example)

Strong for exactly one beat: recursion, `@tailrec`, the `+:` / `:+` decomposition, and the
`implicit class` → `extension` evolution.

Limitation: it has no ADT, no contextual abstraction, and no error path. So it cannot
naturally showcase the three changes that are arguably *the* headline story of the
2.0 → 3.8 arc:

- `sealed trait` + case classes → `enum`
- `implicit` → `given` / `using`
- `Option` / `Either` + `for`-comprehensions

These are the "before and after" moments the audience will most want to see.

## Recommendation: a mini arithmetic-expression evaluator

An `Expr` tree plus an `eval` (e.g. evaluate `1 + 2 * 3`). Universally understood, roughly
the same line count as the palindrome once written, and the canonical vehicle for **both**
an ADT and a typeclass — so it carries the highest overall feature coverage.

### Feature → version mapping

- **2.x foundations** — `sealed abstract class Expr` with case classes (ADT); `match` in
  `eval`; recursion; `for`-comprehension over `Option` / `Either` for the division-by-zero
  path.
- **2.8** — `@tailrec` (in a tokenizer or a `foldLeft` over a flat operand list); the 2.8
  collections redesign.
- **2.10** — string interpolation in a `show` pretty-printer; `implicit class ExprOps` for
  `expr.eval`; a value class (`extends AnyVal`) for a typed operator/result; `Try`.
- **2.13** — literal types; the second collections redesign; a `Numeric`-style typeclass.
- **3.0** — the big collapse: `enum Expr`; `implicit class` → `extension`; an evaluation
  environment passed via `given` / `using`; optional braces / significant indentation;
  top-level `@main`; dropping `new`; a union return type (`Int | Double`).
- **3.3** — `boundary` / `break` standing in for the removed non-local returns.
- **3.7** — named tuples and named pattern matching (`case Add(left = l) => …`), both now
  stable, for the result/environment shapes.

### The `@tailrec` caveat

Evaluating a binary tree is not tail-recursive, so `@tailrec` does not sit on `eval` the way
it does on the palindrome. Three clean resolutions:

1. Put `@tailrec` on a tokenizer / `foldLeft` step (natural and idiomatic).
2. Keep the palindrome as a separate 30-second micro-example purely for the recursion beat.
3. **(Preferred)** Make the non-tail-recursive `eval` the motivating contrast for the
   3.3 `boundary` / `break` slide.

## Runner-up: a mini-JSON / `Show` renderer

Even better for the typeclass story — it naturally reaches `given` / `using`, `extension`,
and Scala 3's `derives` for automatic typeclass derivation. But it is weaker on `@tailrec`
and on a meaningful error path, so the evaluator wins on overall coverage.

## Decision

`isPalindrome` stays the running example. The finalized talk spec
(`scaladays-2026-talk.md`) doesn't swap the example to fix the limitation above. It grows
the problem instead, so each headline change is still needed:

- ADT: `PalindromeResult` (`Palindrome` | `BreaksAt(index)`), sealed trait → `enum`
- contextual abstraction: equality as an `Eq` type class, `implicit` → `given` / `using`
- the richer answer: `BreaksAt` reports where a non-palindrome breaks, in place of an
  error path

The evaluator and its version-by-version draft are therefore not pursued. The repo
implements the palindrome design for every version from 2.5 to 3.9 (see `STATE.md` and
`DESIGN.md`).
