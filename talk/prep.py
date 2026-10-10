#!/usr/bin/env python3
"""Builds the speakers' practice documents from talk/script.md and the deck's screenshots, as PDFs for offline
reading on a phone or tablet.

Usage: talk/prep.py      write out/talk-prep/{odd,martin,together}.pdf

- odd.pdf and martin.pdf: one speaker's practice script. Their part at a glance, a plan for practising alone, the
  timing checkpoints, the whole script slide by slide with their own lines highlighted, a cue drill (the line before
  each of theirs, and theirs as first letters only), and the Q&A.
- together.pdf: the rehearsal plan for both, the click map, the hot spots, a timing sheet to fill in, the day-of
  checklist, the whole script, and the Q&A.

The script's turns are laid out as in the presenter view: Odd's on the left in blue, Martin's on the right in
orange. Slide images come from talk/render.py --screenshots (run it first; they show each slide's final build).
Needs Chrome, as talk/render.py does, and macOS's sips to shrink the screenshots.
"""

from __future__ import annotations

import html
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render  # noqa: E402  (talk/render.py: Chrome, and where the screenshots are)

ROOT = render.ROOT
SCRIPT = ROOT / "talk/script.md"
SHOTS = render.OUT / "5.18-deck/shots"
OUT = ROOT / "out/talk-prep"
IMAGES = OUT / "img"

HEADING = re.compile(r"^## (\d+) · (\S+) — (.+?)(?: · (\d+) s · (\d+:\d\d))?$")
NAMES = {"ODD": "Odd", "MARTIN": "Martin", "BOTH": "Both"}


@dataclass
class Line:
    who: str  # ODD, MARTIN or BOTH
    text: str


@dataclass
class Slide:
    n: int
    sid: str
    title: str
    seconds: int | None
    clock: str | None
    reserve: bool
    directions: list[str] = field(default_factory=list)
    lines: list[Line] = field(default_factory=list)

    @property
    def clicks(self) -> int:
        return sum(line.text.count("[click]") for line in self.lines)


def parse() -> tuple[list[Slide], list[tuple[str, str, str]]]:
    """The script's slides, and its timing checkpoints (slide, clock, what to do if later)."""
    slides: list[Slide] = []
    checkpoints = []
    reserve = False
    for raw in SCRIPT.read_text().splitlines():
        if raw.startswith("# Reserve"):
            reserve = True
        elif m := HEADING.match(raw):
            n, sid, title, seconds, clock = m.groups()
            slides.append(Slide(int(n), sid, title, int(seconds) if seconds else None, clock, reserve))
        elif m := re.match(r"^\| (\d+ · [^|]+?) \| (\d+:\d\d) \| ([^|]+?) \|$", raw):
            checkpoints.append(m.groups())
        elif not slides:
            continue
        elif m := re.match(r"^(MARTIN|ODD|BOTH): (.*)$", raw):
            slides[-1].lines.append(Line(m.group(1), m.group(2)))
        elif raw.startswith((" ", "\t")) and raw.strip() and slides[-1].lines:
            slides[-1].lines[-1].text += " " + raw.strip()
        elif raw.startswith("> "):
            slides[-1].directions.append(raw[2:])
    return slides, checkpoints


def initials(text: str) -> str:
    """A line as the first letter of each word, keeping punctuation: the first-letter memory method."""
    words = []
    for token in text.split():
        if token == "[click]":
            words.append("◆")
        else:
            words.append(re.sub(r"([\w'’])[\w'’.]*", r"\1", token))
    return " ".join(words)


def without_clicks(text: str) -> str:
    return re.sub(r"\s*\[click\]\s*", " ", text).strip()


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def spoken(text: str, who: str, me: str | None) -> str:
    """A line's text with its clicks as badges; the badge says who acts on it, for the reader."""
    if me == "MARTIN":
        badge = '<span class="click">▶ CLICK</span>' if who != "ODD" else '<span class="click">▶ CLICK on Odd\'s cue</span>'
    elif me == "ODD":
        badge = '<span class="click">◆ nod: Martin clicks</span>' if who == "ODD" else '<span class="click dim">◆ click</span>'
    else:
        badge = '<span class="click">▶ click</span>' if who != "ODD" else '<span class="click">▶ click (Odd nods)</span>'
    return esc(text).replace("[click]", badge)


def image(slide: Slide) -> Path:
    return IMAGES / f"{slide.n:02}-{slide.sid}.jpg"


def slide_html(slide: Slide, me: str | None) -> str:
    timing = f'{slide.seconds} s · at {slide.clock}' if slide.clock else "reserve, Q&A only"
    clicks = f' · {slide.clicks} click{"s" if slide.clicks != 1 else ""}' if slide.clicks else ""
    directions = "".join(f'<p class="dir">{esc(d)}</p>' for d in slide.directions)
    turns = []
    for line in slide.lines:
        kind = line.who.lower()
        mine = me is None or line.who in (me, "BOTH")
        turns.append(f'<div class="turn {kind}{"" if mine else " other"}"><b>{NAMES[line.who]}</b> '
                     f'{spoken(line.text, line.who, me)}</div>')
    if me == "MARTIN" and not slide.reserve:
        turns.append('<p class="advance">then → next slide</p>')
    if not slide.lines:
        turns.append('<p class="dir">Nobody speaks.</p>')
    return (f'<section class="slide"><div class="head"><h3><span class="num">{slide.n}</span> {esc(slide.title)}</h3>'
            f'<p class="meta">{slide.sid} · {timing}{clicks}</p><img src="{image(slide).as_uri()}">{directions}</div>'
            f'<div class="turns">{"".join(turns)}</div></section>')


def script_html(slides: list[Slide], me: str | None) -> str:
    return "".join(slide_html(s, me) for s in slides)


def drill_html(slides: list[Slide], me: str) -> str:
    """Each of my lines after its cue: the line before it, in full, and mine as first letters."""
    rows, previous = [], None
    for slide in (s for s in slides if not s.reserve):
        new_slide = True
        for line in slide.lines:
            if line.who in (me, "BOTH"):
                cue = []
                if new_slide:
                    cue.append(f'<span class="newslide">slide {slide.n} appears: {esc(slide.title)}</span>')
                if previous:
                    label = "(you, last slide):" if new_slide and previous.who in (me, "BOTH") else NAMES[previous.who] + ":"
                    cue.append(f'<span class="cue-who">{label}</span> {esc(without_clicks(previous.text))}')
                rows.append(f'<div class="drill"><div class="cue"><span class="sn">{slide.n}</span>'
                            f'{"<br>".join(cue)}</div><div class="initials {me.lower()}">{esc(initials(line.text))}</div></div>')
            previous, new_slide = line, False
    return "".join(rows)


def checkpoints_html(checkpoints) -> str:
    rows = "".join(f"<tr><td>{esc(s)}</td><td><b>{c}</b></td><td>{esc(a)}</td></tr>" for s, c, a in checkpoints)
    return f'<table class="grid"><tr><th>At slide</th><th>Clock</th><th>If you\'re later</th></tr>{rows}</table>'


def timing_sheet_html(slides: list[Slide]) -> str:
    """Every version's opening slide as a checkpoint, with room for three runs' times."""
    marks = [s for s in slides if not s.reserve and (s.sid.startswith(("tc", "cloud")) or s.sid in ("takeaways", "thanks"))]
    last = marks[-1]
    minutes, seconds = divmod(sum(int(x) * f for x, f in zip(last.clock.split(":"), (60, 1))) + last.seconds, 60)
    blanks = "<td></td>" * 3
    rows = "".join(f'<tr><td>{s.n} · {esc(s.title)}</td><td><b>{s.clock}</b></td>{blanks}</tr>' for s in marks)
    return (f'<table class="grid timing"><tr><th>Slide</th><th>Plan</th><th>Run 1</th><th>Run 2</th><th>Run 3</th></tr>'
            f'{rows}<tr><td>End of “{esc(last.title)}”</td><td><b>{minutes}:{seconds:02}</b></td>{blanks}</tr></table>')


def click_map_html(slides: list[Slide]) -> str:
    rows = []
    for s in slides:
        if s.reserve or not s.clicks:
            continue
        cues = []
        for line in s.lines:
            parts = line.text.split("[click]")
            owner = f'<span class="{line.who.lower()}-t">{"Odd nods" if line.who == "ODD" else NAMES[line.who]}</span>'
            for i, before in enumerate(parts[:-1]):
                words = before.split()
                if words:
                    cues.append(f'{owner}: “…{esc(" ".join(words[-5:]))}” <b>▶</b>')
                else:  # the click opens the line: show the words it comes before
                    after = parts[i + 1].split()
                    cues.append(f'{owner}: <b>▶</b> before “{esc(" ".join(after[:5]))}…”')
        rows.append(f'<tr><td>{s.n}</td><td>{esc(s.title)}</td><td>{s.clicks}</td><td>{"<br>".join(cues)}</td></tr>')
    return f'<table class="grid clickmap"><tr><th>#</th><th>Slide</th><th>Clicks</th><th>Where the click goes</th></tr>{"".join(rows)}</table>'


def stats(slides: list[Slide]) -> dict[str, tuple[int, int]]:
    out = {}
    for who in ("ODD", "MARTIN"):
        lines = [l for s in slides if not s.reserve for l in s.lines if l.who in (who, "BOTH")]
        out[who] = (len(lines), sum(len(l.text.replace("[click]", "").split()) for l in lines))
    return out


CSS = """
@page { size: 148mm 210mm; margin: 10mm 9mm 11mm 9mm; }
* { box-sizing: border-box; }
body { font: 10.5pt/1.38 -apple-system, 'Helvetica Neue', Helvetica, sans-serif; color: #1d1f24; margin: 0; }
h1 { font-size: 22pt; line-height: 1.1; margin: 0 0 4mm; }
h2 { font-size: 15pt; margin: 0 0 3mm; padding-bottom: 1.5mm; border-bottom: 2px solid #1d1f24; break-after: avoid; }
h2.part { break-before: page; }
h3 { font-size: 11.5pt; margin: 0 0 1mm; }
h4 { font-size: 10.5pt; margin: 3mm 0 1mm; break-after: avoid; }
p { margin: 0 0 2.2mm; }
ul, ol { margin: 0 0 2.5mm; padding-left: 5mm; }
li { margin-bottom: 1.2mm; }
.cover { height: 186mm; display: flex; flex-direction: column; justify-content: space-between; break-after: page; }
.cover .kicker { font-size: 10pt; letter-spacing: 0.08em; text-transform: uppercase; color: #6b7280; }
.cover .big { font-size: 13pt; }
.cover .who { font-size: 30pt; font-weight: 700; }
.odd-c { color: #1f6fd1; } .martin-c { color: #d4660f; }
.box { border: 1px solid #d5d8de; border-radius: 3mm; padding: 3mm 3.5mm; margin: 0 0 3mm; break-inside: avoid; background: #f7f8fa; }
.box.warn { background: #fff6ec; border-color: #f2c595; }
.box.blue { background: #eef5ff; border-color: #b9d4f7; }
.grid { border-collapse: collapse; width: 100%; font-size: 9pt; margin-bottom: 3mm; }
.grid th, .grid td { border: 1px solid #cfd3da; padding: 1.2mm 1.6mm; text-align: left; vertical-align: top; }
.grid th { background: #eef0f3; }
.timing td:nth-child(n+3) { width: 15mm; }
.grid td:first-child { white-space: nowrap; }
.grid.qa td:first-child { white-space: normal; }
.clickmap td:first-child, .clickmap td:nth-child(3) { text-align: center; width: 9mm; }
.odd-t { color: #1f6fd1; font-weight: 600; } .martin-t { color: #d4660f; font-weight: 600; } .both-t { font-weight: 600; }
.slide { border-top: 1px solid #d5d8de; padding: 2.5mm 0 3mm; }
.head { break-inside: avoid; margin-bottom: 1.5mm; }
.head img { display: block; width: 100%; border-radius: 1.5mm; margin: 1mm 0 1.5mm; }
.turn { break-inside: avoid; }
.num { display: inline-block; min-width: 7mm; padding: 0 1.2mm; border-radius: 1.2mm; background: #1d1f24; color: #fff;
  text-align: center; font-size: 9.5pt; }
.meta { color: #6b7280; font-size: 8.5pt; margin-bottom: 1mm; }
.dir { font-style: italic; color: #4b5563; font-size: 9pt; margin-bottom: 1mm; }
.turns { display: flex; flex-direction: column; gap: 1.3mm; }
.turn { max-width: 86%; padding: 1.4mm 2.4mm; border-radius: 2mm; font-size: 10.5pt; }
.turn b { font-size: 7.5pt; text-transform: uppercase; letter-spacing: 0.05em; margin-right: 1mm; }
.turn.odd { align-self: flex-start; background: #e7f1ff; border-left: 3px solid #1f6fd1; }
.turn.odd b { color: #1f6fd1; }
.turn.martin { align-self: flex-end; background: #fff0e3; border-right: 3px solid #d4660f; }
.turn.martin b { color: #d4660f; }
.turn.both { align-self: center; background: linear-gradient(90deg, #e7f1ff, #fff0e3); border-left: 3px solid #1f6fd1;
  border-right: 3px solid #d4660f; }
.turn.other { background: none; border-color: #d5d8de; color: #6b7280; font-size: 9pt; }
.turn.other b { color: #9aa0aa; }
.click { display: inline-block; font-size: 7.5pt; font-weight: 700; padding: 0 1.2mm; margin: 0 0.6mm; border-radius: 1mm;
  background: #111; color: #ffd84a; vertical-align: 1px; white-space: nowrap; }
.click.dim { background: #c9ccd2; color: #fff; }
.advance { text-align: right; color: #9aa0aa; font-size: 8pt; margin: 0.5mm 0 0; }
.drill { break-inside: avoid; border-bottom: 1px dashed #d5d8de; padding: 1.6mm 0; }
.cue { color: #6b7280; font-size: 8.8pt; }
.cue .sn { display: inline-block; min-width: 6mm; font-weight: 700; color: #1d1f24; }
.cue .newslide { color: #1d1f24; font-weight: 600; }
.cue-who { font-weight: 600; }
.initials { font: 600 11.5pt/1.4 'Menlo', monospace; padding-left: 6mm; letter-spacing: 0.02em; }
.initials.odd { color: #1f6fd1; } .initials.martin { color: #d4660f; }
.cols { columns: 2; column-gap: 5mm; }
.small { font-size: 9pt; }
.check li { list-style: none; margin-left: -4mm; }
.check li::before { content: "☐  "; }
"""


def page(title: str, body: str) -> str:
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{esc(title)}</title><style>{CSS}</style></head>'
            f'<body>{body}</body></html>')


def cover(who_html: str, subtitle: str, extra: str) -> str:
    return (f'<div class="cover"><div><p class="kicker">ScalaDays 2026 · Berlin</p><h1>A Brief History of Scala</h1>'
            f'<p class="big">Monday 12 October, 11:20 · 30 minutes</p></div>'
            f'<div><p class="who">{who_html}</p><p class="big">{subtitle}</p></div><div>{extra}</div></div>')


LEGEND = """<div class="box small"><b>How the script reads.</b> As in the presenter view: Odd's turns on the left in blue,
Martin's on the right in orange; <b>{mine}</b>. <span class="click">{badge}</span> marks a click in the middle of a line.
The slide image shows each slide's final build, every bubble included. Italic lines are stage directions; never
spoken.</div>"""

QA = """
<h2 class="part">Q&amp;A</h2>
<p>About 8½ minutes are left for questions if the talk runs to plan. <b>Martin repeats each question</b> into the mic
(for the room and the recording) and either answers or hands it over: questions about what the compiler does, what it
costs or why the code isn't written another way go to Odd. Keep answers to two or three sentences; offer the repository
for the rest. Leave the thank-you slide (61) up; jump to a reserve slide by typing its number and Enter in the
presenter view, and back with 6 1 Enter.</p>
<h4>Reserve slides: who says what</h4>
{reserve}
<h4>Questions to expect</h4>
<table class="grid qa">
<tr><th>Question</th><th>Who</th><th>Answer in brief</th></tr>
<tr><td>Isn't the +: / :+ extractor slow? (Odd invites it on slide 28)</td><td>Odd</td><td>Yes: on a List the last
element costs a walk, on a String every step copies, so quietly O(n²). Slide 62: the 2007 index loop is ten thousand
times faster; slide 63: slicing without copying makes the pattern linear again.</td></tr>
<tr><td>Can palindromize be linear?</td><td>Odd</td><td>Slide 64: the palindromic tail is the longest suffix that's also
a prefix of the reverse, so KMP finds it in one pass. Fifteen lines of index tables; not what this talk is about.</td></tr>
<tr><td>Is Scala 4.0 real? Are Prolog-style patterns coming?</td><td>Martin</td><td>Made up, for the talk: two
authors, three opinions. Odd's objection on slide 59 is the real answer: which equality would the pattern use?</td></tr>
<tr><td>Why your own Eq and not cats' Eq, or CanEqual?</td><td>Odd</td><td>Every version stands alone, with no
dependencies, back to 2007. CanEqual answers “may this type be compared with == at all?”, not “how?”: the caller
choosing case-insensitive needs a type class.</td></tr>
<tr><td>Why skip 2.6, 2.7, 3.1–3.5 and 3.7–3.9?</td><td>Martin</td><td>They change nothing our code uses. All 19
versions are in the repository, and every one compiles and passes its tests.</td></tr>
<tr><td>How do you even compile Scala 2.5 today?</td><td>Odd</td><td>Not with Mill: no compiler bridge before 2.10.
A script runs each version's own scalac on JDK 8, reading a JDK 7 rt.jar, with a stand-in FunSuite for 2.5 and 2.6.</td></tr>
<tr><td>Couldn't 2.10–2.12 already call methods on a String?</td><td>Odd</td><td>The language could: a String wrapper, or
IsTraversableLike (2.10) / IsSeqLike (2.11). Our code keeps one mechanism per version; that's the “nobody read that
Scaladoc” line on slide 40.</td></tr>
<tr><td>What about opaque types?</td><td>Odd</td><td>Not in the code. Value classes promise no allocation but box in
generic and array contexts (slide 26); opaque types keep the promise.</td></tr>
</table>
"""


ODD_PLAN = """<div class="box"><b>Saturday, at home (out loud)</b>
<ol><li><b>Read-through, 20 min.</b> Go through <i>The script</i> once with the slides. Read {partner}'s lines too:
they're your cues. Note where a line feels unnatural in your mouth.</li>
<li><b>Cue drill, 3 × 10 min.</b> In <i>Cue drill</i>, read the cue, then say your line aloud from its first letters
only. Check it against <i>The script</i> when unsure. Repeat the slides you stumbled on until they're smooth.</li>
<li><b>Full run, standing, 25 min.</b> Your lines in full voice, {partner}'s in a flat voice. Start a timer and
check yourself against the checkpoints below.</li>
<li><b>The signature moments</b> on the previous page, each three times. Practise the pauses: count “one, two”
silently after a joke, and before Odd's concessions.</li>
<li><b>Pack</b>, with the list below. Download these PDFs to the iPad and phone, and open each once.</li></ol></div>
<div class="box"><b>Sunday, on the way to Berlin (offline, quietly)</b>
<ol><li><b>The skeleton, 5 min.</b> From memory, list the versions in order (2.5, 2.8, 2.9, 2.10, 2.11, 2.12, 2.13,
3.0, 3.6, 4.0) and what each brings. If you know the order, you'll never be lost.</li>
<li><b>Cue drill</b>, one pass on first letters only, mouthing the lines; check only the ones you miss.</li>
<li>Read <i>Q&amp;A</i>: the reserve slides and the questions to expect.</li>
<li>Then rest. Lunch, and meet {partner} after it with your voice fresh.</li></ol></div>
<div class="box warn"><b>Packing list</b><ul class="check">
<li>The laptop that presents, its charger, and the deck running with Wi-Fi off (<code>talk/present.py</code>)</li>
<li>USB-C to HDMI adapter (and a spare, if you have one)</li>
<li>The clicker, with a spare battery</li>
<li>iPad and phone, with these PDFs downloaded, and their chargers</li>
<li>What you'll wear on stage; a water bottle</li></ul></div>
"""

MARTIN_PLAN = """<div class="box"><b>Saturday, whenever you find an hour (out loud)</b>
<ol><li><b>Read-through, 20 min.</b> Go through <i>The script</i> once with the slides. Read Odd's lines too: they're
your cues, and your clicks. Note where a line feels unnatural in your mouth.</li>
<li><b>Cue drill, 3 × 10 min.</b> In <i>Cue drill</i>, read the cue, then say your line aloud from its first letters
only. Check it against <i>The script</i> when unsure. Repeat the slides you stumbled on until they're smooth.</li>
<li><b>The skeleton, 5 min.</b> From memory, list the versions in order (2.5, 2.8, 2.9, 2.10, 2.11, 2.12, 2.13,
3.0, 3.6, 4.0) and what each brings. You introduce every one of them.</li></ol>
<p class="small">Short on time? Do the cue drill and skip the rest: ten minutes on a bench works too.</p></div>
<div class="box"><b>Sunday morning, before Odd arrives (about 11:00)</b>
<ol><li><b>Full run, standing, 25 min.</b> Your lines in full voice, Odd's in a flat voice. Start a timer and check
yourself against the checkpoints below. Click on your thumb, or on a pen, at every <span class="click">▶ CLICK</span>:
the clicks are half your part.</li>
<li><b>The signature moments</b> on the previous page, each three times. Practise the pauses: count “one, two”
silently after a joke, and let Odd's concessions land before you answer.</li>
<li>Read <i>Q&amp;A</i>: you repeat every question and decide who answers.</li></ol></div>
<div class="box warn"><b>You're in Berlin already: if you pass the venue</b><ul class="check">
<li>Find the room for Monday 11:20, and how long before the slot you can get in</li>
<li>What the projector takes (HDMI, USB-C), and whether there's a confidence monitor</li>
<li>The microphones: handheld or headset, and who to ask</li>
<li>Where we'd stand: left and right of the screen, with a view of the laptop</li></ul></div>
"""


def reserve_html(slides: list[Slide], me: str | None) -> str:
    return script_html([s for s in slides if s.reserve], me)


def personal(slides, checkpoints, me: str) -> str:
    talk = [s for s in slides if not s.reserve]
    st = stats(slides)
    mine, theirs = st[me], st["MARTIN" if me == "ODD" else "ODD"]
    clicks = sum(s.clicks for s in talk)
    odd_clicks = sum(l.text.count("[click]") for s in talk for l in s.lines if l.who == "ODD")
    name, partner = NAMES[me], NAMES["MARTIN" if me == "ODD" else "ODD"]
    color = me.lower() + "-c"

    if me == "ODD":
        role = """<p><b>Odd, the skeptic.</b> The code reviewer, and the one who knows how it works underneath: what the
compiler inserts, what it costs, where it breaks. Dry, deadpan, counts allocations, remembers every migration. Never
shouts, never sneers: just unimpressed.</p>
<div class="box blue"><b>Your arc: Scala slowly wins you over.</b> Play it; it's the story under the jokes.
<ol><li><b>Slide 36 · 2.12</b>: the first concession. Take a breath before “All right. I concede.”</li>
<li><b>Slide 47 · 3.0</b>: “I'm… almost moved.” Mean it, a little.</li>
<li><b>Slide 55 · 3.6</b>: “I'm running out of things to complain about.”</li>
<li><b>Slide 60 · takeaways</b>: “… I'll give you that one.” The last line before the thank-you; slow, to the room.</li></ol></div>
<h4>Your signature moments</h4>
<ul><li><b>1 · cover</b>: “And I'm Odd.” exactly as Martin said his name: same rhythm, a nod, no pause before
“Odd”. A beat, deadpan, then “That's <i>also</i> my name.”, stressing “also”, so the room hears “I'm odd”. Don't wait
for the laugh.</li>
<li><b>23 · 2.10</b>: a beat before “Alphabetically, that is.”: the room needs a second to see 2.10 sort before 2.9.</li>
<li><b>18 · CanBuildFrom</b>: point at the signature and count its type parameters on your fingers.</li>
<li><b>37 · 2.13</b>: Martin finds your name in the cloud. “I was young and needed the commits.” Then “No comment.”</li>
<li><b>56 · Scala 4.0</b>: deadpan. “Two authors, three opinions.”</li></ul>
<h4>Clicks</h4>
<p>Martin holds the clicker. {odd_clicks} of the talk's {clicks} mid-slide clicks fall inside your lines: at each
<span class="click">◆ nod: Martin clicks</span>, nod or look at Martin (or say “click”). In the cue drill a click in
your line is a ◆.</p>"""
    else:
        role = """<p><b>Martin, the enthusiast.</b> The fan, and the one who wrote the code. Warm, nostalgic, sees the best
in every release, defends the old code like an old car that still starts. You introduce each step and ask what the room
is thinking; you don't explain the machinery. Never sarcastic: enthusiasm is the joke.</p>
<div class="box warn"><b>You hold the clicker.</b> Every click in the talk is yours: {clicks} mid-slide clicks plus
the click to each next slide. {odd_clicks} of them fall inside Odd's lines, marked <span class="click">▶ CLICK on Odd's
cue</span>: watch for Odd's nod or look. Let each morph finish (about 2½ s) before anyone talks over it: the code moving
is the show. Every “again” slide is a two-second bridge: one line, then click.</div>
<h4>Your signature moments</h4>
<ul><li><b>1 · cover</b>: “Hi Berlin!” You open the talk; walk on together, you center-left, Odd right. In the beat
after Odd's “And I'm Odd.”, glance at Odd with mild, fond resignation; don't laugh. Go on once the laugh starts, or
after a second without one.</li>
<li><b>37 · 2.13</b>: find Odd's name in the tag cloud and point at it. A beat after “You weren't that young.”</li>
<li><b>36 · 2.12</b>: Odd's first concession; let Odd breathe, then “Can I get that in writing?”</li>
<li><b>49 · m3-0-clean</b>: the class morphs away and nobody speaks. Let it play before you go on.</li>
<li><b>60 · takeaways</b>: drop the comedy a notch; slower, to the room.</li>
<li><b>61 · thanks</b>: last lines, then “Thank you! Questions?” together; leave the QR code up.</li></ul>
<h4>Odd's arc</h4>
<p>Scala slowly wins Odd over: a first concession at 2.12 (36), “almost moved” at 3.0 (47), and “I'll give you that
one” at the end (60). Your enthusiasm is what Odd gives in to: keep it warm, never smug at a concession.</p>"""
    role = role.format(clicks=clicks, odd_clicks=odd_clicks)

    schedule = ODD_PLAN if me == "ODD" else MARTIN_PLAN
    plan = f"""
<h2 class="part">How to practise before Sunday afternoon</h2>
<p>You have {mine[0]} turns ({mine[1]} words); {partner} has {theirs[0]} ({theirs[1]} words). The dialogue runs about
21½ minutes. The goal for Sunday afternoon is to know your lines and their cues well enough that the rehearsal with
{partner} is about timing and play, not about remembering. The presenter notes will be there on Monday: glance, don't
read.</p>
{schedule.format(partner=partner)}
<div class="box"><b>Monday morning</b><p>One cue-drill pass over breakfast, then leave it. The notes will catch you.</p></div>
<h4>Timing checkpoints</h4>
{checkpoints_html(checkpoints)}
<p class="small">The times assume a relaxed pace and a beat after each joke. Later than a checkpoint: do what the last
column says.</p>
"""
    body = (cover(f'<span class="{color}">{name}</span>\'s practice script',
                  f"Your lines in {'blue' if me == 'ODD' else 'orange'}, with {partner}'s as cues",
                  f'<p class="small">Generated from talk/script.md by talk/prep.py. Slides are the deck 5.18 build.</p>')
            + f'<h2>Your part at a glance</h2>{role}'
            + plan
            + f'<h2 class="part">The script</h2>'
            + LEGEND.format(mine=f"your lines are in colour, {partner}'s greyed as cues",
                            badge="▶ CLICK" if me == "MARTIN" else "◆ nod: Martin clicks")
            + script_html(talk, me)
            + f'<h2 class="part">Cue drill</h2><p>The line before each of yours, in grey, then yours as first letters only '
              f'(◆ is a click). Say your line in full before you look it up in <i>The script</i>. Slide numbers are on the '
              f'left.</p>'
            + drill_html(slides, me)
            + QA.format(reserve=reserve_html(slides, me)))
    return page(f"{name}'s practice script", body)


def together(slides, checkpoints) -> str:
    talk = [s for s in slides if not s.reserve]
    clicks = sum(s.clicks for s in talk)
    odd_click_slides = [s for s in talk if any("[click]" in l.text for l in s.lines if l.who == "ODD")]
    st = stats(slides)
    plan = """
<h2>Sunday afternoon: the rehearsal</h2>
<p>About two and a half hours, in a hotel room or a quiet corner. Bring the laptop, its charger, the clicker, and this
document. Without a projector, put the slides window on the laptop and the presenter view on a phone or iPad
browser, or both on the laptop side by side.</p>
<table class="grid">
<tr><th>Time</th><th>Step</th><th>What it's for</th></tr>
<tr><td>15 min</td><td><b>Set up</b></td><td><code>talk/present.py</code>: presenter view, slides window, clicker paired.
Check that it runs with Wi-Fi off. Agree on the cut rules (below) before anything else.</td></tr>
<tr><td>15 min</td><td><b>Speed run</b></td><td>Lines only, as fast as you can, no acting, no slides. It finds the gaps
in memory, and the cues you don't know yet.</td></tr>
<tr><td>45 min</td><td><b>Blocking run</b></td><td>With slides and clicker, standing as on stage (Martin left with the
clicker, Odd right). Stop anywhere: fix clicks, morph waits, who looks where.</td></tr>
<tr><td>20 min</td><td><b>Hot spots</b></td><td>Each spot on the list below, three times in a row.</td></tr>
<tr><td>10 min</td><td><b>Break</b></td><td></td></tr>
<tr><td>25 min</td><td><b>Dress run</b></td><td>As on Monday: walk on, no stopping, timer on (T in the presenter view).
Note the clock at every checkpoint in the timing sheet.</td></tr>
<tr><td>15 min</td><td><b>Q&amp;A drill</b></td><td>Ask each other the questions to expect; jump to 62–64 and back to 61.</td></tr>
<tr><td>20 min</td><td><b>Second dress run</b></td><td>If the first was over 23 minutes or rough. Otherwise, rest.</td></tr>
</table>
<div class="box"><b>Monday</b><ul>
<li><b>Breakfast</b>: one speed run, 10 minutes. Nothing new after that.</li>
<li><b>At the room, at least 30 minutes early</b> (or in the break before the slot): laptop on the projector, slides
window full screen (F), presenter view on the laptop, clicker range from both stage positions, microphones.</li>
<li><b>Ten minutes before</b>: Do Not Disturb on, notifications and other apps closed, display sleep off, charger
in, slide 1 up, timer reset. Water within reach.</li>
<li><b>Walk on together</b>, Martin center-left, Odd right, arms crossed.</li></ul></div>
<h4>The rules we agree on</h4>
<ul><li><b>Running late</b>: follow the checkpoint table; the one behind the clock decides nothing alone, so agree
now that Martin calls it (a look and “let's move on”).</li>
<li><b>A forgotten line</b>: the other says the gist of it, or the next line. Never correct each other on stage.</li>
<li><b>A long laugh</b>: wait it out. Never talk over a laugh or a morph.</li>
<li><b>A missed click</b>: Odd says “click” with a look, as if it's the running gag.</li>
<li><b>Laptop or projector fails</b>: the deck's artifact on another machine
(claude.ai/artifact/25dnv7jYfipK6R27X8g94t, shared beforehand), and these PDFs on the iPad as a last resort.</li></ul>
<h4>Presenter view keys</h4>
<p class="small">→ or space: next click · ←: back · a number, then Enter: jump to that slide · B: black out the slides ·
T: start or pause the timer · + and −: notes size · F in the slides window: full screen.</p>
"""
    hot = ["<li><b>1 · cover</b>: the walk-on, and “And I'm Odd.” said like Martin's name, a deadpan beat while "
           "Martin glances over, then “That's <i>also</i> my name.” The first ten seconds set the tone.</li>",
           "<li><b>3 · goal</b>: Odd has two turns in a row, with a click at the start of the second.</li>",
           f"<li><b>Clicks on Odd's lines</b> (Martin clicks when Odd nods): slides "
           f"{', '.join(str(s.n) for s in odd_click_slides)}. Run each one until the nod and the click are one move.</li>",
           "<li><b>The “again” slides</b> (14, 16, 21, 25, 27, 31, 35, 39, 43, 45, 52, 54, 58): one line, click, and "
           "silence while the code morphs.</li>",
           "<li><b>23 · 2.10</b>: the beat before “Alphabetically”.</li>",
           "<li><b>36 · 2.12</b>: Odd's first concession; the breath before it, and Martin's timing on “in writing”.</li>",
           "<li><b>37 · 2.13</b>: Martin finds Odd's name and points; the beat after “You weren't that young.”</li>",
           "<li><b>44 · Eq in 3.0</b>: four clicks, alternating speakers.</li>",
           "<li><b>46–49 · the 3.0 methods</b>: palindromize morphs, the class is commented out, gets its bubble, and "
           "morphs away on 49, where nobody speaks.</li>",
           "<li><b>56–59 · Scala 4.0</b>: deadpan, both of you. Let the two names sit.</li>",
           "<li><b>60–61 · the ending</b>: slower, to the room; “I'll give you that one”; “Thank you! Questions?” "
           "together, on the same breath.</li>"]
    body = (cover('<span class="martin-c">Martin</span> &amp; <span class="odd-c">Odd</span>: rehearsing together',
                  "Sunday afternoon in Berlin, and Monday morning",
                  f'<p class="small">{len(talk)} slides, {clicks} mid-slide clicks, about 21½ minutes of dialogue: Martin '
                  f'{st["MARTIN"][0]} turns, Odd {st["ODD"][0]}. Generated from talk/script.md by talk/prep.py.</p>')
            + plan
            + f'<h2 class="part">Hot spots</h2><ul>{"".join(hot)}</ul>'
            + '<h4>Staging</h4><ul><li>Martin stands left of the screen and holds the clicker; Odd stands right.</li>'
              '<li>Glance at the notes, don\'t read them; face the room.</li>'
              '<li>Let every morph finish before talking over it. Pause after a joke; never explain one, never laugh at '
              'your own.</li></ul>'
            + f'<h2 class="part">Timing sheet</h2><p>Write the clock at each slide in every run. The talk is 30 minutes; '
              f'the plan ends at about 21½, leaving 8½ for questions.</p>{timing_sheet_html(slides)}'
              f'<h4>If you\'re behind</h4>{checkpoints_html(checkpoints)}'
            + f'<h2 class="part">Click map</h2><p>Every mid-slide click, and the words it follows. The click to the next '
              f'slide always comes after a slide\'s last line, and isn\'t listed.</p>{click_map_html(slides)}'
            + '<h2 class="part">The script</h2>'
            + LEGEND.format(mine="both in colour", badge="▶ click")
            + script_html(talk, None)
            + QA.format(reserve=reserve_html(slides, None)))
    return page("Rehearsing together", body)


def shrink_images(slides: list[Slide]) -> None:
    if not SHOTS.is_dir():
        sys.exit("talk/prep.py: no screenshots; run talk/render.py --screenshots first")
    IMAGES.mkdir(parents=True, exist_ok=True)
    for s in slides:
        png = SHOTS / f"{s.n:02}-{s.sid}.png"
        if not png.exists():
            sys.exit(f"talk/prep.py: no screenshot {png.name}; rerun talk/render.py --screenshots")
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "70", "--resampleWidth", "960",
                        str(png), "--out", str(image(s))], check=True, capture_output=True)


def pdf(name: str, document: str, profile: Path) -> Path:
    source, target = OUT / f"{name}.html", OUT / f"{name}.pdf"
    source.write_text(document)
    target.unlink(missing_ok=True)
    render.run_chrome(profile, ["--no-pdf-header-footer", f"--print-to-pdf={target}", source.as_uri()],
                      render.screenshot_written(target))
    return target


def main() -> None:
    slides, checkpoints = parse()
    OUT.mkdir(parents=True, exist_ok=True)
    shrink_images(slides)
    with tempfile.TemporaryDirectory() as tmp:
        profile = Path(tmp) / "profile"
        for name, document in (("odd", personal(slides, checkpoints, "ODD")),
                               ("martin", personal(slides, checkpoints, "MARTIN")),
                               ("together", together(slides, checkpoints))):
            print(pdf(name, document, profile).relative_to(ROOT))


if __name__ == "__main__":
    main()
