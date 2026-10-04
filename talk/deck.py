#!/usr/bin/env python3
"""Builds the talk's deck in talk/5.12-deck/: hand-written framing slides around generated code slides that morph from
one Scala version to the next, with handwritten-style notes in speech bubbles that point at the code they explain.

Usage: talk/deck.py

The deck holds two kinds of slide. The code slides (ids starting with "m") are generated from the version sources
through talk/morph.py and rewritten on every run; never edit them by hand. Every other slide is hand-written and
edited in place, in the deck's artifact or in its file. The script only normalizes the code panels on those slides:
the same padding and code size as the code slides, and the code coloured the same way (so write their code as plain
text). It writes deck.json's order, sections and faces, keeping its other keys; the order is SEQUENCE below.

Each code slide gets the notes in NOTES: a bubble placed next to the code it points at, with a tail ending at a
highlight behind that code. The notes fade in one per click after the morph. Where a step changes both methods,
isPalindrome morphs first, with its notes, onto a slide that still shows the old palindromize, and palindromize
morphs on the next click. From the second code state on, every
change is highlighted and explained, and the build fails if any code that's new in a version lies outside every
highlight. Where a hand-written slide interrupts the morph, the code it interrupts is shown again afterwards, so the
next change still morphs.

Bubbles are placed automatically: the position nearest the anchor that overlaps no code and no other bubble, and
whose tail crosses no code but its own. The script fails if a note's anchor isn't in the code, or no place fits.
It also fails if a slide in SEQUENCE has no file, or a hand-written slide's file isn't in SEQUENCE.
"""

import json
import math
import re
from html import escape, unescape
from pathlib import Path

import morph

ROOT = Path(__file__).resolve().parent.parent
DECK = ROOT / "talk/5.12-deck/project"
TITLE = "A Brief History of Scala"
FACES = {
    "ibm-plex-sans": {"family": "IBM Plex Sans",
                      "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&display=swap"},
    "ibm-plex-mono": {"family": "IBM Plex Mono",
                      "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&display=swap"},
    "fuzzy-bubbles": {"family": "Fuzzy Bubbles",
                      "href": "https://fonts.googleapis.com/css2?family=Fuzzy+Bubbles&display=swap"},
}

# Every code slide looks like the hand-written slides with code: eyebrow, heading, then the code in a panel.
# One code size for every code slide, the largest at which every bubble still finds room: 25px, line height 1.4. At
# 26px the widest code leaves a note on its first line no side to come from. The reserve slides keep 24px.
# The panel starts below the heading (128 + heading 70.4 + gap 36); the version is on the timeline, not above it.
SIZE = 25
LH = round(SIZE * 1.4, 1)
PANEL_TOP, PANEL_PAD_X, PANEL_PAD_Y = 234, 44, 36
LEFT, TOP = 128 + 1 + PANEL_PAD_X, PANEL_TOP + 1 + PANEL_PAD_Y  # inside the panel's 1px border and padding
CW = SIZE * 0.6  # IBM Plex Mono advances 0.6 em
MAX_CHARS = int((1664 - 2 - 2 * PANEL_PAD_X) / CW)  # longer lines are wrapped
CODE_STYLE = f"font-size:{SIZE}px; line-height:1.4"
# The reserve slides keep the code size they were written for: their code is longer, and only shown in the Q&A.
RESERVE = {"r-indexedseq", "r-stringslice", "r-linear"}
RESERVE_CODE_STYLE = "font-size:24px; line-height:1.4"

# Bubbles: Fuzzy Bubbles at 26px (it looks as large as a handwriting script at 36); 0.60 em per character is a
# little over its average advance, so text never overflows.
NOTE_SIZE, NOTE_LH, NOTE_EM = 26, 34, 0.60
PAD_X, PAD_Y, RADIUS, TAIL_BASE = 26, 16, 18, 22
# The bubble fill is clearly lighter than the code panel, so a note reads as lying on top of the code; the code a
# note is about gets a soft amber highlight behind it.
BG, FG, INK, PAPER, LINE = "#1B1F2A", "#E8E6DF", "#F3E6D3", "#3A4358", "#E3A869"
HIGHLIGHT = "rgba(227, 168, 105, 0.22)"
PANEL, PANEL_EDGE, COMMENT = "#242A38", "#343B4C", "#9AA3AF"

# The slide sequence, one group per Scala version that changes something: ("cloud", v) is that version's slide from
# the tag-cloud deck (who wrote it), then, for each track whose code changes in v (see morph.py: "eq" for Eq, "ops" for
# Scala 2's method syntax, "code" for the methods), the track's previous state shown again without a heading or notes
# (("eq-again", u), ("ops-again", u), ("again", u)), morphing into its state in v. A code slide shows only the methods
# that change in that step. Anything else is a hand-written slide's id.
SEQUENCE = [
    "cover", "oneliner", "goal", "eq",
    ("cloud", "2.5"), "f2-5",
    ("eq", "2.5"), ("ops", "2.5"), ("again", "0"), ("code", "2.5"),
    ("cloud", "2.8"), "f2-8", ("eq-again", "2.5"), ("eq", "2.8"), ("again", "2.5"),
    ("code", "2.8"),
    ("cloud", "2.9"), "f2-9", ("again", "2.8"), ("code", "2.9"),
    ("cloud", "2.10"), "f2-10", ("ops-again", "2.8"), ("ops", "2.10"), ("again", "2.9"), ("code", "2.10"),
    ("cloud", "2.11"), "f2-11", ("ops-again", "2.10"), ("ops", "2.11"),
    ("cloud", "2.12"), "f2-12", ("eq-again", "2.8"), ("eq", "2.12"),
    ("cloud", "2.13"), "f2-13", ("again", "2.10"), ("code", "2.13"),
    ("cloud", "3.0"), "f3-0", ("eq-again", "2.12"), ("eq", "3.0"), ("again", "2.13"), ("code", "3.0"),
    ("cloud", "3.6"), "f3-6", ("eq-again", "3.0"), ("eq", "3.6"), ("again", "3.0"), ("code", "3.6"),
    "cloud4-0", "f4-0", ("again", "3.6"), ("code", "4.0"),
    "takeaways", "thanks",
    "r-indexedseq", "r-stringslice", "r-linear",
]
SECTIONS = {
    "intro": {"description": "One tiny function, and the rule that grows it", "start": "cover"},
    "scala2": {"description": "Scala 2.5 to 2.13: the ideas arrive before the syntax", "start": "tc2-5"},
    "scala3": {"description": "Scala 3.0 to 3.9: the big collapse, then refinements", "start": "tc3-0"},
    "closing": {"description": "Where isPalindrome ends up, and what the journey says", "start": "cloud4-0"},
    "reserve": {"description": "Held back for the Q&A", "start": "r-indexedseq"},
}

# Per code state: the heading, like the hand-written slides' (one line at 64px). A step split in two may give its
# first slide (isPalindrome) a heading of its own, as a pair; its second slide then drops the first's notes.
TITLES = {
    "0": "It starts as a one-liner",
    "2.5": "A better way?",
    "2.8": ("@tailrec", "CanBuildFrom keeps the collection type"),
    "2.9": "tails finds the palindromic suffix",
    "2.10": "+: and :+ extractors",
    "2.13": "IsSeq and BuildFrom",
    "3.0": "using extensions",
    "3.6": "Context bounds get names",
    "4.0": "Prolog extractors",
}

# Per code state: the speaker notes.
ASIDES = {
    "0": "The one-liners from the start of the talk, about to become 2.5's generic methods.",
    "4.0": "Not a real release: an ending joke, and a wish. A pattern that names x twice would only match when both "
           "ends are equal, as unification does in Prolog: the comparison disappears into the pattern. No Scala has "
           "this, and it would have to decide which equality it means; ours is the caller's Eq.",
    "2.5": "The whole design with 2007 machinery. No +: and :+ extractors yet, so it's index arithmetic; the call is "
           "in tail position, even inside || and &&, so scalac already compiles it to a jump, but nothing checks "
           "that. palindromize finds the longest palindromic suffix with our own isPalindrome, so it takes an Eq too, "
           "and mirrors what comes before it. Generic code can't build the same kind of collection, so it returns a "
           "Seq: \"abcb\" gives a Seq[Char], not a String.",
    "2.8": "Two changes. @tailrec turns a promise into a check: the generated code is unchanged. And the collections "
           "redesign: SeqLike[A, Repr] names the concrete type, and CanBuildFrom is a factory for builders of it. "
           "bf(xs.repr) gives a builder, and we fill it. Now palindromize(\"abcb\") is the String \"abcba\". Be "
           "honest: it worked, and the signatures scared people.",
    "2.9": "A library change, not a language one: 2.9 adds tails, every suffix from the whole sequence down to the "
           "empty one. indexWhere returns the first that's a palindrome, which is where the mirrored part starts. "
           "Same search, same order and cost as 2.8's (0 to n).find(...).get, without the index arithmetic or the "
           ".get. 2.10 to 3.9 keep it.",
    "2.10": "Talk stage 2. x +: middle :+ y parses as (x +: middle) :+ y: an operator's first character sets its "
            "precedence. With no index to carry, the inner loop goes and @tailrec moves onto isPalindrome itself. Say "
            "the caveat: on a List, :+ needs init and last, which are O(n), and a String copies on every step, so "
            "this is quietly O(n²); a Vector keeps it (effectively) linear.",
    "2.13": "The 2.12 code stops compiling for String: StringOps is no longer a collection, so Repr is inferred as "
            "WrappedString. IsSeq accepts anything readable as a Seq, String included; BuildFrom replaces "
            "CanBuildFrom. The wart: Scala 2 can't mention isSeq.A in the same parameter list as isSeq, so the element "
            "type becomes an extra type parameter A0, tied by a refinement.",
    "3.0": "The big collapse, on the methods. Braces go; implicit becomes a context bound and using; object "
           "Palindrome and the wrapper class disappear, because an extension method is an ordinary method too: "
           "isPalindrome(xs) and xs.isPalindrome are the same method. x === y is Eq's own extension, found because "
           "the context bound's Eq is a given in scope: no name for it, no second wrapper. palindromize loses 2.13's "
           "refinement and extra type parameter, because the method's using clause comes after the extension's and "
           "can name isSeq.A.",
    "3.6": "palindromize's using clause folds into the type parameter: a context bound can now be named, and isSeq.A "
           "still works. isPalindrome needs no name for its Eq, so it doesn't change. The given syntax changes too, "
           "on the Eq slide: given universal: [A] => Eq[A], \"for every A, an Eq[A]\". 3.5 rejects both. 3.7 to 3.9 "
           "change nothing this code uses.",
}

# Per code state: the notes, in the order they appear. A note is its highlighted code (one or more anchors, the
# tail pointing at the first) and its text. An anchor is exact code text, first occurrence; with ⟨ ⟩ inside it,
# only the marked part is highlighted (the rest is context to find the right place). From the second code state
# on, the notes cover every change: the build fails if any code that's new in a version lies outside every
# highlight. The first code state has nothing to compare with, so its notes pick the main points.
NOTES = {
    "2.5": [
        ("from >= to ||", "walk two indices inward"),
        ("): ⟨Seq[A]⟩ = {", "generic code can only promise a Seq"),
    ],
    "2.8": [
        (["@tailrec"], "now the compiler\nchecks the loop"),
        (["palindromize⟨[A, Repr]⟩", "⟨SeqLike[A, Repr]⟩", "⟨, bf: CanBuildFrom[Repr, A, Repr]⟩", "): ⟨Repr⟩ = {",
          "⟨val seq = xs.toSeq⟩", "(0 to ⟨seq⟩.length)", "isPalindrome(⟨seq⟩.drop"],
         "Repr: the caller's own type,\nwith a builder factory for it;\ntoSeq reads it as a Seq"),
        (["⟨(bf(xs.repr) ++= seq ++= seq.take(start).reverseIterator).result⟩"],
         "the input, then\nits reversed prefix:\nString in, String out"),
    ],
    "2.9": [
        (["seq.⟨tails.indexWhere(isPalindrome(_))⟩"], "every suffix in turn; the first\npalindrome is where to\nstart mirroring"),
    ],
    "2.10": [
        (["⟨case x +: middle :+ y =>⟩", "=> ⟨eq.eqv(x, y)⟩"], "peel off both ends,\ncompare them directly"),
        (["= ⟨xs match⟩ {", "&& ⟨isPalindrome(middle)⟩", "⟨case _ => true⟩"],
         "one match replaces the loop,\nrecursing on the middle"),
    ],
    "2.13": [
        (["palindromize⟨[Repr, A0](xs: Repr)⟩(", "⟨isSeq: IsSeq[Repr] { type A = A0 }⟩", "val seq = ⟨isSeq(xs)⟩.toSeq"],
         "any Repr IsSeq can read, as isSeq(xs);\nA0 and its refinement are the wart"),
        (["eq: Eq[⟨A0⟩]", "⟨BuildFrom[Repr, A0, Repr]⟩", "⟨bf.fromSpecific(xs)(seq.iterator ++⟩ seq"],
         "BuildFrom replaces\nCanBuildFrom; fromSpecific\nbuilds in one call"),
    ],
    "3.0": [
        (["⟨extension [A: Eq](xs: Seq[A])⟩"],
         "extension and a context bound replace\nthe object, wrapper class and implicit"),
        (["=> ⟨x === y⟩", "⟨middle.isPalindrome⟩", "indexWhere(⟨_.isPalindrome⟩)"],
         "=== and isPalindrome:\nextensions, called\nlike methods"),
        (["⟨extension [Repr](xs: Repr)(using isSeq: IsSeq[Repr])⟩", "palindromize⟨(using eq: Eq[isSeq.A]⟩",
          "BuildFrom[Repr, ⟨isSeq.A⟩, Repr]"],
         "IsSeq in the extension's\nusing; later clauses\nsee isSeq.A: no A0"),
    ],
    "3.6": [
        (["[⟨Repr: IsSeq as isSeq⟩]"], "a context bound with\na name: isSeq.A still works"),
    ],
    "0": [],
    "4.0": [
        (["middle :+ ⟨x⟩ =>"], "x twice: both ends\nmust be the same"),
    ],
}


# The Eq track: headings, speaker notes and notes per state, as for the methods above.
EQ_TITLES = {
    "2.5": "Equality is a type class",
    "2.8": "Char gets toLower",
    "2.12": "SAM conversion: lambdas implement traits",
    "3.0": "given and placeholder lambdas",
    "3.6": "The new given syntax",
}
EQ_ASIDES = {
    "2.5": "Stage 3, already in 2.5. Universal == is hardwired, so equality becomes a type class: the default instance "
           "lives in Eq's companion and is found through the implicit scope. Eq.caseInsensitive is an opt-in val you "
           "pass explicitly or put in scope as an implicit. No lambdas can implement a trait yet, hence the anonymous "
           "classes.",
    "2.8": "A library change: the 2.8 collections redesign comes with a richer Char, and toLower replaces "
           "Character.toLowerCase. Eq itself doesn't change.",
    "2.12": "SAM conversion: a lambda can implement any trait with a single abstract method, so the two anonymous "
            "classes shrink to one line each. A good moment for the old-ways speaker to concede one. Nothing else "
            "about Eq changes until Scala 3.",
    "3.0": "The big collapse reaches Eq: braces give way to indentation, implicit def becomes given, and the lambdas "
           "shrink to placeholders, _ == _. caseInsensitive stays a plain val: it's opt-in, so it isn't a given. The "
           "trait gains ===, an extension: wherever an Eq[A] is a given in scope, x === y calls its eqv. eqv stays "
           "the single abstract method, so the lambdas still implement Eq.",
    "3.6": "The new given syntax: given universal: [A] => Eq[A] reads as \"for every A, an Eq[A]\". 3.5 rejects it. "
           "3.7 to 3.9 change nothing here.",
}
EQ_NOTES = {
    "2.5": [
        (["⟨implicit def universal[A]⟩"], "the default, found in\nEq's implicit scope"),
        (["⟨val caseInsensitive⟩"], "opt-in: pass it, or\nput it in scope"),
        (["Eq[A] = ⟨new Eq[A] {⟩"], "each instance is an\nanonymous class"),
    ],
    "2.8": [
        (["= ⟨x.toLower == y.toLower⟩"], "the 2.8 library\nadds toLower to Char"),
    ],
    "2.12": [
        (["Eq[A] = ⟨(x, y) => x == y⟩", "Eq[Char] = ⟨(x, y) => x.toLower == y.toLower⟩"],
         "a lambda implements\na one-method trait"),
    ],
    "3.0": [
        (["trait Eq[A]⟨:⟩", "object Eq⟨:⟩"], "braces give way\nto indentation"),
        (["⟨given⟩ universal"], "given replaces\nimplicit def"),
        (["⟨extension (x: A) def ===(y: A): Boolean = eqv(x, y)⟩"], "x === y, wherever an\nEq[A] is a given in scope"),
        (["Eq[A] = ⟨_ == _⟩", "Eq[Char] = ⟨_.toLower == _.toLower⟩"], "placeholder lambdas"),
    ],
    "3.6": [
        (["given universal⟨: [A] =>⟩ Eq[A]"], "for every A, an Eq[A]"),
    ],
}

# The method-syntax track (Scala 2 only; Scala 3's extensions are on the code slides).
OPS_TITLES = {
    "2.5": "Method syntax through an implicit conversion",
    "2.8": "CanBuildFrom",
    "2.10": "Implicit value classes",
    "2.11": "Value classes may hide their field",
    "2.13": "IsSeq and BuildFrom",
}
OPS_ASIDES = {
    "2.5": "Stage 6, already in 2.5: method syntax without changing Seq. PalindromeOps is an ordinary wrapper class "
           "that holds the Seq and forwards to the functions in object Palindrome. The implicit def is the trick: "
           "when the compiler finds no isPalindrome on a Seq, it looks for an implicit conversion in scope to a type "
           "that has one, and rewrites xs.isPalindrome to palindromeOps(xs).isPalindrome. The Eq still arrives as an "
           "implicit, now on the method. Costs: a wrapper object on every call, and one implicit conversion only: "
           "views don't chain, so a String, which first has to become a Seq, can't use it until 2.13; earlier "
           "versions write isPalindrome(\"racecar\") or \"racecar\".toList.isPalindrome.",
    "2.8": "For xs.palindromize to return the caller's type, the wrapper has to know it: it now wraps a "
           "SeqLike[A, Repr] and asks for the CanBuildFrom too, and isPalindrome passes the collection on as a Seq "
           "with toSeq.",
    "2.10": "Talk stage 6, first step. The class and the conversion become one implicit class, and extends AnyVal "
            "makes it a value class, which usually needs no wrapper object at all. 2.10 insists the value class's "
            "field is public: it rejects private val with \"value class needs to have a publicly accessible val "
            "parameter\".",
    "2.11": "2.11 relaxes that, so the wrapped collection no longer leaks as a public member of every Seq. Strings "
            "still can't use method syntax up to 2.12: implicit views don't chain (String to WrappedString to "
            "PalindromeOps).",
    "2.13": "The 2.13 collections: String is no longer a collection, so the wrapper is rebuilt on IsSeq, following "
            "the pattern the 2.13 documentation gives. An implicit def again, from any Repr with an IsSeq; the "
            "singleton type seq.type keeps seq.A known at the call site. It's no longer a value class (it holds xs "
            "and seq), and it needs import scala.language.implicitConversions. The payoff: the conversion starts from "
            "String itself, so \"racecar\".isPalindrome finally works in Scala 2.",
}
OPS_NOTES = {
    "2.5": [
        (["⟨class PalindromeOps[A](xs: Seq[A])⟩"], "a wrapper that\nforwards"),
        (["⟨implicit def palindromeOps⟩"], "the conversion\nthe compiler adds"),
    ],
    "2.8": [
        (["PalindromeOps⟨[A, Repr](xs: SeqLike[A, Repr])⟩", "isPalindrome(xs⟨.toSeq⟩)",
          "⟨, bf: CanBuildFrom[Repr, A, Repr]): Repr⟩", "palindromeOps⟨[A, Repr](xs: SeqLike[A, Repr])⟩",
          ": PalindromeOps⟨[A, Repr]⟩ ="],
         "Repr travels along"),
    ],
    "2.10": [
        (["⟨implicit class⟩", "(⟨val⟩ xs", "⟨extends AnyVal⟩"], "implicit value class"),
    ],
    "2.11": [
        (["(⟨private⟩ val xs"], "may be private"),
    ],
    "2.13": [
        (["PalindromeOps⟨[Repr, S <: IsSeq[Repr]](xs: Repr, seq: S) {⟩", "Eq[⟨seq.A⟩]): Boolean", "isPalindrome(⟨seq(xs)⟩",
          "Eq[⟨seq.A⟩], bf", "bf: ⟨BuildFrom[Repr, seq.A, Repr]⟩", "Palindrome⟨.palindromize[Repr, seq.A](xs)(seq: seq.type, eq, bf)⟩"],
         "built on IsSeq, which\nreads any Repr as a Seq"),
        (["⟨implicit def palindromeOps[Repr](xs: Repr)(⟩", "⟨implicit seq: IsSeq[Repr])⟩:", "⟨: PalindromeOps[Repr, seq.type] =⟩",
          "⟨new PalindromeOps(xs, seq)⟩"],
         "from String itself:\nno chain of views"),
    ],
}


def wrap(line: str) -> list[str]:
    """A line too long for the panel, broken where the hand-written slides break them: after a `)(` between parameter
    lists, else after the ` = ` that starts a definition's body, else after a `, ` between parameters, rightmost
    first; continuations are indented 4 more."""
    if len(line) <= MAX_CHARS:
        return [line]
    cuts, between, body, depth = [], [], [], 0
    for i, ch in enumerate(line):
        depth += ch in "[{" and 1 or ch in "]}" and -1 or 0
        if line.startswith(")(", i) and depth == 0:
            between.append(i + 2)
        elif line.startswith(" = ", i) and depth == 0:
            body.append(i + 3)
        elif line.startswith(", ", i) and depth == 0:
            cuts.append(i + 2)
    fits = [c for c in between if c <= MAX_CHARS] or [c for c in body if c <= MAX_CHARS] or \
        [c for c in cuts if c <= MAX_CHARS]
    if not fits:
        raise SystemExit(f"can't wrap: {line!r}")
    indent = " " * (len(line) - len(line.lstrip()) + 4)
    return [line[:fits[-1]].rstrip()] + wrap(indent + line[fits[-1]:].lstrip())


def code_rects(runs, top=TOP):
    return [(LEFT + r[0]["col"] * CW, top + r[0]["line"] * LH,
             LEFT + (r[-1]["col"] + len(r[-1]["text"])) * CW, top + (r[0]["line"] + 1) * LH) for r in runs]


def anchor_span(lines, text, top=TOP):
    """The (x0, y0, x1, y1) box of the first occurrence of text in the code, plus where that line's text ends."""
    context = text.replace("⟨", "").replace("⟩", "")
    offset = text.index("⟨") if "⟨" in text else 0
    marked = text[offset:].split("⟩")[0].lstrip("⟨") if "⟨" in text else text
    for n, line in enumerate(lines):
        c = line.find(context)
        if c >= 0:
            c += offset
            return LEFT + c * CW, top + n * LH, LEFT + (c + len(marked)) * CW, top + (n + 1) * LH, LEFT + len(line) * CW
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


def built(order, id_=None) -> str:
    """The attributes of a note's element: its id, if it keeps its place across a morph, and the click it fades in on
    (none: it's there from the start)."""
    return (f' id="{id_}"' if id_ else "") + (f' data-build-in="fade {order}"' if order else "")


def highlight_html(span, order, id_=None):
    """A soft highlight behind the code a note is about; it's emitted before the code, so the text stays on top."""
    x0, y0, x1, y1 = span[0] - 5, span[1] + 2, span[2] + 5, span[3] - 2
    return (f'<div{built(order, id_)} style="position:absolute; left:{round(x0, 1)}px; top:{round(y0, 1)}px; '
            f'width:{round(x1 - x0, 1)}px; height:{round(y1 - y0, 1)}px; background:{HIGHLIGHT}; border-radius:6px">'
            f"</div>")


def bubble_svg(box, side, base, tip, span, order, id_=None):
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
    return (f'<svg aria-label=""{built(order, id_)} width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'style="position:absolute; left:{left}px; top:{top}px; width:{w}px; height:{h}px">'
            f'<path d="{d}" fill="{PAPER}" fill-opacity="0.97" stroke="{LINE}" stroke-width="1.75" '
            f'stroke-linejoin="round"/></svg>')


def note_html(box, text, order, id_=None):
    x0, y0, x1, _ = box
    body = "<br>".join(escape(l) for l in text.split("\n"))
    return (f'<p{built(order, id_)} style="position:absolute; left:{x0 + PAD_X}px; top:{y0 + PAD_Y}px; '
            f"width:{x1 - x0 - 2 * PAD_X}px; font-family:'Fuzzy Bubbles', 'Trebuchet MS', sans-serif; font-size:{NOTE_SIZE}px; "
            f'font-weight:400; line-height:{NOTE_LH}px; white-space:nowrap; color:{INK}">{body}</p>')


def code_slide(slide_id, state, runs, transition, notes, aside, title, prefix="t", only=None, shown=(), keep=None,
               layout=None):
    """A code slide. Its panel holds exactly its code: the bubbles go wherever on the slide they fit, clear of the
    heading, the code and the timeline. A step split in two (isPalindrome first, then palindromize) shows the notes
    numbered `only` (1-based, all if None) on its first slide; on its second, those (`shown`) are there from the
    start, at their places on the first (`keep`) where the code leaves them room, and with ids, so they stay put
    through the morph. `layout`, if given, receives each note's placement."""
    # The panel is pinned, with one id on every code slide, so a morph resizes it instead of fading it.
    height = round(len(state["lines"]) * LH + 2 * PANEL_PAD_Y + 2, 1)
    top = TOP
    area = (128 + 6, 128, 1792 - 6, 952)  # inside the margins and above the timeline, less a bubble's 6px outline
    rows = [f'<section id="{slide_id}" data-transition="{transition}" style="background:{BG}; color:{FG}; '
            f"font-family:'IBM Plex Sans', Arial, sans-serif; padding:128px; display:flex; "
            f'flex-direction:column; gap:36px">',
            f'<div id="code-panel" style="position:absolute; left:128px; top:{PANEL_TOP}px; width:1664px; '
            f'height:{height}px; background:{PANEL}; border:1px solid {PANEL_EDGE}; border-radius:16px"></div>',
]
    if title:  # a state shown again has no heading: the next slide's heading names what changes
        rows.append(f'<h2 style="font-size:64px; font-weight:600; line-height:1.1">{escape(title)}</h2>')
    # Place the notes first: their highlights paint behind the code, their bubbles on top of it.
    blocked = code_rects(runs, top)
    if title:  # keep clear of the heading too (IBM Plex Sans semibold: about 0.6 em per character)
        blocked.append((128, 128, 128 + len(title) * 64 * 0.6, 128 + 71))
    bubbles, placed = [], []
    # Notes are placed largest first (they still appear in reading order), and a note with several highlights points
    # its tail at whichever one gives the best spot.
    todo = []
    for order, (anchors, text) in enumerate(notes, 1):
        if only is not None and order not in only:
            continue
        spans = [anchor_span(state["lines"], a, top) for a in ([anchors] if isinstance(anchors, str) else anchors)]
        todo.append((order, text, spans))
    # If a note finds no room, it moves to the front of the queue and the layout starts over.
    size = lambda text: len(text.split("\n")) * max(len(l) for l in text.split("\n"))
    queue = sorted(todo, key=lambda n: -size(n[1]))
    # Notes kept from the step's first slide are placed first, where they were, unless the code is in the way now.
    kept = [(n, keep[n[0]]) for n in queue if keep and n[0] in keep and
            not any(overlaps(keep[n[0]][0], r) for r in blocked)]
    queue = [n for n in queue if n not in [k[0] for k in kept]]
    for attempt in range(len(queue) + 1):
        bubbles, tails, placed, failed = [], [], [], None
        for (order, text, spans), (box, side, base, tip, span) in kept:
            bubbles.append(box)
            tails.append(curve_points(base, tip))
            placed.append((order, text, span, box, side, base, tip, spans))
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
    if layout is not None:
        layout.update({p[0]: (p[3], p[4], p[5], p[6], p[2]) for p in placed})
    # The click each note fades in on: those shown from the start take none.
    click = {n: i for i, n in enumerate((p[0] for p in placed if p[0] not in shown), 1)}
    split = only is not None or shown
    nid = lambda n, part: f"{prefix}n{n}{part}" if split else None
    rows += [highlight_html(sp, click.get(p[0]), nid(p[0], f"h{j}")) for p in placed for j, sp in enumerate(p[7])]
    rows += morph.code_runs_html(runs, SIZE, LH, CW, LEFT, top, prefix)
    for order, text, span, box, side, base, tip, _ in placed:
        rows.append(bubble_svg(box, side, base, tip, span, click.get(order), nid(order, "b")))
        rows.append(note_html(box, text, click.get(order), nid(order, "t")))
    if aside:
        rows.append(f"<aside>{escape(aside, quote=False)}</aside>")
    rows.append("</section>")
    return "\n".join(rows) + "\n"



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


def uniform_panels(html: str, style: str = CODE_STYLE) -> str:
    """Every code panel like the code slides': the same padding, and the same code size and line height (`style`)."""
    def panel(d):
        opening = re.sub(r"padding:[\d ]+px(?: \d+px)?", f"padding:{PANEL_PAD_Y}px {PANEL_PAD_X}px", d.group(1))
        body = re.sub(r"font-size:\d+px; line-height:[\d.]+", style, d.group(2))
        return opening + body + d.group(3)
    return re.sub(r"(<div style=\"[^\"]*IBM Plex Mono[^\"]*\">)(.*?)(</div>)", panel, html, flags=re.S)


def normalize(html: str, style: str = CODE_STYLE) -> str:
    """A hand-written slide's code panels like the code slides': uniform_panels, and each code line coloured by
    highlight_line. Both only depend on the text, so running this again changes nothing."""
    html = uniform_panels(html, style)
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


# Per track: the slide id prefix, the code token id prefix, and the headings, speaker notes and notes per state.
TRACKS = {
    "code": {"slide": "m", "token": "t", "titles": TITLES, "asides": ASIDES, "notes": NOTES,
             "again": "Back to the methods as they stand in {v}, before the next version changes them."},
    "eq": {"slide": "e", "token": "e", "titles": EQ_TITLES, "asides": EQ_ASIDES, "notes": EQ_NOTES,
           "again": "Back to Eq as it stands in {v}, before the next version changes it."},
    "ops": {"slide": "o", "token": "o", "titles": OPS_TITLES, "asides": OPS_ASIDES, "notes": OPS_NOTES,
            "again": "Back to the method syntax as it stands in {v}, before the next version changes it."},
}
GENERATED = re.compile(r"^(m|e|o|tc)\d")  # generated slide ids: m2-5, m2-8-is, e2-12-again, o2-10, tc2-8, ...
CLOUDS = ROOT / "talk/tag-cloud/project/slides"  # the tag-cloud deck's slides, one per release (s2-8.html, ...)


def _tag_cloud():
    """talk/tag-cloud.py, for its timeline footer (its file name isn't a module name)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("tag_cloud", ROOT / "talk/tag-cloud.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TAG_CLOUD = _tag_cloud()
RELEASES = [d[1:].replace("_", ".") for d in morph.VERSIONS] + ["4.0"]  # the timeline: 2.5 to 3.9, and 4.0


def footer(version: str | None) -> list[str]:
    """The tag-cloud deck's timeline along the bottom, the slide's version marked in amber (none marked if None)."""
    return TAG_CLOUD.timeline(RELEASES, version)


def with_footer(html: str, version: str | None) -> str:
    """A hand-written slide with the timeline as its last pinned elements, before the speaker notes; a footer from an
    earlier build is replaced."""
    lines = [l for l in html.split("\n") if "data-bleed=" not in l]
    at = next(i for i in range(len(lines) - 1, -1, -1) if lines[i].startswith(("<aside", "</section")))
    return "\n".join(lines[:at] + footer(version) + lines[at:])


# Hand-written slides that belong to a version, for the timeline's amber mark ("New in" slides, f2-8 and so on, are
# marked by their id).
HAND_VERSIONS = {"cloud4-0": "4.0"}


def leaving(n: int, default: str | None = "fade") -> str | None:
    """How slide n of SEQUENCE leaves: at once when the next slide shows a state again (it then morphs on), else the
    default."""
    nxt = SEQUENCE[n + 1] if n + 1 < len(SEQUENCE) else None
    leads_to_again = isinstance(nxt, tuple) and nxt[0] != "cloud" and track_of(nxt[0])[1]
    return "none" if leads_to_again else default


# Code states that come from no version directory: the one-liner the talk starts from (slide 2), morphed into 2.5's
# methods; and an imagined Scala 4.0, the ending joke: 3.6's isPalindrome with a Prolog-style pattern that names x
# twice, so the two ends must be equal. No real Scala compiles it.
ONE_LINER = {"dir": None, "versions": ["0"], "lines": [
    "def isPalindrome(s: String): Boolean = s == s.reverse", "", "def palindromize(s: String): String = s + s.reverse"]}
PROLOG = ("case x +: middle :+ y => x === y && middle.isPalindrome", "case x +: middle :+ x => middle.isPalindrome")

def code_states() -> list[dict]:
    states = morph.load_states("code")
    lines = [line.replace(*PROLOG) for line in states[-1]["lines"]]
    assert lines != states[-1]["lines"], "3.6's match case changed: update PROLOG"
    return [ONE_LINER] + states + [{"dir": None, "versions": ["4.0"], "lines": lines}]


def track_of(kind: str) -> tuple[str, bool]:
    """A sequence item's track, and whether it shows a state again."""
    if kind in ("code", "again"):
        return "code", kind == "again"
    track, _, again = kind.partition("-")
    return track, again == "again"


def blocks(lines: list[str]) -> list[list[str]]:
    """The methods of a code state: its blocks between blank lines (isPalindrome, then palindromize)."""
    out, cur = [], []
    for line in lines + [""]:
        if line.strip():
            cur.append(line)
        elif cur:
            out.append(cur)
            cur = []
    return out


def definitions(lines: list[str]) -> list[list[str]]:
    """The top-level definitions of an Eq state (trait Eq, then object Eq): a definition starts at column 0, after a
    blank line."""
    out = [[]]
    for n, line in enumerate(lines):
        if n and line[:1].isalpha() and not lines[n - 1].strip():
            out[-1].pop()  # the blank line between them; join puts it back
            out.append([])
        out[-1].append(line)
    return out


def join(parts: list[list[str]]) -> list[str]:
    return [line for i, part in enumerate(parts) for line in ([""] if i else []) + part]


def views(track: str, states: list[dict], k: int) -> tuple[dict | None, dict | None, dict]:
    """What the slides of the step into state k show: the previous state shown again (None for a track's first state),
    a state between them (None unless both methods change: the new isPalindrome next to the old palindromize, so
    isPalindrome morphs first), and state k. On the code and Eq tracks only the methods or definitions that change
    in this step are shown, on every slide."""
    after, before, between = states[k], states[k - 1] if k else None, None
    if track == "eq" and before:  # only the definitions that change: object Eq, and trait Eq where it changes
        a, b = definitions(after["lines"]), definitions(before["lines"])
        keep = [i for i in range(len(a)) if a[i] != b[i]]
        after = {**after, "lines": join([a[i] for i in keep])}
        before = {**before, "lines": join([b[i] for i in keep])}
    if track == "code" and before:
        a, b = blocks(after["lines"]), blocks(before["lines"])
        keep = [i for i in range(len(a)) if a[i] != b[i]]
        if len(keep) == 2:
            between = {**after, "lines": join([a[0], b[1]])}
        after = {**after, "lines": join([a[i] for i in keep])}
        before = {**before, "lines": join([b[i] for i in keep])}
    wrapped = lambda st: st and {**st, "lines": [part for line in st["lines"] for part in wrap(line)]}
    return wrapped(before), wrapped(between), wrapped(after)


def first_method(state: dict, notes: list) -> set[int]:
    """The notes (numbered from 1) all of whose anchors are in the first method, isPalindrome."""
    end = TOP + len(blocks(state["lines"])[0]) * LH
    return {n for n, (anchors, _) in enumerate(notes, 1)
            if all(anchor_span(state["lines"], a)[1] < end for a in ([anchors] if isinstance(anchors, str) else anchors))}


def build():
    steps = {}  # (track, k) -> (before view, between view, after view, before runs, between runs, after runs)
    index = {}
    for track, spec in TRACKS.items():
        states = code_states() if track == "code" else morph.load_states(track)
        index[track] = {st["versions"][0]: k for k, st in enumerate(states)}
        assert set(spec["notes"]) == set(spec["asides"]) == set(index[track]) == set(spec["titles"]), \
            f"{track}: notes for {sorted(spec['notes'])}, states {sorted(index[track])}"
        for k in range(len(states)):
            before, between, after = views(track, states, k)
            runs = morph.chain([v for v in (before, between, after) if v])
            steps[track, k] = (before, between, after, runs[0] if before else None, runs[1] if between else None,
                               runs[-1])
            notes = spec["notes"][after["versions"][0]]
            if before and before["versions"] != ONE_LINER["versions"] and (missing := uncovered(after, runs[-1], runs[0], notes)):
                raise SystemExit(f"{track} {after['versions'][0]}: new code without a highlight: " + ", ".join(missing))

    ids = []  # every slide's id; a step split in two adds its first slide, <id>-is, before its own
    item_id = []  # the id of each item of SEQUENCE
    for n, item in enumerate(SEQUENCE):
        if not isinstance(item, tuple):
            ids.append(item)
            item_id.append(item)
            continue
        kind, v = item
        if kind == "cloud":
            ids.append("tc" + v.replace(".", "-"))
            item_id.append(ids[-1])
            continue
        track, again = track_of(kind)
        if not again and steps[track, index[track][v]][1]:
            ids.append(TRACKS[track]["slide"] + v.replace(".", "-") + "-is")
        ids.append(TRACKS[track]["slide"] + v.replace(".", "-") + ("-again" if again else ""))
        item_id.append(ids[-1])
        if again:  # a state shown again leads straight into the track's next state
            nxt = SEQUENCE[n + 1] if n + 1 < len(SEQUENCE) else None
            assert isinstance(nxt, tuple) and track_of(nxt[0]) == (track, False) and \
                index[track][nxt[1]] == index[track][v] + 1, f"{item} must be followed by the next {track} state"
    assert len(set(ids)) == len(ids), "a slide appears twice in SEQUENCE"

    slides = DECK / "slides"
    hand = {item for item in SEQUENCE if not isinstance(item, tuple)}
    files = {f.stem for f in slides.glob("*.html")}
    if missing := sorted(hand - files):
        raise SystemExit("slides in SEQUENCE without a file: " + ", ".join(missing))
    if stray := sorted(f for f in files - hand if not GENERATED.match(f)):
        raise SystemExit("hand-written slides not in SEQUENCE: " + ", ".join(stray))
    for old in files - hand - set(ids):
        (slides / f"{old}.html").unlink()

    for n, item in enumerate(SEQUENCE):
        if not isinstance(item, tuple):
            path = slides / f"{item}.html"
            html = path.read_text()
            if leave := leaving(n, None):  # it leads into a state shown again
                html = re.sub(r'(<section id="[^"]+" data-transition=")[a-z]+"', rf'\g<1>{leave}"', html, count=1)
            new_in = re.match(r"f(\d+)-(\d+)$", item)  # a "New in" slide, f2-8 for 2.8
            new = with_footer(normalize(html, RESERVE_CODE_STYLE if item in RESERVE else CODE_STYLE), HAND_VERSIONS.get(item) or (new_in and ".".join(new_in.groups())))
            if new != html:
                path.write_text(new)
            continue
        kind, v = item
        if kind == "cloud":
            html = (CLOUDS / f"s{v.replace('.', '-')}.html").read_text()
            html = html.replace(f'<section id="s{v.replace(".", "-")}" data-transition="push"',
                                f'<section id="{item_id[n]}" data-transition="{leaving(n, "push")}"', 1)
            (slides / f"{item_id[n]}.html").write_text(with_footer(html, v))  # the timeline with 4.0
            continue
        track, again = track_of(kind)
        spec = TRACKS[track]
        k = index[track][v]
        slide = item_id[n]
        if again:  # the previous state, as the next step shows it
            view, runs = steps[track, k + 1][0], steps[track, k + 1][3]
            html = code_slide(slide, view, runs, "magic", [], spec["again"].format(v=v), "", spec["token"])
            (slides / f"{slide}.html").write_text(with_footer(html, view["versions"][0]))
            continue
        _, between, view, _, between_runs, runs = steps[track, k]
        notes, aside, title = spec["notes"][v], spec["asides"][v], spec["titles"][v]
        first, layout = set(), {}
        first_title, title = title if isinstance(title, tuple) else (title, title)
        only = None
        if between:  # isPalindrome morphs first, with its notes; palindromize follows on the next click
            first = first_method(view, notes)
            html = code_slide(f"{slide}-is", between, between_runs, "magic", notes, aside, first_title, spec["token"],
                              only=first, layout=layout)
            (slides / f"{slide}-is.html").write_text(with_footer(html, view["versions"][0]))
            if first_title != title:  # a new heading, a new topic: isPalindrome's notes go
                only, first = set(range(1, len(notes) + 1)) - first, set()
        html = code_slide(slide, view, runs, leaving(n), notes, aside, title, spec["token"], only=only, shown=first,
                          keep=layout)
        (slides / f"{slide}.html").write_text(with_footer(html, view["versions"][0]))

    path = DECK / "deck.json"
    deck = json.loads(path.read_text()) if path.exists() else \
        {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-09-27T12:00:00Z"}}
    deck.update({"title": TITLE, "order": ids, "sections": SECTIONS, "faces": FACES})
    path.write_text(json.dumps(deck, indent=2, ensure_ascii=False) + "\n")
    count = sum(len(n) for spec in TRACKS.values() for n in spec["notes"].values())
    print(f"{DECK.parent.name}: {len(ids)} slides, {count} notes")

if __name__ == "__main__":
    import sys
    if sys.argv[1:]:
        sys.exit(__doc__)
    build()
