# Design Log

Newest entries first. Each entry records what changed, why, the alternatives rejected, the limitations accepted, and
how it was verified. Current project facts live in `STATE.md`.

---

## 2026-09-26 — No result ADT: only `isPalindrome` and `palindromize`

### What changed

Every version drops `PalindromeResult` (`Palindrome` | `BreaksAt(index)`), `checkPalindrome` and the private helper
`palindromicSuffixStart`. `isPalindrome` returns its `Boolean` directly. In 2.5–2.9 an inner `loop` walks an index
inward with `from >= to || (eq.eqv(xs(from), xs(to)) && loop(from + 1))`. From 2.10, `isPalindrome` recurses on
itself through `case x +: middle :+ y => eq.eqv(x, y) && isPalindrome(middle)`, with `@tailrec` on the method. In
Scala 3, that's `middle.isPalindrome` inside the extension. `palindromize` inlines the suffix search as its first line:
`val start = (0 to xs.length).find(i => isPalindrome(xs.drop(i))).get` (on `xs.toSeq` from 2.8, on `ops.toSeq` from
2.13).

The tests lose the `checkPalindrome` assertions and 3.7's named-pattern test. "isPalindrome finds a mismatch inside
matching ends" keeps what the `BreaksAt(2)` cases checked: `"abcxba"` and `1, 2, 3, 4, 2, 1` aren't palindromes.
3.7 no longer differs from 3.6, so its `NOTES.md` is gone and eight versions change the code. The talk's stage 5 (the
ADT) is removed and 5b becomes stage 5. Both decks follow: the talk deck loses the 3.7 slide and the ADT from the 2.5
and 3.0 slides. The morph deck is regenerated, and `talk/morph.py` finds the code by `@tailrec` or `def isPalindrome`.
This branch's decks are published to new artifacts (<https://claude.ai/artifact/4nvk9BRuCLeutLsoEpQt3d> and
<https://claude.ai/artifact/RYU4d3bpEjxvV7MX1sfTKb>), so the artifacts of the branch it's stacked on still match that
branch's code.

### Why

The ADT carried one beat (`sealed trait` → `enum`) and cost every version three definitions. `checkPalindrome`
needed a loop with an extra `from` parameter just to report the index, and `isPalindrome` became a comparison against
`Palindrome`. Without the ADT, the recursion in 2.10+ and Scala 3 is exactly the talk spec's stages 2–4, with no inner
helper. On the slides, the code that changes between versions is now the part the talk is about.

### Alternatives rejected

- **Keep `BreaksAt` and drop only `checkPalindrome`'s wrapper methods.** It still needs the `from`-carrying loop and
  the ADT definitions, which is most of the cost.
- **Move 3.7's named-pattern test onto something else.** Nothing left in the code has a case class with a named
  field to match. A test invented for the syntax would add a difference the problem doesn't ask for.
- **Keep `palindromicSuffixStart` as a named helper.** It's one expression, used once. Inlined as `val start = …`, it
  reads in place, and the 2.8 → 2.13 → 3.0 diffs of `palindromize` still show only how the result gets built.
- **Rewrite the submitted talk description.** It still promises "contrasting sealed-trait ADTs with Scala 3 enums".
  That's recorded as an open item in the talk spec instead: say it in one line on the 3.0 slide, or edit the
  description if that's still possible.
- **Publish the simplified decks over the existing artifacts.** The branch this one is stacked on would then have
  artifacts that don't match its code. New artifacts keep each branch self-consistent. Merging this branch means
  switching to the new links, which its `talk/README.md` already does.

### Limitations accepted

- `isPalindrome` no longer says where a non-palindrome breaks.
- Scala 2's `from >= to || (… && loop(from + 1))` is denser than the `if`/`else if`/`else` it replaces. It's kept
  because it mirrors the `eq.eqv(x, y) && isPalindrome(middle)` that follows in 2.10.
- The morph deck keeps its one-row header and 80px margins. The code is now 16 lines at most, and it would fit under
  the talk deck's larger headings too, but the header was left as it is.

### Verification

`./mill __.test`: 14 versions, 11 tests each, all pass. That includes `@tailrec` on the self-recursive `isPalindrome`
in 2.10–2.13 and on the Scala 3 extension method. `legacy/test.sh`: 2.5–2.9 pass, including 2.8's `@tailrec` through
`||` and `&&`. `tools/evolution.py --check` passes. `talk/render.py`: all 21 slides pass (s28-cbf is the tightest, at
941 of 952px). `talk/morph.py`: 25px code, 69–90 runs per slide. Every id shared by neighbouring slides has the same
text (64–75 per transition), and the rightmost run ends at x=1782.

---

## 2026-09-26 — `talk/morph.py`: a deck where the code changes in place

### What changed

`talk/morph.py` generates a second deck, `talk/morph/project/` (the claude.ai Slides format, artifact
<https://claude.ai/artifact/RYU4d3bpEjxvV7MX1sfTKb>). It shows `isPalindrome` and `palindromize`, without comments, on one slide per distinct state of that code. That's six slides: 2.5–2.7,
2.8–2.9, 2.10–2.12, 2.13, 3.0–3.5 and 3.6–3.9. Each slide leaves with the format's magic-move transition, so tokens
that survive into the next version glide to their new place, and the rest fade out or in.

Every run of code is a pinned `<p>` placed from its line and column (IBM Plex Mono advances 0.6 em per character).
A token that survives keeps its `id` from slide to slide. Tokens are matched per pair of versions: unchanged lines
first (compared without indentation), then a token diff within the changed regions, then identifiers that moved out of
order where there's exactly one candidate on each side.

### Why

A diff shows what changed; a morph shows where each part went (`(using eq: Eq[A])` moving up into the `extension`,
`implicit` turning into `using`), and that's the talk's story. The Slides format's magic move animates in the presenter's
own tempo, one click per version, and needs no script.

### Alternatives rejected

- **One element per token.** A slide has at most 200 elements and the code is about 250 tokens. Neighbouring tokens
  are merged into runs. A run has to be the same run on both of its slide's transitions, or the ids stop matching, so
  the cut points between runs are propagated along the whole chain of slides until they're stable (79–109 runs per
  slide).
- **A live `<x-embed>` that animates with JavaScript.** It would run on its own clock, not on the presenter's click.
  It's limited to 16 KB, and PPTX/PDF export flattens it.
- **A global token diff without the line pass.** Common tokens like `(` and `:` then match across unrelated lines and
  fly around for no reason.
- **Keeping the talk deck's two-line headings.** 2.13's code is 25 lines. At the 24px floor the code only fits with a
  one-row header (version and year, and the version's `NOTES.md` summary). The slides use 80px top and bottom
  margins instead of 128px.

### Limitations accepted

- The magic move's timing and easing are the artifact's. Nothing in the repo can play the animation. `morph.py` only
  checks that matched runs have the same text.
- A token that moves out of order and isn't a unique identifier (`eq` appearing twice, say) fades instead of moving.
- The deck is generated, so hand edits in the artifact are overwritten on the next run.

### Verification

`talk/morph.py` reports the font size (24px) and the runs per slide. A check over the generated slides confirmed that
every id shared by two neighbouring slides holds the same text: 75–98 shared runs per transition. Geometry by
arithmetic: the longest line (111 characters) ends at x≈1726 and the lowest line at y≈968.

---

## 2026-09-26 — `talk/`: the slide deck and a layout check in the repo

### What changed

`talk/deck/project/` holds the deck for the talk: `deck.json` plus one HTML file per slide, in the format of the
claude.ai Slides artifact it's presented from (22 slides, drafted from `EVOLUTION.md` and the talk spec).
`talk/render.py` renders every slide in headless Chrome on the 1920×1080 canvas, with the deck's fonts. It exits 1 if
anything crosses the margins or overflows its container, and `--screenshots` writes one PNG per slide plus contact
sheets. `talk/README.md` explains how the files and the artifact are kept in step.

### Why

The deck only existed as an artifact, and its source files and the render check only in a session's temporary
directory. The repo is where the talk's code lives, so the deck's source belongs next to it, under version control.
The render check found the deck's one real problem so far (see below), so it's worth being able to run again.

### Alternatives rejected

- **Committing the generator that produced the 19 versions' sources.** It was a one-off template script. The sources
  are what's compiled and tested; keeping the generator would be a second copy of all the code to keep in sync, and
  `EVOLUTION.md` already records how the versions differ.
- **Moving the talk spec and problem-selection docs into `talk/`.** Several documents and `tools/evolution.py` point
  at them where they are; moving them is churn without a benefit.
- **Committing the downloaded fonts or the screenshots.** Both are reproducible, and the screenshots change with
  every edit. They go to the git-ignored `out/talk-render/`.
- **One tall screenshot of all slides, cropped per slide** (the first approach). Chrome corrupted the bottom of very
  tall screenshots, and macOS `sips` ignores a crop offset of 0. One page per slide avoids both.
- **Google Fonts loaded over the network during rendering.** With virtual time, headless Chrome hung. The fonts are
  downloaded once and served from local files.
- **Waiting for Chrome to exit.** On macOS, headless Chrome writes its output and then keeps running, so every call
  took a minute until a time limit killed it. The script polls for the DOM dump or the finished PNG and stops Chrome
  then: 20 seconds for the full check with screenshots, instead of about 45 minutes.
- **JetBrains Mono for code** (the deck's first code font). Its programming ligatures showed `==` as `═`, `>=` as `≥`
  and `=>` as `⇒`, which misleads when the syntax is the subject, and the slide format can't switch ligatures off.
  The deck uses IBM Plex Mono, which has none and matches IBM Plex Sans.

### Limitations accepted

- The artifact and `talk/deck/` can drift; syncing is a manual step, described in `talk/README.md` and `STATE.md`.
- The slides' code isn't checked against the sources.
- `render.py` approximates the artifact's renderer: it applies the format's defaults, but doesn't run the artifact's
  own page code.
- `render.py` needs Chrome and network access for the first font download, so it isn't part of CI.

### Verification

- `talk/deck/project/` was read back from the published artifact, not copied from local drafts.
- `talk/render.py --screenshots` passes on all 22 slides in about 20 seconds. The only report is the takeaways
  heading, which is meant to take two lines. The contact sheets were inspected.
- With a code line made too long on one slide, the script failed, naming the slide and the overflow (154px), and
  passed again once the slide was restored.

---

## 2026-09-26 — `palindromize`: showing the 2.8 and 2.13 collections redesigns

### What changed

Every version gains `palindromize`, which builds the shortest palindrome that starts with `xs` (`"abcb"` →
`"abcba"`, `"abb"` → `"abba"`, `"racecar"` unchanged). A private helper, `palindromicSuffixStart`, is identical in
every version apart from syntax. It finds the longest suffix that's already a palindrome, using `isPalindrome` and
therefore an `Eq`, and only the elements before it are mirrored (`reverseIterator.drop(length - start)`). From 2.8
the result has the input's own collection type. It's available as a function and as a method (`xs.palindromize`)
in every version. The talk spec gains a matching
Stage 5b. The function's signature shows the collections story:

- **2.5–2.7**: `palindromize[A](xs: Seq[A])(implicit eq: Eq[A]): Seq[A]`. The type is lost: `"abcb"` gives a
  `Seq[Char]`.
- **2.8–2.12**: `palindromize[A, Repr](xs: SeqLike[A, Repr])(implicit eq: Eq[A], bf: CanBuildFrom[Repr, A, Repr]):
  Repr`, filling the builder `bf(xs.repr)`.
- **2.13**: `palindromize[Repr, A0](xs: Repr)(implicit seq: IsSeq[Repr] { type A = A0 }, eq: Eq[A0],
  bf: BuildFrom[Repr, A0, Repr])`. 2.13 now differs from 2.12.
- **3.0**: an `extension [Repr](xs: Repr)(using seq: IsSeq[Repr])` whose `palindromize` takes
  `(using eq: Eq[seq.A], bf: BuildFrom[Repr, seq.A, Repr])`. From 3.6 it's written `[Repr: IsSeq as seq]`.

For method syntax, the Scala 2 `PalindromeOps` wrapper carries the collection type, and its shape follows each
redesign:

- **2.5–2.7**: `PalindromeOps[A](xs: Seq[A])`.
- **2.8–2.12**: `PalindromeOps[A, Repr](xs: SeqLike[A, Repr])`, an implicit value class from 2.10. The Boolean
  methods pass `xs.toSeq` on.
- **2.13**: the pattern the 2.13 docs give for custom collection operations. An `implicit def palindromeOps[Repr](xs:
  Repr)(implicit seq: IsSeq[Repr])` returns a `PalindromeOps[Repr, seq.type]` (not a value class), and it needs
  `import scala.language.implicitConversions`. Because the conversion starts from `String` itself, `"racecar"
  .isPalindrome` and `"abc".palindromize` work in Scala 2 for the first time, and the 2.13 tests use them.

### Why

The 2.8 collections redesign is the largest change between neighbouring releases, yet the 2.7 → 2.8 diff only showed
`@tailrec` and `toLower`. `isPalindrome` only *reads* collections, and `CanBuildFrom` only matters when generic code
*builds* one of the type it was given. Following the talk's rule (add machinery only when the problem demands
it), the problem grows by one step: after checking a palindrome, make one. "Give me back what I gave you" is exactly
what `CanBuildFrom` exists for, and `"abc"` → `"abcba"` makes it visible in one line.

*Shortest* palindrome, not just "xs followed by its reverse", because it's the answer a reader expects, and because
finding the palindromic suffix reuses `isPalindrome`. That makes `palindromize` depend on `Eq`, so the type-class
thread and the collections thread meet in one signature. It costs one helper, which is the same in every version,
so the per-version diffs still show only how the result gets built.

The name `palindromize` shares the stem of `isPalindrome` and `checkPalindrome`. It's a verb, like the collection
operations it's built from (`reverse`, `map`, `filter`), it means "add the fewest elements" on puzzle sites (as
ours now does), and `xs.palindromize.isPalindrome` always holds.

Method syntax is included because every other operation has it, so a function-only `palindromize` stood out. The
wrapper's changing shape is part of the collections story rather than noise: carrying `Repr` is exactly what the 2.8
design asked of library authors, and the 2.13 `IsSeq` pattern is what replaced it.

### Alternatives rejected

- **Other names.** `mirrored` describes the mechanics but doesn't say "palindrome". `palindrize` isn't a word and
  drops the shared stem. `toPalindrome` suggests a conversion to a type named `Palindrome`, which is also our result
  case. `palindromized` follows `sorted`, but participles are the exception in Scala's collections.
- **Mirroring the whole sequence** (`xs` + reverse without the first element: `"abcb"` → `"abcbcba"`). Simpler, but
  not the shortest, doesn't use `Eq`, and turns `"racecar"` into a 13-character palindrome.
- **A linear-time suffix search** (via the KMP failure function on the reverse of `xs`, a separator, then `xs`). It's
  an algorithm topic, not a language one, like the Manacher's algorithm the talk already excludes. The O(n²)
  "try each suffix" helper is one line and reuses `isPalindrome`.
- **`==` instead of `Eq` in the suffix search.** Then `palindromize` and `isPalindrome` could disagree: with
  `Eq.caseInsensitive` in scope, `palindromize("abA")` would return a string that `isPalindrome` already accepted
  as it was.
- **A version-specific suffix search** (e.g. `tails` from 2.9, or a `@tailrec` helper). It would add diffs that
  aren't about the collections redesigns.
- **A filtering or normalizing operation** (e.g. dropping ignored characters). `filter` already returns `Repr` in
  2.8 without any implicit, so no `CanBuildFrom` would appear in our code.
- **Passing the `CanBuildFrom` through to `++`** (`xs ++ xs.reverseIterator.drop(…)`). It's shorter, but it hides
  what the implicit *is*. Filling the builder by hand shows it's a builder factory. It also makes the 2.13 diff tiny
  (`bf(xs.repr)` → `bf.newBuilder(xs)`), so the slide is about the signature.
- **The 2.13 "no implicit needed" form**, `palindromize[A, CC[X] <: SeqOps[X, CC, CC[X]]](xs: CC[A]): CC[A]`. It
  shows that ordinary code lost `CanBuildFrom`, but a `String` then comes back as an `IndexedSeq[Char]`. Keeping
  `String` working is the point of the example, and `IsSeq` + `BuildFrom` is the documented 2.13 way to do that.
- **In 2.13, a second wrapper for `palindromize` next to the `Seq[A]` value class.** It would keep the value class
  for the Boolean methods, but two conversions with overlapping receivers are harder to read. One `IsSeq` wrapper
  serves all three methods and brings `String` method syntax.
- **In 2.13, the wrapper method written without the explicit `[Repr, seq.A]` and `seq: seq.type`.** It doesn't
  compile: scalac can't unify `seq.A` (with `seq: S`) with the function's `{ type A = A0 }` refinement. The
  alternative, duplicating the five-line body in the wrapper, would let the two copies drift apart.
- **`IsTraversableLike` in 2.10–2.12**, which would allow `"abc".palindromize` before 2.13. It adds a third mechanism
  without a new language feature, and it doesn't fit the implicit value class.

### Limitations accepted

- The suffix search is O(n²) on an `IndexedSeq` (up to n suffixes, each checked in O(n)), and O(n³) on a `List`,
  where each check's `:+` recursion is itself O(n²). `palindromicSuffixStart` also copies a `String` once
  (`ops.toSeq` / `xs.toSeq`).
- 2.5–2.12 still can't use method syntax on a `String` (views don't chain), so their tests use the function form for
  strings.
- The 2.13 wrapper isn't a value class, reversing the 2.10/2.11 value-class beat. That's the documented 2.13 pattern.
- 2.5's `palindromize(List(1, 2, 3)) == List(1, 2, 3, 2, 1)` is `false` (no content-based equality), so the 2.5–2.7
  tests compare with `.toList` and `.mkString`.
- The talk's §2 budget was already full. Stage 5b adds about two slides, which is recorded as an open item in the
  talk spec.

### Verification

- Each form was compiled and run in isolation first. The 2.5–2.7 form returns a `Seq`, with `.toList` equal to the
  expected `List`. The `SeqLike`/`CanBuildFrom` form returns `String`/`List`/`Vector` on 2.8, 2.9 and 2.12. On 2.13
  the same code fails for `String` ("found: WrappedString, required: String"). The `IsSeq`/`BuildFrom` form works on
  2.13. The Scala 3 extension works on 3.0 and 3.9, and the `[Repr: IsSeq as seq]` form on 3.6 and 3.9.
- The wrappers were prototyped on 2.8, 2.10, 2.12 and 2.13, including `"racecar".isPalindrome`, an explicit
  `Eq.caseInsensitive` and a local implicit `Eq` on 2.13. The 2.13 wrapper needed the explicit type arguments
  described above, and `-feature` required the `implicitConversions` import.
- The 2.10–2.13 sources compile without warnings under `-deprecation -feature`.
- The shortest-palindrome version was prototyped on 2.5 and 2.7 first: `"abc"`, `"abcb"`, `"abb"`, `"racecar"`, `""`,
  `"a"` and `"abac"` give `"abcba"`, `"abcba"`, `"abba"`, `"racecar"`, `""`, `"a"` and `"abacaba"`, and `"abA"` stays
  as it is with `Eq.caseInsensitive`.
- `./mill __.test`: 2.10–2.13 and 3.0–3.9 pass (11 tests each, 12 in 3.7–3.9). `legacy/test.sh`: 2.5–2.9 pass (11
  tests each). The tests cover the shortest cases (`"abcb"`, `"abb"`, `"racecar"`, `""`) and an `Eq` in scope.
- `tools/evolution.py` required a new `2/13/NOTES.md`, and `--check` passes.

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

- Several versions are identical apart from the header: 2.5–2.7, 2.8–2.9, 3.0–3.5 and 3.6–3.9 (3.7–3.9
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
