# Design Log

Newest entries first. Each entry records what changed, why, the alternatives rejected, the limitations accepted, and
how it was verified. Current project facts live in `STATE.md`.

---

## 2026-09-28 — Matchers instead of `assert` in the tests

### What changed

Every suite mixes in ScalaTest's matchers and writes its checks as `x shouldBe true`, `x shouldBe false` and
`x shouldBe expected` instead of `assert(x)`, `assert(!x)` and `assert(x == expected)`. 2.5–2.9 write
`x should be (true)`: ScalaTest 1.x only has `ShouldMatchers`, and `shouldBe` arrives with ScalaTest 3 in 2.10. The
stand-in for 2.5 and 2.6 gains a minimal `ShouldMatchers` (`should be (…)` only) and loses its unused `assert`.

### Why

The checks read as statements, with no `assert(…)` parentheses and no `!` on the negative cases. Comparing values
gets better failure messages: `"abcb[a]" was not equal to "abcb[]"` shows both values and where they differ.

### Alternatives rejected

- **`AnyFlatSpec` or `AnyFreeSpec`.** They change how a test is named (`"x" should "y" in {`), not the checks, and
  the stand-in would need their naming syntax.
- **utest, whose `assert` takes several conditions.** It's only published for 2.11+ and Scala 3.
- **A custom `palindrome` matcher (`"aa" shouldBe palindrome`).** It needs a matcher for both `String` and
  `Seq[A]` with an `Eq` in every version: test machinery the talk would have to explain.
- **Table-driven loops.** They'd shorten the suites, but inputs checked in a loop need a clue to say which one
  failed. They can still be added on top.

### Limitations accepted

A failed Boolean check only says `false was not equal to true` plus its line. `assert` names the expression, but in
Scala 3 in its compiler-expanded form (`Palindrome$package.isPalindrome[scala.Char](scala.Predef.wrapString("ab"))(…)
was false`), so little is lost.

### Verification

Tried on 3.9 first, then applied to the other versions by a script (`assert(!x)` → `x shouldBe false`,
`assert(x == y)` → `x shouldBe y`, `assert(x)` → `x shouldBe true`); its 3.8 output is identical to the
hand-written 3.9 suite. `./mill __.test` passes all 14, and `legacy/test.sh` passes 2.5–2.9 (13 tests each), including
real ScalaTest 1.0, 1.8 and 1.9.2. Two deliberately broken checks in 2.5 fail in the stand-in (`false was not true`,
`abba was not abb`). A throwaway 3.9 suite showed the failure messages quoted above.

---

## 2026-09-28 — Version directories at the top level: `v2_5` … `v3_9`

### What changed

The version directories moved from `2/<minor>` and `3/<minor>` to the top level as `v2_<minor>` and `v3_<minor>`
(`2/13` → `v2_13`, `3/9` → `v3_9`), and the Mill modules are named the same (`./mill v3_9.test`). The empty group
files `2/package.mill.yaml` and `3/package.mill.yaml` are gone. `tools/evolution.py`, `talk/morph.py`,
`legacy/test.sh` and the Claude Code hook find the versions under the new names.

### Why

One flat level of versions is easier to browse than two, and the directory name says which version it is.

### Alternatives rejected

- **`v2.13`, the version as written.** Mill 1.1.10 silently skips a module directory with a dot in its name: it
  isn't discovered, and `./mill v2.13.compile` can't resolve. Keeping the dot would mean replacing the declarative
  YAML modules with a Scala `build.mill` that sets each module's directory, and the module names still couldn't
  contain the dot.
- **`v2-13` or `v213`.** Both are discovered too, but `v2-13` isn't a Scala identifier, and `v213` reads ambiguously.

### Limitations accepted

The directory and module names use `_` where the version has a dot. Older entries below refer to the old paths
(`2/13`, `3/9`).

### Verification

Probed in a scratch copy of the build: `v2.13` isn't discovered; `v2_13`, `v2-13` and `v213` are, and `v2_13.test`
passes. After the move, `./mill resolve __.test` lists `v2_10.test` … `v3_9.test`, `./mill __.test` passes all 14
(13 tests each), `legacy/test.sh` passes 2.5–2.9, and `tools/evolution.py --check` passes. The morph deck regenerates
unchanged; the annotated decks change only in the speaker note that names the 3.9 source path.

---

## 2026-09-28 — Deck versions in the directory names

### What changed

The four decks share one version lineage, and each deck's directory starts with its version: `talk/1.2-deck`,
`talk/2.3-morph`, `talk/3.2-annotated`, `talk/4.1-annotated-all`. The major number is the kind of deck, in the order
each builds on the ones before it (1 explains, 2 animates, 3 does both, 4 does both for every change); the minor
number counts the revisions that changed the code a deck shows or its look. `talk/README.md` has the table with each
revision. The decks themselves are unchanged; the generators and `render.py` point at the new paths.

### Why

The decks are one line of development, each built from the previous ones, so one lineage says how they relate.
Putting the version in the directory name keeps it visible in the repository without changing any slide.

### Alternatives rejected

- **A version per deck, each starting at 1.0.** It hides that 3 merges 1 and 2, and that 4 extends 3.
- **Stamping the version on the cover slides and in `deck.json`.** It changes the decks, and a stamp can go stale.
- **A slash as the delimiter (`3.2/annotated`).** It would make each version a directory level of its own.

### Limitations accepted

A revision renames the deck's directory, and the path in its generator. The artifacts keep their links.

### Verification

`git mv` keeps the history; regenerating the three generated decks into the new directories reproduces them byte for
byte. `talk/render.py` finds all four decks under their new names.

---

## 2026-09-27 — Review of the code, notes and slides

### What changed

A pass over every version's code, tests and notes, every talk slide and speaker note, and every note in the
annotated decks, checking that each is correct, relevant and idiomatic Scala for its release.

- **The 2.5–2.9 loop** walks two indices inward, `loop(from + 1, to - 1)` from `loop(0, xs.length - 1)`, instead of
  recomputing the far end from `xs.length` on every step.
- **`palindromize` from 2.8 on** reads the input as a `Seq` once (`val elems = xs.toSeq`, `seq(xs).toSeq` from 2.13)
  and mirrors with `elems.take(start).reverse`, the same idiom as 2.5's `xs ++ xs.take(start).reverse`. Before,
  2.13 and 3.x called `ops.toSeq` inside the search, copying a `String` input on every step, and the mirror was
  `reverseIterator.drop(length - start)`. The 2.8 → 2.13 diff now changes exactly `xs.toSeq` → `seq(xs).toSeq`,
  `bf(xs.repr)` → `bf.newBuilder(xs)` and `result` → `result()`.
- **Test names** say what they expect: "accepts palindrome strings", "rejects non-palindrome strings".
- **Prose corrections.** The O(n²) caveat for `x +: middle :+ y` now names `String` too (each step copies a
  substring) and credits `Vector`, not every `IndexedSeq`, with staying linear. 3.0's notes and the 2 → 3 table no
  longer mention `if … then … else`, which left the code with the result ADT. 2.13's notes quote the wrapper's call
  with its `eq` argument, and say that leaving out `implicitConversions` draws a warning rather than being required.
  The talk spec, `STATE.md`, the slides and the annotated notes follow the new code; resolved placeholders are gone
  from the speaker notes.

### Verified rather than assumed

- The recursive call inside `||`/`&&` compiles to a jump in 2.5, 2.7 and 2.8, before and after the change (`javap`
  shows `goto 0`), so "scalac already compiles it to a loop" holds.
- `"racecar".reverse == "racecar"` is `false` on 2.7.7 and `true` on 2.8.2.
- 3.5.2 rejects both `given universal: [A] => Eq[A]` and `[A: Eq as eq]`; 3.6.4 accepts both.
- The repository is public; the release years in the timeline are right.

### Alternatives rejected

- **Renaming the `Eq` parameter from `eq`**, which shadows `AnyRef.eq`. It reads well, nothing in the code uses
  reference equality, and the name appears on most slides.
- **`tails.indexWhere(isPalindrome(_))` for the suffix search.** Neater, but 2.5–2.8 have no `tails`, and the talk
  relies on the search being the same line in every version.

### Verification

All 19 versions pass: `./mill __.test` (14 versions, 11 tests each) and `legacy/test.sh` (2.5–2.9).
`tools/evolution.py --check` passes. The every-change deck's coverage check passes after re-anchoring its notes on
the new code. `talk/render.py` passes for all three decks, and I checked the changed slides' screenshots.

---

## 2026-09-27 — The every-change variant, and a more exact token matcher

### What changed

`talk/annotated.py --all-changes` builds `talk/annotated-all/project/`, a variant of the annotated deck in which
every change between two versions is highlighted and explained. The changes are declared per version in `CHANGES`:
each is one or more highlighted code spans and one note, with the tail pointing at whichever highlight gives the
best spot. The build fails if any token that's new in a version (one the previous version has no counterpart for)
lies outside every highlight. 2.5, the first version, keeps the talk's notes, since it has nothing to compare with.
The variant has 17 notes.

The token matcher in `talk/morph.py` now works in phases: identical lines; similar lines, paired across the whole
code; what's left within each changed region; then identifiers that moved. Before, it matched tokens across a whole
changed region at once, so a token on an almost unchanged line could pair with one on another line. The 2.10
signature was flagged as changed, and its tokens flew around in the morph. All three generated decks use the new
matcher.

Note placement in `annotated.py` became more thorough: notes are placed largest first (they still appear in reading
order), a note may point at any of its highlights, a note that finds no room moves to the front and the layout
starts over, and tails keep clear of other tails.

### Why

The annotated deck's notes were written by hand from the talk's points, two or three per slide, so smaller changes
(`b.result()`, `val ops = seq(xs)`) had none, and nothing checked the notes against the diffs. Deriving the changes
from the morph's own token matching makes coverage checkable.

### Alternatives rejected

- **One note per changed span.** 2.8 alone has 14 spans. Related edits share a note instead (the three builder
  lines in 2.8, `BuildFrom` and `newBuilder` in 2.13), each still highlighted.
- **Replacing the annotated deck.** The variant is denser: the talk's version keeps the main points; this one is for
  reading closely. Both are generated from the same code.
- **Letting tails cross code or each other on crowded slides.** Merging notes about one idea kept every slide clean
  instead: 2.8 has three notes, 2.13 four, 3.0 three.

### Limitations accepted

- The notes are grouped by hand. The check guarantees that every change is highlighted, not that the grouping is
  the best one.
- Removed code (2.10's index loop, 3.0's braces) isn't on the new slide, so only its note can mention it.

### Verification

`talk/annotated.py --all-changes` passes its coverage check for every version. `talk/render.py --screenshots` passes
for both annotated decks, and I checked the variant's code slides in the screenshots: no bubble or tail covers code,
and no tails cross. The morph deck regenerates with the new matcher, 69–92 runs per slide.

---

## 2026-09-27 — `talk/annotated.py`: the morph with handwritten notes

### What changed

A third deck, `talk/annotated/project/` (artifact <https://claude.ai/artifact/36zpmLsjkc1dcmvW7n6JPr>), merges the
other two. The talk deck's framing and side-topic slides are copied in. The code slides are the morph deck's, with
14 handwritten notes in speech bubbles (Fuzzy Bubbles, cream on a fill clearly lighter than the code panel, a thin amber
outline). Each bubble's slender tail ends at a soft amber highlight behind the code it explains; the highlight fades
in with its note, and paints behind the code so the text stays crisp. The notes fade in one per click after each morph, and
the speaker notes carry the rest. Where a talk slide interrupts the morph (value classes and SAM after 2.10; the 2 → 3
table before 3.0), the code is shown once more afterwards, so the next change still morphs. All slides share one style, the talk deck's code slides' in a dark palette:
an amber eyebrow, a 64px heading, and the code in a panel one step lighter than the background with a hairline edge.
The code slides are built that way too. Their panel is pinned, with one id on every code slide, so a morph resizes it
instead of fading it, and their notes stay inside it. All code in the deck is 24px with line height 1.4: the largest
size at which the tallest code (2.8, 17 lines) fits under the heading. Lines too long for the panel are wrapped
where the talk deck wraps them: after a `)(` between parameter lists, else after a `, ` between parameters. The copied
slides' code is re-highlighted with `morph.py`'s highlighter, and their panels get the same padding and code size. Removed diff lines stay dimmed and
comments grey. The 2 → 3 table becomes two code panels side by side, because table cells can't hold coloured spans.
`talk/morph.py` is split
into `load_states`, `chain` and `code_runs_html`, which both generators use; the morph deck's output is unchanged.
`talk/render.py` takes an optional deck directory.

Bubbles are placed automatically. For each note, the generator searches the slide for the position nearest its anchor
where the bubble overlaps no code and no other bubble, and where the tail's drawn curve crosses no code but its own.
It fails if an anchor isn't in the code or nothing fits. Above or below the code, the tail lands on the anchored
words. Beside it, the note is a margin note: the tail points at the end of the line, and the highlight marks the
words.

### Why

The morph shows *what* moves, and the talk deck says *why*. Put next to the code, a note needs no slide of its own and
no reading back and forth between the slide and the speaker. Placing the bubbles automatically keeps the deck
regenerable: when the code changes, the notes follow their anchors.

### Alternatives rejected

- **Hand-placed bubbles.** Every code change would mean re-placing them, and nothing would catch a bubble covering
  code.
- **`x-connector` arrows and plain boxes.** The format's connectors are straight or right-angled lines with a
  constant arrowhead, which is diagram-like rather than handwritten. The bubble and its tail are one SVG outline
  instead, so the tail joins the bubble without a seam.
- **Tails that always point at the anchored words.** In dense code (2.10's `x +: middle :+ y`), every path to the words
  crosses other lines. Margin notes that point at the line's end, with the words highlighted, never do.
- **Testing the tail as a straight line.** The first version did, and the 2.8 `@tailrec` tail curved through `Int` and
  `1 - from`. The test now samples the drawn curve, and a tail bows at most 14px.
- **Interleaving the talk slides without repeating the code.** Magic move only animates between neighbouring slides,
  so the 2.10 → 2.13 and 2.13 → 3.0 morphs would be lost. The repeat costs one click each.
- **Code at the talk deck's 28px.** With the heading above it, a 28px panel holds about 14 lines, and 2.8's code
  is 17. Dropping the heading from the tallest slides, or shrinking only their code, would break the uniformity
  asked for; 24px everywhere is the size that fits every slide.
- **The morph deck's layout (no panel, a one-row header) for the code slides.** It made the code slides look unlike
  every other slide in the deck.
- **An underline beneath the code a note is about**, the first version. A highlight behind the code marks it more
  clearly from a distance. The first bubble fill, one shade off the code panel, also blended in; the fill is now
  clearly lighter.
- **Other fonts for the notes** (tried in the deck: Caveat, Mynerve, Shantell Sans, Handlee). Fuzzy Bubbles was
  picked from 21 Google fonts compared side by side on a sample page, each in a note bubble at matched sizes. Its
  soft, round letters set the notes apart from the code while staying legible from the back of a room. The
  connected scripts were slower to read. Its fallback is Trebuchet MS, not Comic Sans, which would turn the notes
  cartoonish if the font failed to load.
- **Restyling the talk deck itself.** It's presented on its own too, in its light style. Restyling at build time
  keeps the two decks independent, and the talk deck stays the single source of those slides' content.
- **Dropping the side topics.** `Eq`, value classes, SAM and the given syntax aren't in the morphing methods. Their
  slides stay, and the 3.6 given syntax moves into that slide's speaker notes.

### Limitations accepted

- Tight slides limit the notes. 2.10 has room for one margin note beside its pattern, so its two points share one
  bubble. The 2.8 `@tailrec` note gets a long hairline tail, because nothing closer is free.
- Bubble widths come from an estimate of Fuzzy Bubbles's character width (0.60 em at 26px; 0.56 overflowed one
  note by 8px). The render check reports any
  text that overflows its bubble.
  overflows its bubble.
- Nothing in the repo plays the build-in and magic-move animations. The static render shows every note at once.

### Verification

`talk/render.py --screenshots talk/annotated`: all 21 slides pass (the takeaways heading wraps on purpose). I checked
the code slides' screenshots: no bubble or tail covers code. `talk/morph.py` regenerates the morph deck byte for
byte after the refactor.

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
