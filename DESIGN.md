# Design Log

Newest entries first. Each entry records what changed, why, the alternatives rejected, the limitations accepted, and
how it was verified. Current project facts live in `STATE.md`.

---

## 2026-09-26 — `EVOLUTION.md`: generated per-version diffs as the basis for the slides

### What changed

`EVOLUTION.md` records how the code changes from each Scala version to the next: an overview table, the baseline
source, one section per version that changes something (notes, then a diff of the source and of the tests), and the
final source. `tools/evolution.py` generates it from the version directories. In Claude Code, a checked-in
`PostToolUse` hook (`.claude/settings.json`) runs the generator after every Write/Edit to a version's source, test
suite or `NOTES.md`. If the generator fails, the hook exits with code 2, so a missing or stray note is reported back
to Claude instead of being swallowed. The prose comes from a `NOTES.md` in
each version directory that changes something. `tools/evolution.py --check` runs in CI
(`.github/workflows/evolution.yml`) and fails when the document is stale.

### Why

The document must stay in step with the code, and it will be edited for months while the slides take shape.
Generating everything that can be derived (versions, which ones changed, the diffs, the code) makes those parts
correct by construction. The only hand-written part is the notes, and they are kept as close to the code as possible:
in the directory of the version they describe, required exactly where the code changes, and rejected where it
doesn't.

### Alternatives rejected

- **A hand-written document.** Code blocks copied into markdown drift silently. The previous `STATE.md` §4 already
  held per-version code and would have become a second copy; it now points to `EVOLUTION.md`, and the "New here"
  matrix column went for the same reason.
- **All notes in one file, or in the generator.** Nothing would prompt anyone to update a note when a version's code
  changes. With `NOTES.md` next to `Palindrome.scala`, the note is in the same directory as the change, and the
  missing/stray check catches added or removed changes.
- **Diffing with `git diff` or `diff`.** Their output differs between versions and platforms, which would make
  `--check` flaky. Python's `difflib` produces the same output everywhere.
- **Always showing a diff.** The 2.13 → 3.0 change rewrites almost every line, and its diff is unreadable. Below 50%
  line similarity the generator shows both versions in full instead, which is also what a slide needs.
- **Only a pre-commit hook.** Git doesn't version hooks, so each clone (and each assistant's environment) would
  have to install it. CI checks every push and PR without any setup. Regenerating is one command, listed in
  `STATE.md`. The Claude Code hook is a convenience on top of CI, not the guarantee: it doesn't run for Junie,
  for manual edits, or for files changed through Bash (e.g. a `git mv` or `rm` of a `NOTES.md`).
- **A hook that ignores generator failures** (`|| true`). A failure means a `NOTES.md` is missing or stray. Hiding
  that would leave `EVOLUTION.md` stale until CI catches it, and exit code 2 costs nothing.

### Limitations accepted

- The check proves a note *exists* where the code changed, not that it describes the change correctly. The
  `STATE.md` convention asks whoever changes the code to reread the note.
- The CI job needs only Python, not Scala. It checks that the document matches the code, not that the code
  compiles; that remains `./mill __.test` and `legacy/test.sh`.

### Verification

`tools/evolution.py --check` passes on the current tree. On a scratch copy it fails in each of these cases:
a code change without a note ("`3/9/NOTES.md` is missing"), a note for an unchanged version ("stray"), an edited
note without regenerating ("out of date"), and a malformed version header. The hook command was pipe-tested with a matching file
(regenerates), a non-matching file (does nothing) and a missing note (exit 2 with the generator's message). It was
then triggered live: an Edit to `3/7/NOTES.md` appeared in `EVOLUTION.md` without running the script by hand.

---

## 2026-09-26 — One design across all versions, following the ScalaDays 2026 talk

### What changed

The 19 versions no longer implement `isPalindrome(s: String, ignore: Set[Char])`. They now implement the design the
talk spec (`scaladays-2026-talk.md` §3) arrives at:

- generic over `Seq[A]` instead of `String`;
- element equality as an `Eq[A]` type class, with a universal default in the companion and an opt-in
  `Eq.caseInsensitive`;
- a `PalindromeResult` ADT (`Palindrome` | `BreaksAt(index)`) from `checkPalindrome`, with `isPalindrome` as its
  Boolean view;
- method syntax on any `Seq`.

Every version writes this design with the best features of its own release, so the diff between neighbouring versions
shows what the language gained: `@tailrec` (2.8), `+:`/`:+` extractors and implicit value classes (2.10), `private val`
in value classes (2.11), SAM lambdas (2.12), `given`/`using`/`enum`/`extension`/indentation (3.0), the new given
syntax and `[A: Eq as eq]` (3.6), and named patterns in the tests (3.7). `STATE.md` §2 and §4 have the full mapping.

### Why

Of the two documents, `scaladays-2026-talk.md` is the finalized one. It keeps `isPalindrome` as the running example
and grows the problem until it needs a type class, an ADT and an extension method. That answers the objection in
`scala-history-talk-problem-selection.md`: the old example had no ADT, no contextual abstraction and no richer
answer. The repo is the talk's sample code, so it follows the talk.

The versions are "same design, best features per release", not "one talk stage per version", because the repo's
point is comparison. Two neighbouring versions should differ only in what their language changed. Mapping stages to
versions would mix design changes with language changes and put features in versions that don't introduce them
(`implicit` parameters exist from 2.5, yet the talk introduces them after `@tailrec`).

### Alternatives rejected

- **The arithmetic-expression evaluator** (recommended in `scala-history-talk-problem-selection.md`). It was
  superseded by the talk spec, which gets the ADT, type-class and extension beats from `isPalindrome` without
  swapping the example.
- **One talk stage per version** (e.g. 2.5 = the one-liner, 2.8 = `@tailrec`, …). Rejected for the reason above.
  Stage 0 (`s == s.reverse`) also can't be written for 2.5–2.7, where collection `==` isn't content-based.
- **Keeping the `ignore: Set[Char]` parameter.** The talk's customization hook is `Eq`. `ignore` would add a second
  hook and bring back the default argument the talk doesn't use. Sentence palindromes ("race car") are the job of the
  talk's reserve "normalized input" stage (opaque types), which isn't in the code.
- **Keeping the `null` check.** Generic `Seq[A]` code in idiomatic Scala doesn't test for `null`, and the talk
  doesn't either.
- **A case-insensitive `Eq[Char]` as the default**, as the talk's Stage 3/4 slides show (`implicit val charCI` /
  `given Eq[Char]`). As the only instance it can't handle `Seq("a", "b", "a")`, whose elements need an `Eq[String]`.
  As a default next to a universal instance, it needs prioritization (a `LowPriority` trait in Scala 2, and
  resolution rules that changed during 3.x), and case-sensitive checks become opt-out. An explicit
  `Eq.caseInsensitive` keeps the default unsurprising. It also shows both ways to supply an instance: passed
  explicitly, or put in lexical scope, which beats the companion. The slides can still show the talk's shorter form.
- **Keeping a separate top-level `def isPalindrome` with `@targetName` in Scala 3** (the previous design). An extension
  method is an ordinary method, so `isPalindrome(xs)` already works on the extension. The second definition and the
  JVM-name clash it caused go away.
- **A `String` overload of `PalindromeOps` for Scala 2**, so that `"racecar".isPalindrome` compiles there too. It would
  double the enrichment code in every Scala 2 version to hide a real 2→3 difference: Scala 3 extension receivers may
  be converted, and Scala 2 implicit views don't chain. The Scala 2 tests use `isPalindrome("racecar")` and
  `"racecar".toList.isPalindrome` instead.
- **Structural recursion before 2.10** (e.g. `head`/`last`/`slice`). Without `+:`/`:+`, index arithmetic is the
  idiomatic pre-2.10 form, and the switch to extractors then shows up in the 2.10 diff.
- **`boundary`/`break` in 3.3, and named tuples in the implementation from 3.7.** Neither is natural for a tail-recursive
  check. `boundary`/`break` suited the evaluator's non-tail-recursive `eval`, not this. Named patterns appear in the
  3.7+ tests, where matching on a result is natural.
- **Adding the talk's reserve material (opaque types, `@main`, `inline`, `CanEqual`).** The talk leaves its scope open
  (§6). All of it arrives in 3.0 and would turn that single diff into a grab bag. It can be added later if the talk
  keeps it.

### Limitations accepted

- Several versions are identical apart from the header: 2.5–2.7, 2.8–2.9, 2.12–2.13, 3.0–3.5 and 3.6–3.9 (3.7–3.9
  differ from 3.6 only in the tests). Those releases changed nothing this example uses, and inventing a difference
  would break the "only real changes" rule.
- From 2.10, the extractor recursion is O(n²) on a `List`, because `:+` needs `init`/`last`. It's linear on an
  `IndexedSeq`. The talk states this as its Stage 2 caveat.
- `Eq.universal` allocates an instance per call before 3.0. That's irrelevant at this size, and a cached
  `Eq[Any]` cast would obscure the example.

### Verification

- Before writing the repo files, each variant was compiled and run in isolation on its compiler, to confirm the
  version boundaries: 2.10 rejects `private val` in a value class, 2.11 rejects SAM lambdas, 2.5–2.7 lack
  `Char.toLower`, 2.5–2.6 lack `Seq(...)`, 3.5 rejects `[A: Eq as eq]` and the new given syntax, and 3.6 rejects
  `BreaksAt(index = i)`. Scala 2.13 rejects `"racecar".isPalindrome`, while 3.0 and 3.9 accept it.
- `javap` on the 2.5.1 output shows `loop` compiled to a backward `goto`, confirming the "already a loop before
  `@tailrec`" comment.
- `./mill __.test`: 2.10–2.13 and 3.0–3.9 pass (9 tests each, 10 in 3.7–3.9). `legacy/test.sh`: 2.5–2.9 pass (9 tests
  each).
