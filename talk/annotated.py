#!/usr/bin/env python3
"""Generates the annotated deck in talk/3.2-annotated/: the talk deck's framing slides around the code morph, with
handwritten notes in speech bubbles that point at the code they explain.

Usage: talk/annotated.py                 the deck in talk/3.2-annotated/, with the talk's notes
       talk/annotated.py --all-changes   a variant in talk/4.1-annotated-all/, where every change is highlighted and
                                         explained

The code slides come from talk/morph.py (same states, same token ids, so they morph the same way). Each code slide
gets the notes in NOTES below: a bubble placed next to the code it points at, with a tail ending at a highlight
behind that code. The notes fade in one per click after the morph. The other slides are copied from talk/1.2-deck/, so
they stay in step with the talk deck, and restyled on the way: the code slides' dark palette, and their code
highlighted the same way. Where a talk slide interrupts the morph, the code it interrupts is shown again
afterwards, so the next change still morphs.

Bubbles are placed automatically: the position nearest the anchor that overlaps no code and no other bubble, and
whose tail crosses no code but its own. The script fails if a note's anchor isn't in the code, or no place fits.
"""

import json
import math
import re
from html import escape, unescape
from pathlib import Path

import morph

ROOT = Path(__file__).resolve().parent.parent
TALK = ROOT / "talk/1.2-deck/project"
OUT = ROOT / "talk/3.2-annotated/project"
OUT_ALL = ROOT / "talk/4.1-annotated-all/project"  # the every-change variant

# Every code slide looks like the talk deck's code slides: eyebrow, heading, then the code in a panel. One code size
# for the whole deck, the largest at which the tallest code (2.8, 17 lines once wrapped) fits: 24px, line height 1.4.
# The panel starts where the talk slides' flow puts it: 128 + eyebrow 33.6 + gap 36 + heading 70.4 + gap 36.
SIZE, LH = 24, 33.6
PANEL_TOP, PANEL_PAD_X, PANEL_PAD_Y = 304, 44, 36
LEFT, TOP = 128 + 1 + PANEL_PAD_X, PANEL_TOP + 1 + PANEL_PAD_Y  # inside the panel's 1px border and padding
CW = SIZE * 0.6  # IBM Plex Mono advances 0.6 em
MAX_CHARS = int((1664 - 2 - 2 * PANEL_PAD_X) / CW)  # longer lines are wrapped
CODE_STYLE = "font-size:24px; line-height:1.4"

# Bubbles: Fuzzy Bubbles at 26px (it looks as large as a handwriting script at 36); 0.60 em per character is a
# little over its average advance, so text never overflows.
NOTE_SIZE, NOTE_LH, NOTE_EM = 26, 34, 0.60
PAD_X, PAD_Y, RADIUS, TAIL_BASE = 26, 16, 18, 22
# The bubble fill is clearly lighter than the code panel, so a note reads as lying on top of the code; the code a
# note is about gets a soft amber highlight behind it.
BG, FG, INK, PAPER, LINE = "#1B1F2A", "#E8E6DF", "#F3E6D3", "#3A4358", "#E3A869"
HIGHLIGHT = "rgba(227, 168, 105, 0.22)"
PANEL, PANEL_EDGE, ADDED, COMMENT = "#242A38", "#343B4C", "#26344C", "#9AA3AF"

# The slide sequence. ("code", first version) is a code state; ("again", first version) shows it once more without
# notes, after talk slides interrupted the morph; anything else is a talk slide id, copied as it is.
SEQUENCE = [
    "cover", "premise", "timeline", "oneliner",
    "scala2", "s25-types", ("code", "2.5"), ("code", "2.8"), ("code", "2.10"),
    "s210-valueclass", "s212-sam", ("again", "2.10"), ("code", "2.13"),
    "scala3", "s30-collapse", ("again", "2.13"), ("code", "3.0"), ("code", "3.6"),
    "final", "takeaways", "thanks",
]
SECTIONS = {
    "intro": {"description": "One tiny function, and the rule that grows it", "start": "cover"},
    "scala2": {"description": "Scala 2.5 to 2.13: the ideas arrive before the syntax", "start": "scala2"},
    "scala3": {"description": "Scala 3.0 to 3.9: the big collapse, then refinements", "start": "scala3"},
    "closing": {"description": "Where isPalindrome ends up, and what the journey says", "start": "final"},
}

# Per code state: the heading, like the talk slides' (one line at 64px).
TITLES = {
    "2.5": "The whole design with 2007 machinery",
    "2.8": "CanBuildFrom keeps the collection type",
    "2.10": "x +: middle :+ y peels off both ends",
    "2.13": "IsSeq and BuildFrom replace CanBuildFrom",
    "3.0": "The methods, collapsed",
    "3.6": "Context bounds get names",
}

# Per code state: the notes, in the order they appear, and the speaker notes. An anchor is exact code text, first
# occurrence; with ⟨ ⟩ inside it, only the marked part is highlighted (the rest is context to find the right place).
NOTES = {
    "2.5": ([
        ("implicit eq: Eq[A]", "equality: an implicit type class"),
        ("from >= to ||", "no extractors yet:\nwalk two indices inward"),
        ("): ⟨Seq[A]⟩ = {", "generic code can only promise a Seq"),
    ], "The whole design with 2007 machinery. No +: and :+ extractors yet, so it's index arithmetic; the call is in "
       "tail position, even inside || and &&, so scalac already compiles it to a jump, but nothing checks that. "
       "palindromize finds the longest palindromic suffix with our own isPalindrome, so it takes an Eq too, and "
       "mirrors what comes before it. Generic code can't build the same kind of collection, so it returns a Seq: "
       "\"abcb\" gives a Seq[Char], not a String."),
    "2.8": ([
        ("@tailrec", "now the compiler\nchecks the loop"),
        ("SeqLike[A, Repr]", "Repr names the caller's\nconcrete collection"),
        ("CanBuildFrom[Repr, A, Repr]", "a builder for Repr:\nString in, String out"),
    ], "Two changes. @tailrec turns a promise into a check: the generated code is unchanged. And the collections "
       "redesign: SeqLike[A, Repr] names the concrete type, and CanBuildFrom is a factory for builders of it. "
       "bf(xs.repr) gives a builder, and we fill it. Now palindromize(\"abcb\") is the String \"abcba\". Be honest: it "
       "worked, and the signatures scared people."),
    "2.10": ([
        ("x +: middle :+ y", "peel off both ends,\nrecurse on the middle"),
    ], "Talk stage 2. x +: middle :+ y parses as (x +: middle) :+ y: an operator's first character sets its "
       "precedence. With no index to carry, the inner loop goes and @tailrec moves onto isPalindrome itself. Say "
       "the caveat: on a List, :+ needs init and last, which are O(n), and a String copies on every step, so this is "
       "quietly O(n²); a Vector keeps it (effectively) linear."),
    "2.13": ([
        ("IsSeq[Repr] { type A = A0 }", "IsSeq reads any Repr as a Seq;\nthe refinement is the wart"),
        ("bf.newBuilder(xs)", "BuildFrom replaces\nCanBuildFrom"),
    ], "The 2.12 code stops compiling for String: StringOps is no longer a collection, so Repr is inferred as "
       "WrappedString. IsSeq accepts anything readable as a Seq, String included; BuildFrom replaces CanBuildFrom. "
       "The wart: Scala 2 can't mention seq.A in the same parameter list as seq, so the element type becomes an "
       "extra type parameter A0, tied by a refinement."),
    "3.0": ([
        ("using eq: Eq[A]", "implicit becomes using"),
        ("middle.isPalindrome", "an extension is also\nan ordinary method"),
        ("Eq[seq.A]", "a later using clause\ncan depend on seq"),
    ], "The big collapse, on the methods. Braces go; implicit becomes using; object Palindrome and the wrapper "
       "class disappear, because an extension method is an ordinary method too: isPalindrome(xs) and "
       "xs.isPalindrome are the same method. palindromize loses 2.13's refinement and extra type parameter, because "
       "the method's using clause comes after the extension's and can name seq.A."),
    "3.6": ([
        ("A: Eq as eq", "a context bound\nwith a name"),
        ("Repr: IsSeq as seq", "the same for IsSeq;\nseq.A still works"),
    ], "The using clauses fold into the type parameters: a context bound can now be named. The given syntax changes "
       "too, off this slide: given universal: [A] => Eq[A], \"for every A, an Eq[A]\". 3.5 rejects both. 3.7 to 3.9 "
       "change nothing this code uses."),
}


# The every-change variant (--all-changes): from the second code state on, every change gets highlighted and
# explained. A change is its highlighted code (one or more anchors, the note's tail pointing at the first) and one
# note. The build fails if any code that's new in a version lies outside every highlight. The first code state has
# nothing to compare with, so it keeps its NOTES.
CHANGES = {
    "2.8": [
        (["@tailrec"], "now the compiler\nchecks the loop"),
        (["palindromize⟨[A, Repr]⟩", "⟨SeqLike[A, Repr]⟩", "⟨, bf: CanBuildFrom[Repr, A, Repr]⟩", "): ⟨Repr⟩ = {",
          "⟨val elems = xs.toSeq⟩", "(0 to ⟨elems⟩.length)", "isPalindrome(⟨elems⟩.drop"],
         "Repr: the caller's own type,\nwith a builder factory for it;\ntoSeq reads it as a Seq"),
        (["⟨val b = bf(xs.repr)⟩", "⟨b ++= elems⟩", "⟨b ++= elems.take(start).reverse⟩", "⟨b.result⟩"],
         "the input, then its reversed\nprefix: String in, String out"),
    ],
    "2.10": [
        (["⟨case x +: middle :+ y =>⟩", "=> ⟨eq.eqv(x, y)⟩"], "peel off both ends,\ncompare them directly"),
        (["= ⟨xs match⟩ {", "&& ⟨isPalindrome(middle)⟩", "⟨case _ => true⟩"],
         "one match replaces the loop,\nrecursing on the middle"),
    ],
    "2.13": [
        (["palindromize⟨[Repr, A0](xs: Repr)⟩(", "⟨seq: IsSeq[Repr] { type A = A0 }⟩", "val elems = ⟨seq(xs)⟩.toSeq"],
         "any Repr IsSeq can read,\nas seq(xs); A0 and its\nrefinement are the wart"),
        (["eq: Eq[⟨A0⟩]", "⟨BuildFrom[Repr, A0, Repr]⟩", "bf.⟨newBuilder⟩(xs)"],
         "BuildFrom and newBuilder\nreplace CanBuildFrom\nand bf(xs.repr)"),
        (["b.result⟨()⟩"], "2.13 deprecates\nleaving out the ()"),
    ],
    "3.0": [
        (["⟨extension [A](xs: Seq[A])⟩", "⟨(using eq: Eq[A])⟩"],
         "extension and using replace the\nobject, wrapper class and implicit"),
        (["⟨middle.isPalindrome⟩", "drop(i)⟨.isPalindrome⟩"], "an extension is also\nan ordinary method"),
        (["⟨extension [Repr](xs: Repr)(using seq: IsSeq[Repr])⟩", "palindromize⟨(using eq: Eq[seq.A]⟩",
          "BuildFrom[Repr, ⟨seq.A⟩, Repr]"],
         "IsSeq in the extension's using;\nlater clauses see seq.A: no A0"),
    ],
    "3.6": [
        (["[⟨A: Eq as eq⟩]"], "a context bound\nwith a name"),
        (["[⟨Repr: IsSeq as seq⟩]"], "the same for IsSeq;\nseq.A still works"),
    ],
}


def wrap(line: str) -> list[str]:
    """A line too long for the panel, broken where the talk slides break them: after a `)(` between parameter lists,
    else after a `, ` between parameters, rightmost first; continuations are indented 4 more."""
    if len(line) <= MAX_CHARS:
        return [line]
    cuts, between, depth = [], [], 0
    for i, ch in enumerate(line):
        depth += ch in "[{" and 1 or ch in "]}" and -1 or 0
        if line.startswith(")(", i) and depth == 0:
            between.append(i + 2)
        elif line.startswith(", ", i) and depth == 0:
            cuts.append(i + 2)
    fits = [c for c in between if c <= MAX_CHARS] or [c for c in cuts if c <= MAX_CHARS]
    if not fits:
        raise SystemExit(f"can't wrap: {line!r}")
    indent = " " * (len(line) - len(line.lstrip()) + 4)
    return [line[:fits[-1]].rstrip()] + wrap(indent + line[fits[-1]:].lstrip())


def code_rects(runs):
    return [(LEFT + r[0]["col"] * CW, TOP + r[0]["line"] * LH,
             LEFT + (r[-1]["col"] + len(r[-1]["text"])) * CW, TOP + (r[0]["line"] + 1) * LH) for r in runs]


def anchor_span(lines, text):
    """The (x0, y0, x1, y1) box of the first occurrence of text in the code, plus where that line's text ends."""
    context = text.replace("⟨", "").replace("⟩", "")
    offset = text.index("⟨") if "⟨" in text else 0
    marked = text[offset:].split("⟩")[0].lstrip("⟨") if "⟨" in text else text
    for n, line in enumerate(lines):
        c = line.find(context)
        if c >= 0:
            c += offset
            return LEFT + c * CW, TOP + n * LH, LEFT + (c + len(marked)) * CW, TOP + (n + 1) * LH, LEFT + len(line) * CW
    raise SystemExit(f"note anchor not in the code: {text!r}")


def overlaps(a, b, pad=0):
    return a[0] - pad < b[2] and b[0] - pad < a[2] and a[1] - pad < b[3] and b[1] - pad < a[3]


def bend(base, tip):
    """The control point of the tail's centreline: a gentle curve, bowing at most 14px however long the tail."""
    (bx, by), (tx, ty) = base, tip
    length = math.dist(base, tip) or 1
    bow = min(0.18 * length, 14)
    return (bx + tx) / 2 + (ty - by) / length * bow, (by + ty) / 2 - (tx - bx) / length * bow


def curve_points(base, tip):
    """Points along the tail's centreline, every 4px or so."""
    c = bend(base, tip)
    steps = max(2, int(math.dist(base, tip) / 4))
    return [((1 - t) ** 2 * base[0] + 2 * (1 - t) * t * c[0] + t * t * tip[0],
             (1 - t) ** 2 * base[1] + 2 * (1 - t) * t * c[1] + t * t * tip[1])
            for t in (i / steps for i in range(steps + 1))]


def crosses(points, r, pad=4):
    return any(r[0] - pad < x < r[2] + pad and r[1] - pad < y < r[3] + pad for x, y in points)


def geometry(box, span):
    """Where the tail leaves the bubble, where it ends, and on which side."""
    x0, y0, x1, y1 = box
    # Above or below: the tail lands on the anchor where it's closest to the bubble's middle, so it runs steeply.
    tx = min(max((x0 + x1) / 2, span[0] + 12), span[2] - 12)
    ax = min(max(tx, x0 + RADIUS + TAIL_BASE), x1 - RADIUS - TAIL_BASE)
    if span[3] <= y0:  # bubble below the code
        return "top", (ax, y0), (tx, span[3] + 1)
    if span[1] >= y1:  # bubble above
        return "bottom", (ax, y1), (tx, span[1] - 1)
    # Beside the code: a margin note, pointing at the end of the anchor's line (the highlight marks the words).
    ay = min(max((span[1] + span[3]) / 2, y0 + RADIUS + TAIL_BASE / 2), y1 - RADIUS - TAIL_BASE / 2)
    if x0 >= span[4]:
        return "left", (x0, ay), (span[4] + 10, (span[1] + span[3]) / 2)
    return "right", (x1, ay), (span[0] - 6, (span[1] + span[3]) / 2)


def place(note, span, blocked, bubbles, anchor_rects, area, tails=()):
    lines = note.split("\n")
    w = round(max(len(l) for l in lines) * NOTE_SIZE * NOTE_EM + 2 * PAD_X)
    h = len(lines) * NOTE_LH + 2 * PAD_Y
    best = None
    for y in range(area[1], area[3] - h + 1, 8):
        for x in range(area[0], area[2] - w + 1, 8):
            box = (x, y, x + w, y + h)
            if any(overlaps(box, r, 14) for r in blocked) or any(overlaps(box, b, 28) for b in bubbles):
                continue
            side, base, tip = geometry(box, span)
            length = math.dist(base, tip)
            score = length + (0 if side in ("top", "bottom") else 30)
            if length < 16 or (best is not None and score >= best[0]):  # a bubble right above its code needs only a short tail
                continue
            points = curve_points(base, tip)[2:-2]
            if any(crosses(points, r) for r in blocked if r not in anchor_rects) or \
                    any(crosses(points, b, 8) for b in bubbles) or \
                    any(math.dist(p, q) < 12 for t in tails for p in points for q in t):
                continue
            best = (score, box, side, base, tip)
    if best is None:
        return None
    return best


def highlight_html(span, order):
    """A soft highlight behind the code a note is about; it's emitted before the code, so the text stays on top."""
    x0, y0, x1, y1 = span[0] - 5, span[1] + 2, span[2] + 5, span[3] - 2
    return (f'<div data-build-in="fade {order}" style="position:absolute; left:{round(x0, 1)}px; top:{round(y0, 1)}px; '
            f'width:{round(x1 - x0, 1)}px; height:{round(y1 - y0, 1)}px; background:{HIGHLIGHT}; border-radius:6px">'
            f"</div>")


def bubble_svg(box, side, base, tip, span, order):
    """The bubble and its tail as one outline."""
    x0, y0, x1, y1 = box
    left, top = math.floor(min(x0, tip[0])) - 6, math.floor(min(y0, tip[1])) - 6
    right, bottom = math.ceil(max(x1, tip[0])) + 6, math.ceil(max(y1, tip[1])) + 6
    X = lambda v: round(v - left, 1)
    Y = lambda v: round(v - top, 1)
    r, b = RADIUS, TAIL_BASE / 2

    ctrl = bend(base, tip)

    def tail(a, c):
        # A slender tail from a to the tip and back to c, both edges following the centreline's curve.
        (ax, ay), (cx, cy), (tx, ty) = a, c, tip
        c1 = (ctrl[0] + (ax - base[0]) / 2, ctrl[1] + (ay - base[1]) / 2)
        c2 = (ctrl[0] + (cx - base[0]) / 2, ctrl[1] + (cy - base[1]) / 2)
        return (f" L{X(ax)},{Y(ay)} Q{X(c1[0])},{Y(c1[1])} {X(tx)},{Y(ty)}"
                f" Q{X(c2[0])},{Y(c2[1])} {X(cx)},{Y(cy)}")

    bx, by = base
    d = f"M{X(x0 + r)},{Y(y0)}"
    if side == "top":
        d += tail((bx - b, y0), (bx + b, y0))
    d += f" L{X(x1 - r)},{Y(y0)} Q{X(x1)},{Y(y0)} {X(x1)},{Y(y0 + r)}"
    if side == "right":
        d += tail((x1, by - b), (x1, by + b))
    d += f" L{X(x1)},{Y(y1 - r)} Q{X(x1)},{Y(y1)} {X(x1 - r)},{Y(y1)}"
    if side == "bottom":
        d += tail((bx + b, y1), (bx - b, y1))
    d += f" L{X(x0 + r)},{Y(y1)} Q{X(x0)},{Y(y1)} {X(x0)},{Y(y1 - r)}"
    if side == "left":
        d += tail((x0, by + b), (x0, by - b))
    d += f" L{X(x0)},{Y(y0 + r)} Q{X(x0)},{Y(y0)} {X(x0 + r)},{Y(y0)} Z"
    w, h = right - left, bottom - top
    return (f'<svg aria-label="" data-build-in="fade {order}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'style="position:absolute; left:{left}px; top:{top}px; width:{w}px; height:{h}px">'
            f'<path d="{d}" fill="{PAPER}" fill-opacity="0.97" stroke="{LINE}" stroke-width="1.75" '
            f'stroke-linejoin="round"/></svg>')


def note_html(box, text, order):
    x0, y0, x1, _ = box
    body = "<br>".join(escape(l) for l in text.split("\n"))
    return (f'<p data-build-in="fade {order}" style="position:absolute; left:{x0 + PAD_X}px; top:{y0 + PAD_Y}px; '
            f"width:{x1 - x0 - 2 * PAD_X}px; font-family:'Fuzzy Bubbles', 'Trebuchet MS', sans-serif; font-size:{NOTE_SIZE}px; "
            f'font-weight:400; line-height:{NOTE_LH}px; white-space:nowrap; color:{INK}">{body}</p>')


def code_slide(slide_id, state, runs, transition, notes, aside):
    # The panel is pinned, with one id on every code slide, so a morph resizes it instead of fading it.
    height = round(len(state["lines"]) * LH + 2 * PANEL_PAD_Y + 2, 1)
    area = (128 + 18, PANEL_TOP + 18, 1792 - 18, int(PANEL_TOP + height - 18))  # bubbles stay inside the panel
    rows = [f'<section id="{slide_id}" data-transition="{transition}" style="background:{BG}; color:{FG}; '
            f"font-family:'IBM Plex Sans', Arial, sans-serif; padding:128px; display:flex; "
            f'flex-direction:column; gap:36px">',
            f'<div id="code-panel" style="position:absolute; left:128px; top:{PANEL_TOP}px; width:1664px; '
            f'height:{height}px; background:{PANEL}; border:1px solid {PANEL_EDGE}; border-radius:16px"></div>',
            f'<p style="font-size:24px; font-weight:600; letter-spacing:3px; text-transform:uppercase; '
            f'color:#F2A65A">{escape(morph.label(state["versions"]))}</p>',
            f'<h2 style="font-size:64px; font-weight:600; line-height:1.1">{escape(TITLES[state["versions"][0]])}'
            f"</h2>"]
    # Place the notes first: their highlights paint behind the code, their bubbles on top of it.
    blocked = code_rects(runs)
    bubbles, placed = [], []
    # Notes are placed largest first (they still appear in reading order), and a note with several highlights points
    # its tail at whichever one gives the best spot.
    todo = []
    for order, (anchors, text) in enumerate(notes, 1):
        spans = [anchor_span(state["lines"], a) for a in ([anchors] if isinstance(anchors, str) else anchors)]
        todo.append((order, text, spans))
    # If a note finds no room, it moves to the front of the queue and the layout starts over.
    size = lambda text: len(text.split("\n")) * max(len(l) for l in text.split("\n"))
    queue = sorted(todo, key=lambda n: -size(n[1]))
    for attempt in range(len(queue) + 1):
        bubbles, tails, placed, failed = [], [], [], None
        for note in queue:
            order, text, spans = note
            mine = [r for r in blocked if any(overlaps(r, sp) for sp in spans)]
            options = [(o, sp) for sp in spans if (o := place(text, sp, blocked, bubbles, mine, area, tails))]
            if not options:
                failed = note
                break
            (_, box, side, base, tip), span = min(options, key=lambda o: o[0][0])
            bubbles.append(box)
            tails.append(curve_points(base, tip))  # later tails keep clear of this one
            placed.append((order, text, span, box, side, base, tip, spans))
        if not failed:
            break
        queue = [failed] + [n for n in queue if n is not failed]
    else:
        raise SystemExit(f"no room for the note {failed[1]!r}")
    placed.sort(key=lambda p: p[0])
    rows += [highlight_html(sp, p[0]) for p in placed for sp in p[7]]
    rows += morph.code_runs_html(runs, SIZE, LH, CW, LEFT, TOP)
    for order, text, span, box, side, base, tip, _ in placed:
        rows.append(bubble_svg(box, side, base, tip, span, order))
        rows.append(note_html(box, text, order))
    if aside:
        rows.append(f"<aside>{escape(aside, quote=False)}</aside>")
    rows.append("</section>")
    return "\n".join(rows) + "\n"

# The talk slides are light; in this deck every slide takes the code slides' dark palette.
RECOLOR = [
    ("<div style=\"background:#1B1F2A; color:#E8E6DF; font-family:'IBM Plex Mono'",
     f"<div style=\"background:{PANEL}; border:1px solid {PANEL_EDGE}; color:#E8E6DF; font-family:'IBM Plex Mono'"),
    ("background:#F7F5EF", f"background:{BG}"),
    ("background:#B8321F", f"background:{BG}"),
    ("color:#1B1F2A", f"color:{FG}"),
    ("color:#B8321F", "color:#F2A65A"),
    ("color:#4A5160", "color:#C9CCD3"),
    ("background:#FFFFFF; border:1px solid #E2DED3", f"background:{PANEL}; border:1px solid {PANEL_EDGE}"),
    ("background:#2A4468; color:#FFFFFF", f"background:{ADDED}; color:{FG}"),
    ("border-top:3px solid #F7F5EF", "border-top:3px solid #F2A65A"),
    ("text-transform:uppercase; color:#F7F5EF", "text-transform:uppercase; color:#F2A65A"),
]


def highlight(code: str) -> str:
    """Code as HTML, coloured like the code slides; a trailing // comment is grey."""
    out, quoted, cut = [], False, len(code)
    for i, ch in enumerate(code):
        quoted ^= ch == '"'
        if not quoted and code.startswith("//", i):
            cut = i
            break
    for m in morph.TOKEN.finditer(code[:cut]):
        t = m.group()
        if t.isspace():
            out.append("&#160;" * len(t))
        else:
            c = morph.color(t)
            out.append(f'<span style="color:{c}">{escape(t)}</span>' if c else escape(t))
    if cut < len(code):
        out.append(f'<span style="color:{COMMENT}">{escape(code[cut:]).replace(" ", "&#160;")}</span>')
    return "".join(out)


def highlight_line(m) -> str:
    style, inner = m.group(1), m.group(2)
    text = unescape(re.sub(r"<[^>]+>", "", inner)).replace("\xa0", " ")
    # Blank lines, whole-line comments and removed diff lines (dimmed) stay as they are.
    if not text.strip() or text.lstrip().startswith("//") or "color:#8A93A0" in style:
        return m.group(0)
    prefix = ""
    if text.startswith("+ "):
        prefix, text = "+&#160;", text[2:]
    return f'<p style="{style}">{prefix}{highlight(text)}</p>'


def collapse_panels(html: str) -> str:
    """The 2 → 3 table as two highlighted code panels side by side (table cells can't hold coloured spans)."""
    rows = re.findall(r"<tr><td>(.*?)</td><td>(.*?)</td></tr>", html)
    heads = re.findall(r"<th[^>]*>(.*?)</th>", html)
    line = '<p style="font-size:26px; line-height:1.9; white-space:nowrap">{}</p>'
    cols = []
    for head, cells in zip(heads, zip(*rows)):
        cols.append(f'<div style="flex:1; display:flex; flex-direction:column; gap:16px">'
                    f'<p style="font-size:24px; font-weight:600; letter-spacing:3px; text-transform:uppercase; '
                    f'color:#C9CCD3">{head}</p>'
                    f"<div style=\"background:{PANEL}; border:1px solid {PANEL_EDGE}; color:{FG}; font-family:'IBM "
                    f"Plex Mono', 'Courier New', monospace; border-radius:16px; padding:28px 36px; display:flex; "
                    f'flex-direction:column">'
                    + "".join(line.format(highlight(unescape(c))) for c in cells) + "</div></div>")
    table = re.search(r"<table.*?</table>", html, re.S).group(0)
    return html.replace(table, '<div style="display:flex; flex-direction:row; gap:32px">' + "".join(cols) + "</div>")


def uniform_panels(html: str) -> str:
    """Every code panel like the code slides': the same padding, and the same code size and line height."""
    def panel(d):
        opening = re.sub(r"padding:[\d ]+px(?: \d+px)?", f"padding:{PANEL_PAD_Y}px {PANEL_PAD_X}px", d.group(1))
        body = re.sub(r"font-size:\d+px; line-height:[\d.]+", CODE_STYLE, d.group(2))
        return opening + body + d.group(3)
    return re.sub(r"(<div style=\"[^\"]*IBM Plex Mono[^\"]*\">)(.*?)(</div>)", panel, html, flags=re.S)


def restyle(html: str) -> str:
    for old, new in RECOLOR:
        html = html.replace(old, new)
    if "<table style=\"font-family:'IBM Plex Mono'" in html:
        html = collapse_panels(html)
    html = uniform_panels(html)
    return re.sub(r"(<div style=\"[^\"]*IBM Plex Mono[^\"]*\">)(.*?)(</div>)",
                  lambda d: d.group(1) + re.sub(r'<p style="([^"]*)">(.*?)</p>', highlight_line, d.group(2),
                                                flags=re.S) + d.group(3), html, flags=re.S)


def uncovered(state, runs, prev_runs, notes) -> list[str]:
    """New code in this state (tokens the previous state has no counterpart for) outside every highlight."""
    prev_ids = {t["id"] for r in prev_runs for t in r}
    spans = [anchor_span(state["lines"], a) for anchors, _ in notes for a in anchors]
    missing = []
    for t in (t for r in runs for t in r if t["id"] not in prev_ids):
        x0, y = LEFT + t["col"] * CW, TOP + t["line"] * LH
        x1 = x0 + len(t["text"]) * CW
        if not any(sp[0] - 0.5 <= x0 and x1 <= sp[2] + 0.5 and abs(sp[1] - y) < 1 for sp in spans):
            missing.append(f"line {t['line']}: {t['text']!r}")
    return missing


def build(all_changes: bool = False):
    out = OUT_ALL if all_changes else OUT
    states = morph.load_states()
    for s in states:
        s["lines"] = [part for line in s["lines"] for part in wrap(line)]
    runs_per_state = morph.chain(states)
    index = {s["versions"][0]: k for k, s in enumerate(states)}
    assert set(NOTES) == set(index) == set(TITLES), f"notes for {sorted(NOTES)}, code states {sorted(index)}"

    ids = []
    for item in SEQUENCE:
        if isinstance(item, tuple):
            kind, v = item
            ids.append("m" + v.replace(".", "-") + ("-again" if kind == "again" else ""))
        else:
            ids.append(item)

    if all_changes:
        assert set(CHANGES) == set(index) - {states[0]["versions"][0]}, f"changes for {sorted(CHANGES)}"
        for v, changes in CHANGES.items():
            k = index[v]
            missing = uncovered(states[k], runs_per_state[k], runs_per_state[k - 1], changes)
            if missing:
                raise SystemExit(f"{v}: new code without a highlight: " + ", ".join(missing))

    out.joinpath("slides").mkdir(parents=True, exist_ok=True)
    for old in out.joinpath("slides").glob("*.html"):
        old.unlink()
    for n, item in enumerate(SEQUENCE):
        if not isinstance(item, tuple):
            (out / f"slides/{item}.html").write_text(restyle((TALK / f"slides/{item}.html").read_text()))
            continue
        kind, v = item
        k = index[v]
        nxt = SEQUENCE[n + 1] if n + 1 < len(SEQUENCE) else None
        morphs = isinstance(nxt, tuple) and index[nxt[1]] == k + 1
        notes, aside = NOTES[v] if kind == "code" else ([], None)
        if kind == "code" and all_changes and v in CHANGES:
            notes = CHANGES[v]
        if kind == "again":
            aside = f"Back to the methods as they stand in {v}, before the next version changes them."
        html = code_slide(ids[n], states[k], runs_per_state[k], "magic" if morphs else "fade", notes, aside)
        (out / f"slides/{ids[n]}.html").write_text(html)

    talk = json.loads((TALK / "deck.json").read_text())
    deck = {
        "v": 4,
        "createdOnFiles": {"v": 1, "at": "2026-09-27T12:00:00Z"},
        "title": "A Brief History of Scala, Every Change" if all_changes else "A Brief History of Scala, Annotated",
        "order": ids,
        "sections": SECTIONS,
        "faces": {**talk["faces"], "fuzzy-bubbles": {
            "family": "Fuzzy Bubbles",
            "href": "https://fonts.googleapis.com/css2?family=Fuzzy+Bubbles&display=swap"}},
    }
    (out / "deck.json").write_text(json.dumps(deck, indent=2, ensure_ascii=False) + "\n")
    count = sum(len(CHANGES.get(v, NOTES[v][0])) if all_changes else len(NOTES[v][0]) for v in index)
    print(f"{out.parent.name}: {len(ids)} slides, {count} notes")


if __name__ == "__main__":
    import sys
    if sys.argv[1:] not in ([], ["--all-changes"]):
        sys.exit(__doc__)
    build(all_changes=sys.argv[1:] == ["--all-changes"])
