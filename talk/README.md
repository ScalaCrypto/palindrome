# Talk material

The slide decks for *A Brief History of Scala* (ScalaDays 2026). The talk itself is specified in
`../scaladays-2026-talk.md`, and the code it shows comes from `../EVOLUTION.md`.

**The main deck, the one presented, is `4.1-annotated-all/`**: the talk deck's slides and the code morph, with a
handwritten note for every change between versions (see "The every-change variant" below). The other decks are its
inputs (`1.2-deck`, `2.3-morph`) or an alternative with fewer notes (`3.2-annotated`); after any change to the code,
the talk deck or the notes, regenerate the main deck, check it and republish it.

- `1.2-deck/project/`: the talk deck's source files, written by hand. `deck.json` holds the title, slide order, sections and fonts, and
  `slides/<id>.html` holds one slide each, including its speaker notes (`<aside>`). The format is the one the claude.ai
  Slides artifact uses; the paths match the artifact's own.
- `2.3-morph/`, `3.2-annotated/`, `4.1-annotated-all/`: the generated decks, below.
- `tag-cloud/`: a deck of who wrote each Scala release, generated from `tag-cloud/authors.json`, below.
- `render.py`: renders a deck, the main deck unless another is named, in headless Chrome and checks the layout.

## Deck versions

The decks share one version lineage, and each deck's directory starts with its version. The major number is the kind
of deck, in the order each builds on the ones before it; the minor number counts its revisions, the ones that
changed the code it shows or its look.

| Directory | Deck | Revisions |
|---|---|---|
| `1.2-deck` | The talk deck, written by hand | 1.0 with the result ADT; 1.1 simplified code; 1.2 review |
| `2.3-morph` | The code morph | 2.0; 2.1 simplified code; 2.2 exact token matching; 2.3 review |
| `3.2-annotated` | 1 and 2 merged, with handwritten notes | 3.0; 3.1 uniform style, font, highlights; 3.2 review |
| `4.1-annotated-all` | 3 with a note for every change; **the main deck** | 4.0; 4.1 review |

A revision renames the directory (`git mv talk/3.2-annotated talk/3.3-annotated`, and the path in `annotated.py` or
`morph.py`); the decks' artifacts keep their links.

## The talk deck and its artifact

The hand-written talk deck is edited as a claude.ai Slides artifact:
<https://claude.ai/artifact/4nvk9BRuCLeutLsoEpQt3d> (private until shared from its Share menu). `1.2-deck/project/` is the
versioned copy of it. Keep the two in step:

- **After editing the artifact** (in the browser, or through Claude): read its files back into `1.2-deck/project/` and
  commit them. With Claude Code, ask it to read the artifact's `project/deck.json` and `project/slides/*.html` and
  copy them here.
- **After editing files here**: publish them to the artifact with `1.2-deck/` as the root, so each file keeps its
  `project/…` path.

The code on the slides is copied from the version sources, sometimes re-wrapped to fit. Nothing checks it against
the sources, so after a code change, compare the affected slides with `EVOLUTION.md`.

## The code-morph deck

`morph.py` generates a second deck, `2.3-morph/project/`, from the version sources: the palindrome methods on one slide
per version where they change, each slide morphing into the next with a magic-move transition, so the code changes in
place. Its artifact is <https://claude.ai/artifact/RYU4d3bpEjxvV7MX1sfTKb>. It's generated, so it's never edited by
hand: after a code change, run `talk/morph.py` and publish `2.3-morph/project/` to the artifact with `2.3-morph/` as the root.
How it matches tokens between versions is in `../DESIGN.md`.

## The annotated deck

`annotated.py` generates a third deck, `3.2-annotated/project/`, that merges the other two. The talk deck's framing and
side-topic slides (`Eq`, value classes, SAM, the 2 → 3 table) are copied in, restyled to its dark palette with their
code highlighted like the code slides. Their code panels shrink to the code slides' size, and anything pinned below
a panel (Stage 0's "… or two", which fades in on a click) moves up with it. The code slides are the morph deck's,
with handwritten notes in speech bubbles that point at the code they explain and fade in one per click after each
morph. Where a talk slide interrupts the morph, the code is shown again afterwards, so the next change still morphs.
The notes and the slide order are in `annotated.py` (`NOTES`, `SEQUENCE`), and the bubbles are placed automatically
next to their code. Its artifact is <https://claude.ai/artifact/36zpmLsjkc1dcmvW7n6JPr>. It's generated too: after changing the
code, the talk deck's slides or the notes, run `talk/annotated.py`, check it with
`talk/render.py --screenshots talk/3.2-annotated`, and publish `3.2-annotated/project/` with `3.2-annotated/` as the
root.

### The every-change variant: the main deck

`talk/annotated.py --all-changes` builds a variant, the main deck, `4.1-annotated-all/project/`, whose notes cover every change instead
of the talk's main points. From 2.8 on, each change between two versions is highlighted and explained. The changes
are declared in `CHANGES` in `annotated.py`, and the build fails if any code that's new in a version lies outside
every highlight. Its artifact is <https://claude.ai/artifact/25dnv7jYfipK6R27X8g94t>. After changing the code, the talk
deck's slides or the notes, run `talk/annotated.py --all-changes`, check it with
`talk/render.py --screenshots`, and publish `4.1-annotated-all/project/` with
`4.1-annotated-all/` as the root.

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
top ones. The deck isn't part of the version lineage above: it shows who wrote Scala, not this repository's code. Its
artifact is <https://claude.ai/artifact/BBnmYfzdH7pmk3VQybdQdm>.

## Checking the layout

```bash
talk/render.py                 # measure every slide of the main deck; exit 1 if anything overflows
talk/render.py --screenshots   # also write out/talk-render/4.1-annotated-all/shots/*.png and contact sheets sheet*.png
talk/render.py --screenshots talk/1.2-deck   # the same for another deck, into out/talk-render/1.2-deck/
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
