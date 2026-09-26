#!/usr/bin/env python3
"""Generates the annotated deck in talk/annotated/: the talk deck's framing slides around the code morph, with
handwritten notes in speech bubbles that point at the code they explain.

Usage: talk/annotated.py

The code slides come from talk/morph.py (same states, same token ids, so they morph the same way). Each code slide
gets the notes in NOTES below: a bubble placed next to the code it points at, with a tail ending at an underline
beneath that code. The notes fade in one per click after the morph. The other slides are copied from talk/deck/, so
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
TALK = ROOT / "talk/deck/project"
OUT = ROOT / "talk/annotated/project"

# Code geometry: IBM Plex Mono advances 0.6 em.
SIZE, LH, LEFT, TOP = 24, 36, 128, 200
CW = SIZE * 0.6

# Bubbles: Caveat at 36px; 0.38 em per character is a little over its average advance, so text never overflows.
NOTE_SIZE, NOTE_LH, NOTE_EM = 36, 40, 0.38
PAD_X, PAD_Y, RADIUS, TAIL_BASE = 26, 16, 18, 22
AREA = (134, 182, 1786, 946)  # where bubbles may go: inside the margins, less the outline's 6px padding
BG, FG, INK, PAPER, LINE = "#1B1F2A", "#E8E6DF", "#F3E6D3", "#242A38", "#E3A869"

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

# Per code state: the notes, in the order they appear, and the speaker notes. An anchor is exact code text, first
# occurrence; with ⟨ ⟩ inside it, only the marked part is underlined (the rest is context to find the right place).
NOTES = {
    "2.5": ([
        ("implicit eq: Eq[A]", "equality is a type class,\npassed in implicitly"),
        ("from >= to ||", "no extractors yet:\nwalk an index inward"),
        ("): ⟨Seq[A]⟩ = {", "generic code can only\npromise a Seq"),
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
       "the caveat: on a List, :+ needs init and last, which are O(n), so this is quietly O(n²); a Vector keeps it "
       "linear."),
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
        return "top", (ax, y0), (tx, span[3] + 2)
    if span[1] >= y1:  # bubble above
        return "bottom", (ax, y1), (tx, span[1] - 4)
    # Beside the code: a margin note, pointing at the end of the anchor's line (the underline marks the words).
    ay = min(max((span[1] + span[3]) / 2, y0 + RADIUS + TAIL_BASE / 2), y1 - RADIUS - TAIL_BASE / 2)
    if x0 >= span[4]:
        return "left", (x0, ay), (span[4] + 10, (span[1] + span[3]) / 2)
    return "right", (x1, ay), (span[0] - 6, (span[1] + span[3]) / 2)


def place(note, span, blocked, bubbles, anchor_rects):
    lines = note.split("\n")
    w = round(max(len(l) for l in lines) * NOTE_SIZE * NOTE_EM + 2 * PAD_X)
    h = len(lines) * NOTE_LH + 2 * PAD_Y
    best = None
    for y in range(AREA[1], AREA[3] - h + 1, 8):
        for x in range(AREA[0], AREA[2] - w + 1, 8):
            box = (x, y, x + w, y + h)
            if any(overlaps(box, r, 14) for r in blocked) or any(overlaps(box, b, 28) for b in bubbles):
                continue
            side, base, tip = geometry(box, span)
            length = math.dist(base, tip)
            score = length + (0 if side in ("top", "bottom") else 30)
            if length < 40 or (best is not None and score >= best[0]):
                continue
            points = curve_points(base, tip)[2:-2]
            if any(crosses(points, r) for r in blocked if r not in anchor_rects) or \
                    any(crosses(points, b, 8) for b in bubbles):
                continue
            best = (score, box, side, base, tip)
    if best is None:
        raise SystemExit(f"no room for the note {note!r}")
    return best[1:]


def bubble_svg(box, side, base, tip, span, order):
    """The bubble and its tail as one outline, plus a hand-drawn underline beneath the anchored code."""
    x0, y0, x1, y1 = box
    ux0, ux1, uy = span[0] + 2, span[2] - 2, span[3] - 3
    left, top = math.floor(min(x0, tip[0], ux0)) - 6, math.floor(min(y0, tip[1], uy)) - 6
    right, bottom = math.ceil(max(x1, tip[0], ux1)) + 6, math.ceil(max(y1, tip[1], uy)) + 6
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
    under = f"M{X(ux0)},{Y(uy)} Q{X((ux0 + ux1) / 2)},{Y(uy + 3)} {X(ux1)},{Y(uy - 1)}"
    w, h = right - left, bottom - top
    return (f'<svg aria-label="" data-build-in="fade {order}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'style="position:absolute; left:{left}px; top:{top}px; width:{w}px; height:{h}px">'
            f'<path d="{under}" fill="none" stroke="{LINE}" stroke-width="2.5" stroke-linecap="round" '
            f'stroke-opacity="0.9"/>'
            f'<path d="{d}" fill="{PAPER}" fill-opacity="0.97" stroke="{LINE}" stroke-width="1.75" '
            f'stroke-linejoin="round"/></svg>')


def note_html(box, text, order):
    x0, y0, x1, _ = box
    body = "<br>".join(escape(l) for l in text.split("\n"))
    return (f'<p data-build-in="fade {order}" style="position:absolute; left:{x0 + PAD_X}px; top:{y0 + PAD_Y}px; '
            f"width:{x1 - x0 - 2 * PAD_X}px; font-family:'Caveat', cursive; font-size:{NOTE_SIZE}px; "
            f'font-weight:500; line-height:{NOTE_LH}px; white-space:nowrap; color:{INK}">{body}</p>')


def code_slide(slide_id, state, runs, transition, notes, aside):
    rows = [f'<section id="{slide_id}" data-transition="{transition}" style="background:{BG}; color:{FG}; '
            f"font-family:'IBM Plex Sans', Arial, sans-serif; padding:128px; display:flex; "
            f'flex-direction:column">',
            '<div style="display:flex; flex-direction:row; justify-content:space-between; align-items:baseline; '
            'gap:48px">',
            f'<p style="font-size:24px; font-weight:600; letter-spacing:3px; text-transform:uppercase; '
            f'white-space:nowrap; color:#F2A65A">{escape(morph.label(state["versions"]))}</p>',
            f'<p style="font-size:24px; color:#C9CCD3; text-align:right">{escape(morph.summary(state))}</p>',
            "</div>"]
    rows += morph.code_runs_html(runs, SIZE, LH, CW, LEFT, TOP)
    blocked = code_rects(runs)
    bubbles = []
    for order, (anchor, text) in enumerate(notes, 1):
        span = anchor_span(state["lines"], anchor)
        mine = [r for r in blocked if overlaps(r, span)]
        box, side, base, tip = place(text, span, blocked, bubbles, mine)
        bubbles.append(box)
        rows.append(bubble_svg(box, side, base, tip, span, order))
        rows.append(note_html(box, text, order))
    if aside:
        rows.append(f"<aside>{escape(aside, quote=False)}</aside>")
    rows.append("</section>")
    return "\n".join(rows) + "\n"

# The talk slides are light; in this deck every slide takes the code slides' dark palette.
PANEL, PANEL_EDGE, ADDED, COMMENT = "#242A38", "#343B4C", "#26344C", "#9AA3AF"
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


def restyle(html: str) -> str:
    for old, new in RECOLOR:
        html = html.replace(old, new)
    if "<table style=\"font-family:'IBM Plex Mono'" in html:
        html = collapse_panels(html)
    return re.sub(r"(<div style=\"[^\"]*IBM Plex Mono[^\"]*\">)(.*?)(</div>)",
                  lambda d: d.group(1) + re.sub(r'<p style="([^"]*)">(.*?)</p>', highlight_line, d.group(2),
                                                flags=re.S) + d.group(3), html, flags=re.S)


def build():
    states = morph.load_states()
    runs_per_state = morph.chain(states)
    index = {s["versions"][0]: k for k, s in enumerate(states)}
    assert set(NOTES) == set(index), f"notes for {sorted(NOTES)}, code states {sorted(index)}"

    ids = []
    for item in SEQUENCE:
        if isinstance(item, tuple):
            kind, v = item
            ids.append("m" + v.replace(".", "-") + ("-again" if kind == "again" else ""))
        else:
            ids.append(item)

    OUT.joinpath("slides").mkdir(parents=True, exist_ok=True)
    for old in OUT.joinpath("slides").glob("*.html"):
        old.unlink()
    for n, item in enumerate(SEQUENCE):
        if not isinstance(item, tuple):
            (OUT / f"slides/{item}.html").write_text(restyle((TALK / f"slides/{item}.html").read_text()))
            continue
        kind, v = item
        k = index[v]
        nxt = SEQUENCE[n + 1] if n + 1 < len(SEQUENCE) else None
        morphs = isinstance(nxt, tuple) and index[nxt[1]] == k + 1
        notes, aside = NOTES[v] if kind == "code" else ([], None)
        if kind == "again":
            aside = f"Back to the methods as they stand in {v}, before the next version changes them."
        html = code_slide(ids[n], states[k], runs_per_state[k], "magic" if morphs else "fade", notes, aside)
        (OUT / f"slides/{ids[n]}.html").write_text(html)

    talk = json.loads((TALK / "deck.json").read_text())
    deck = {
        "v": 4,
        "createdOnFiles": {"v": 1, "at": "2026-09-27T12:00:00Z"},
        "title": "A Brief History of Scala, Annotated",
        "order": ids,
        "sections": SECTIONS,
        "faces": {**talk["faces"], "caveat": {
            "family": "Caveat", "href": "https://fonts.googleapis.com/css2?family=Caveat:wght@500&display=swap"}},
    }
    (OUT / "deck.json").write_text(json.dumps(deck, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(ids)} slides, {sum(len(n[0]) for n in NOTES.values())} notes")


if __name__ == "__main__":
    build()
