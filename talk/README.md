# Talk material

The slide deck for *A Brief History of Scala* (ScalaDays 2026). The talk itself is specified in
`../scaladays-2026-talk.md`, and the code it shows comes from `../EVOLUTION.md`.

- `deck/project/`: the deck's source files. `deck.json` holds the title, slide order, sections and fonts, and
  `slides/<id>.html` holds one slide each, including its speaker notes (`<aside>`). The format is the one the claude.ai
  Slides artifact uses; the paths match the artifact's own.
- `render.py`: renders the deck in headless Chrome and checks the layout.

## The deck and the artifact

The deck is presented and edited as a claude.ai Slides artifact:
<https://claude.ai/artifact/PHcDucovro6sTQXs2Xcnbr> (private until shared from its Share menu). `deck/project/` is the
versioned copy of it. Keep the two in step:

- **After editing the artifact** (in the browser, or through Claude): read its files back into `deck/project/` and
  commit them. With Claude Code, ask it to read the artifact's `project/deck.json` and `project/slides/*.html` and
  copy them here.
- **After editing files here**: publish them to the artifact with `deck/` as the root, so each file keeps its
  `project/…` path.

The code on the slides is copied from the version sources, sometimes re-wrapped to fit. Nothing checks it against
the sources, so after a code change, compare the affected slides with `EVOLUTION.md`.

## The code-morph deck

`morph.py` generates a second deck, `morph/project/`, from the version sources: the palindrome methods on one slide
per version where they change, each slide morphing into the next with a magic-move transition, so the code changes in
place. Its artifact is <https://claude.ai/artifact/D5M6ykhDMvCngXQxsWriTy>. It's generated, so it's never edited by
hand: after a code change, run `talk/morph.py` and publish `morph/project/` to the artifact with `morph/` as the root.
How it matches tokens between versions is in `../DESIGN.md`.

## Checking the layout

```bash
talk/render.py                 # measure every slide; exit 1 if anything overflows
talk/render.py --screenshots   # also write out/talk-render/shots/*.png and contact sheets out/talk-render/sheet*.png
```

Each slide is laid out on the deck's 1920×1080 canvas, with the deck's fonts, and measured:

- **Failures:** an element crossing the 128px margins, or text running past its container (a code line past its
  panel, say).
- **Reported only:** a heading that wraps without a `<br>`; the takeaways statement does this on purpose.
- **Also printed:** each slide's lowest content edge, against the 952px limit.

It needs Python 3 and Google Chrome or Chromium (set `CHROME` to its path if it isn't found). Fonts are downloaded
from the Google Fonts links in `deck.json` on the first run and cached in `out/talk-render/fonts/`.

This approximates the artifact's renderer; it doesn't run it. It applies the slide format's defaults (no margins,
ruled table cells), but the artifact page can still differ in small ways.
