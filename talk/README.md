# Talk material

The slide deck for *A Brief History of Scala* (ScalaDays 2026). The talk itself is specified in
`../scaladays-2026-talk.md`, and the code it shows comes from `../EVOLUTION.md`.

- `5.14-deck/project/`: the deck. `deck.json` holds the title, slide order, sections and fonts, and `slides/<id>.html`
  holds one slide each, including its speaker notes (`<aside>`). The format is the one the claude.ai Slides artifact
  uses; the paths match the artifact's own.
- `deck.py`: builds the deck's code slides, their notes and its slide order; below.
- `morph.py`: the code morph `deck.py` uses.
- `tag-cloud/`: a separate deck of who wrote each Scala release, generated from `tag-cloud/authors.json`, below.
- `render.py`: renders a deck, the talk's deck unless another is named, in headless Chrome and checks the layout.
- `present.py` and `present/`: presents the deck from this computer, with a presenter view; below.

## The deck

The deck is <https://claude.ai/artifact/25dnv7jYfipK6R27X8g94t> (private until shared from its Share menu), and
`5.14-deck/project/` is its versioned copy. It has two kinds of slide:

- **Code slides** are generated from the version sources by `deck.py`, in three tracks: the palindrome methods
  (`m2-5`, …, `m3-6`), `Eq` (`e2-5`, …, `e3-6`) and Scala 2's method syntax (`o2-5`, …, `o2-13`; Scala 3's extensions
  are on the method slides). Each track gets a slide per version where its code changes, and each slide morphs from
  the track's previous one with a magic-move transition, so the code changes in place. The deck goes version by
  version: each Scala version that changes something starts with its slide from the tag-cloud deck (`tc2-8`, …, copied
  from `tag-cloud/project/`), then, for each track that changes, the track's previous state shown again (`…-again`),
  whose last click fades in the next slide's heading, and its new state, so the change morphs in place. A method slide shows only the methods that
  change in that step (2.9: `palindromize`; 2.10: `isPalindrome`), and an `Eq` slide only the definitions that change
  (`object Eq`, and `trait Eq` in 2.5 and 3.0). Every slide carries the tag-cloud deck's timeline
  along the bottom, with its version in amber, instead of a version label above the heading. After each tag-cloud
  slide comes a hand-written "New in Scala x" slide (`f2-8`, …): the version's headline changes, with the ones the
  following slides use in amber. A slide shown again appears without a transition and without a heading; a click brings in the
  next slide's heading, and the click after that morphs it into the new state, the heading staying in place.
  The code track starts with the opening one-liner (`m0-again`), which morphs into 2.5. From the second state
  of a track on, every change is highlighted and explained in a speech bubble, and the build fails if any code that's
  new in a version lies outside every highlight. Where a step changes both methods (2.5, 2.8, 3.0), it morphs in two clicks:
  first `isPalindrome`, onto a slide that still shows the old `palindromize` (`m2-8-is`, …), then `palindromize`. Its
  first slide can have a heading of its own (2.8's `@tailrec`); the second then shows only `palindromize`'s bubbles. The
  bubbles fade in one per click after each morph, `isPalindrome`'s before the second, where they stay put; they're placed
  automatically wherever they fit on the slide, clear of the heading, the code and the timeline: the code panel holds
  only its code, so a bubble never adds a line to it. A bubble never mentions a later version. After 3.6, a made-up Scala 4.0 follows: its tag-cloud and "New in" slides
  (`cloud4-0`, `f4-0`, hand-written) and a code slide (`m4-0`) whose match names `x` twice. The notes are
  `NOTES`, `EQ_NOTES` and `OPS_NOTES` in `deck.py`, the speaker notes `ASIDES`, `EQ_ASIDES` and `OPS_ASIDES`, and how
  tokens are matched between versions is in `../DESIGN.md`. **Never edit these by hand**: the next build overwrites them.
- **Every other slide is hand-written**: the cover, the framing slides, the "New in" slides, the takeaways and the reserve slides. Edit them in the artifact or in their files. The build leaves them
  as they are, except that it normalizes their code panels: the code slides' padding and code size, and the code
  coloured the same way. So write their code as plain text; the colours come back on the next build. Their code is
  copied from the sources and nothing checks it against them, so after a code change, compare them with `EVOLUTION.md`.

The slide order and the sections are `SEQUENCE` and `SECTIONS` in `deck.py`, and the build writes them into
`deck.json`, keeping its other keys. To add, remove or reorder a slide, change `SEQUENCE` (and add or remove the
slide's file); the build fails if a hand-written slide's file isn't in `SEQUENCE`, or a slide in it has no file.

After changing the code, the notes or a slide:

```bash
talk/deck.py                 # rebuild the code slides and deck.json
talk/render.py --screenshots # check the layout
```

then publish `5.14-deck/project/` to the artifact with `5.14-deck/` as the root, so each file keeps its `project/…`
path. After editing the artifact in the browser (or through Claude), read its changed `project/slides/*.html` back
into `5.14-deck/project/` first, then rebuild, check, commit and publish. With Claude Code, ask it to read the
artifact's changed slides and copy them here.

## Deck versions

The deck's directory starts with its version: the major number is the kind of deck, the minor its revision. A
revision that changes the deck's code or look renames the directory (`git mv talk/5.14-deck talk/5.15-deck`, and `DECK`
in `deck.py`); the artifact keeps its link.

5.0 merged the four decks that came before it: the hand-written talk deck (1.x, light, with its own hand-copied code
slides), the generated code-morph deck (2.x), and the annotated decks that combined the two (3.x with the talk's main
points, 4.x with a note for every change). 5.0 is 4.1 with its framing slides edited in place instead of copied and
restyled from 1.2. Why, and what was given up, is in `../DESIGN.md`; the old decks are in the git history. 5.1 adds
the `eq` slide ("Equality for Any", the `Eq` trait) after the goal, and a `Vector` `palindromize` example on the goal
slide. 5.2 follows the denser `palindromize` (`tails.indexWhere`, and a one-expression build from iterators),
which adds a code slide for 2.9, the first version with `tails`, and adds the reserve slide `r-linear`, a linear
`palindromize` with KMP. 5.3 adds `s25-ops` after `s25-types`: 2.5's `PalindromeOps` wrapper and the
`implicit def` that converts to it. 5.4 generates the `Eq` and method-syntax slides as tracks of their own, where they
change, morphing from version to version; they replace `s25-types`, `s25-ops`, `s210-valueclass` and `s212-sam`. 5.5 groups the deck by version, with each
version's tag-cloud slide before it, the timeline on every slide, and only the changed methods on a method slide.
5.6 drops the method-syntax steps that repeat the method slides' changes (2.8, 2.13) and the Scala 3 divider and
2 → 3 table, and shows `palindromize`'s results on the goal slide.
5.7 opens 2.5 like every other version, with its tag-cloud and "New in Scala 2.5" slides instead of the Scala 2
divider. 5.8 starts the code track from the one-liner, places
the bubbles outside the code panel instead of growing it, morphs `isPalindrome` before `palindromize` where a step
changes both, drops the last slide's `isPalindrome`, and ends the tour with a made-up Scala 4.0 (Prolog extractors). It also adds
case-insensitive examples to the goal slide, a QR code to the thank-you slide, and Knuth–Morris–Pratt's full name, without the abbreviation, to `r-linear`. 5.9 makes the code
slides' code 25px instead of 24px (the reserve slides keep 24px), wrapping a few more of Scala 2's long lines.
5.10 follows Scala 3's `x === y` (an extension in `trait Eq`, with `isPalindrome`'s `Eq` an unnamed context
bound), so 3.6 changes only `palindromize`; the `Eq` slides show `trait Eq` only where it changes (2.5, 3.0).
5.11 renames `palindromize`'s `elems` to `seq`, and the `IsSeq` instance it reads it from to `isSeq`.
5.12 builds the goal slide over two clicks: `isPalindrome`, then `palindromize`, then the case-insensitive
examples, under a `// case insensitive` comment instead of the `given`; the subheading is gone.
5.13 adds a bubble to 2.5's `palindromize`, before the `Seq` one: it keeps the palindromic tail and mirrors only the
rest, so the result is the shortest palindrome. The two-liner before 2.5 (`m0-again`) gets the heading "What's
wrong?", which 2.5's "A better way" (no longer a question) replaces, and bubbles: the one-liner `isPalindrome` copies
the string just to compare, and its `palindromize` isn't always the shortest. Every slide shown again fades in the
next slide's heading on its last click, so the version's topic comes before the morph.
5.14 shows 2.13's method syntax, as an implicit class, next to 2.13's methods before 3.0: its `isPalindrome` goes
when `isPalindrome` becomes an extension, and the class when `palindromize` does.

## The tag-cloud deck

`tag-cloud.py` generates `tag-cloud/project/`: a cover, then one slide per Scala release from 2.5 to 3.9, with a
cloud of the authors of the commits that went into it. Each slide leads with the release and its year; the commit
and author counts sit centred in amber below the cloud. The commit range and its footnotes are in the speaker
notes, to keep the slide to the cloud. A name's size follows its commit count within that release,
and the release's top committer is in amber. A timeline of the releases runs along the bottom of every slide, with
the slide's release marked in amber; it fades out at the left edge past 2.5, into the releases the deck doesn't
cover. The slides change with a sliding (`push`) transition. The data is `tag-cloud/authors.json`: per release, the commit range, the
totals and the top 60 authors, plus the method, every merge of one person's aliases, and every exclusion (bots,
unattributable SVN commits). It was gathered from history-only clones of scala/scala and scala/scala3 on 2026-09-28;
its `method` says how, including the releases that needed another range (2.7, 3.6, 3.8). Slide text can't be under
24px, so the generator shows as many names as fit on a slide (at most 60), and the speaker notes say when it's the
top ones. The deck isn't versioned like the talk's deck: it shows who wrote Scala, not this repository's code. Its
artifact is <https://claude.ai/artifact/BBnmYfzdH7pmk3VQybdQdm>.

## Presenting

The artifact's own speaker-notes window can't open: the frame claude.ai shows the deck in blocks the pop-up, in
Safari and in Chrome alike. So the talk is presented from this computer instead:

```bash
talk/present.py                # serve the deck on http://localhost:8765 and open the presenter view
```

In the presenter view, click "Open slides window", move that window to the external display and press F in it for
full screen. Then drive the talk from the presenter view on the laptop: it shows the current slide, what the next
click shows (the next note, or the next slide), the speaker notes and a timer. → or space for the next click, ← back,
a slide number then Enter to jump, B to black out the slides, T to start or pause the timer, + and − for the notes'
size. The two pages stay in step through the browser (`BroadcastChannel`), so either can be reloaded.

The player, in `present/`, covers what the deck uses of the Slides format's motion: the `fade`, `push`, `none` and
`magic` transitions, and `fade` builds. Magic move works like the artifact's: children with the same `id` on both
slides move and resize, and the rest fade. A morph takes 1.6 seconds here, twice as long as it used to, so the
changing code can be followed; the artifact's own timing can't be set. The deck is read from its files on every page load, and the fonts come from
`render.py`'s cache, so the talk needs no network once the fonts are cached. Before the talk, run through the deck
here as well as in the artifact: the player follows the format, but it isn't the artifact's own renderer.

## Checking the layout

```bash
talk/render.py                 # measure every slide of the talk's deck; exit 1 if anything overflows
talk/render.py --screenshots   # also write out/talk-render/5.14-deck/shots/*.png and contact sheets sheet*.png
talk/render.py --screenshots talk/tag-cloud  # the same for another deck, into out/talk-render/tag-cloud/
```

Each slide is laid out on the deck's 1920×1080 canvas, with the deck's fonts, and measured:

- **Failures:** an element crossing the 128px margins, or text running past its container (a code line past its
  panel, say).
- **Reported only:** a heading that wraps without a `<br>`; the takeaways statement does this on purpose.
- **Skipped:** elements marked `data-bleed`, which run to or off the slide's edge on purpose (the tag-cloud
  deck's timeline).
- **Also printed:** each slide's lowest content edge, against the 952px limit.

It needs Python 3 and Google Chrome or Chromium (set `CHROME` to its path if it isn't found). Fonts are downloaded
from the Google Fonts links in `deck.json` on the first run and cached in `out/talk-render/fonts/`.

This approximates the artifact's renderer; it doesn't run it. It applies the slide format's defaults (no margins,
ruled table cells), but the artifact page can still differ in small ways.
