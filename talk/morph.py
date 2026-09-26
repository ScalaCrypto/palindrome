#!/usr/bin/env python3
"""Generates the code-morph deck in talk/morph/: the palindrome methods, version by version, where each slide turns
into the next with a magic-move transition, so the code changes in place.

Usage: talk/morph.py

The code comes from each version's src/Palindrome.scala: isPalindrome and palindromize, without comments. Only versions where that code changes get a slide; the slide is labelled
with the range of versions that share it.

How the morph works: the Slides format's magic move animates every pinned element that has the same id on two
adjacent slides from its old place to its new one, and fades the rest out and in. So each code token that survives
from one version to the next keeps its id. Tokens are merged into runs to stay under the 200-element limit, and a run
must be the same run on both of its slide's transitions, so the cut points between runs are propagated along the
chain until they are stable.
"""

import difflib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "talk/morph/project"

# The version directories, oldest first.
VERSIONS = ["2/5", "2/6", "2/7", "2/8", "2/9", "2/10", "2/11", "2/12", "2/13",
            "3/0", "3/1", "3/2", "3/3", "3/4", "3/5", "3/6", "3/7", "3/8", "3/9"]
YEARS = {"2.5": 2007, "2.8": 2010, "2.10": 2013, "2.11": 2014, "2.12": 2016, "2.13": 2019, "3.0": 2021, "3.6": 2024,
         "3.7": 2025}

# Layout on the 1920x1080 canvas. IBM Plex Mono advances 0.6 em per character.
LEFT, CODE_TOP, MAX_WIDTH, MAX_BOTTOM = 128, 168, 1664, 984
LINE_HEIGHT = 1.35

BG, FG, MUTED, ACCENT, TYPE, LITERAL = "#1B1F2A", "#E8E6DF", "#8A93A0", "#F2A65A", "#8FB8E8", "#A8D08D"
KEYWORDS = {"def", "val", "if", "else", "then", "case", "match", "implicit", "using", "extension", "given", "private",
            "new", "class", "object", "type", "as"}

TOKEN = re.compile(r"\s+|@?[A-Za-z_][A-Za-z0-9_]*|\d+|\"[^\"]*\"|[-+*/<>=!:&|^%~?#]+|.")


def extract(src: str) -> list[str]:
    """The palindrome methods of one version, without comments and with the object's indentation removed."""
    lines = src.splitlines()
    start = next(i for i, l in enumerate(lines) if re.match(r"\s*(@tailrec|def isPalindrome|extension \[A)", l))
    end = next((i for i, l in enumerate(lines) if "Method syntax" in l), len(lines))
    body = [l for l in lines[start:end] if not l.strip().startswith("//")]
    indent = min(len(l) - len(l.lstrip()) for l in body if l.strip())
    out: list[str] = []
    for l in body:
        l = l[indent:].rstrip()
        if l or (out and out[-1]):
            out.append(l)
    while out and not out[-1]:
        out.pop()
    return out


def tokenize(lines: list[str]) -> list[dict]:
    """Non-blank tokens with their line and column."""
    toks = []
    for n, line in enumerate(lines):
        for m in TOKEN.finditer(line):
            if not m.group().isspace():
                toks.append({"text": m.group(), "line": n, "col": m.start()})
    return toks


def match(a_lines, b_lines, a, b) -> dict[int, int]:
    """Token index in a -> token index in b: unchanged lines first, then tokens within changed regions, then
    identifiers that moved further but are unambiguous."""
    pairs: dict[int, int] = {}
    by_line = lambda toks, n: [i for i, t in enumerate(toks) if t["line"] == n]
    sm = difflib.SequenceMatcher(None, [l.strip() for l in a_lines], [l.strip() for l in b_lines], autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        ai = [i for n in range(i1, i2) for i in by_line(a, n)]
        bj = [j for n in range(j1, j2) for j in by_line(b, n)]
        if tag == "equal":
            pairs.update(zip(ai, bj))
        elif tag == "replace":
            tsm = difflib.SequenceMatcher(None, [a[i]["text"] for i in ai], [b[j]["text"] for j in bj], autojunk=False)
            for blk in tsm.get_matching_blocks():
                for k in range(blk.size):
                    pairs[ai[blk.a + k]] = bj[blk.b + k]
    # A second pass for identifiers that moved out of order, when there is exactly one candidate on each side.
    free_a = [i for i in range(len(a)) if i not in pairs]
    used_b = set(pairs.values())
    free_b = [j for j in range(len(b)) if j not in used_b]
    for i in free_a:
        text = a[i]["text"]
        if not re.match(r"[A-Za-z_]\w", text):
            continue
        ca = [x for x in free_a if a[x]["text"] == text]
        cb = [y for y in free_b if b[y]["text"] == text and y not in used_b]
        if len(ca) == 1 and len(cb) == 1:
            pairs[i] = cb[0]
            used_b.add(cb[0])
    return pairs


def glued(toks, i, other, pairs) -> bool:
    """Whether tokens i and i+1 can stay in one run for the transition to `other`: both vanish or appear, or both
    have counterparts that sit next to each other with the same spacing."""
    a, b = pairs.get(i), pairs.get(i + 1)
    if a is None and b is None:
        return True
    if a is None or b is None or b != a + 1:
        return False
    return (other[a]["line"] == other[b]["line"]
            and other[b]["col"] - other[a]["col"] == toks[i + 1]["col"] - toks[i]["col"])


def build():
    states = []  # one per distinct code: versions, lines
    for d in VERSIONS:
        src = (ROOT / d / "src/Palindrome.scala").read_text()
        version = re.match(r"// Scala (\d+\.\d+)", src).group(1)
        lines = extract(src)
        if states and states[-1]["lines"] == lines:
            states[-1]["versions"].append(version)
        else:
            states.append({"dir": d, "versions": [version], "lines": lines})

    toks = [tokenize(s["lines"]) for s in states]
    fwd = [match(states[k]["lines"], states[k + 1]["lines"], toks[k], toks[k + 1]) for k in range(len(states) - 1)]
    bwd = [{v: k for k, v in p.items()} for p in fwd]

    # Ids chain from slide to slide: a matched token inherits its counterpart's id.
    fresh = iter(range(10**6))
    for t in toks[0]:
        t["id"] = next(fresh)
    for k, p in enumerate(fwd):
        back = bwd[k]
        for j, t in enumerate(toks[k + 1]):
            t["id"] = toks[k][back[j]]["id"] if j in back else next(fresh)

    # Cut points between neighbouring tokens: cut[k][i] means tokens i and i+1 of slide k are in different runs.
    cut = []
    for k, ts in enumerate(toks):
        c = []
        for i in range(len(ts) - 1):
            same = ts[i]["line"] == ts[i + 1]["line"]
            ok = same and (k == 0 or glued(ts, i, toks[k - 1], bwd[k - 1])) and \
                (k == len(toks) - 1 or glued(ts, i, toks[k + 1], fwd[k]))
            c.append(not ok)
        cut.append(c)
    changed = True
    while changed:
        changed = False
        for k in range(len(toks) - 1):
            for p, src, dst in ((fwd[k], k, k + 1), (bwd[k], k + 1, k)):
                for i, is_cut in enumerate(cut[src]):
                    a, b = p.get(i), p.get(i + 1)
                    if is_cut and a is not None and b == a + 1 and not cut[dst][a]:
                        cut[dst][a] = True
                        changed = True

    width = max(len(l) for s in states for l in s["lines"])
    height = max(len(s["lines"]) for s in states)
    size = min(28, int(MAX_WIDTH / (0.6 * width)), int((MAX_BOTTOM - CODE_TOP) / (LINE_HEIGHT * height)))
    lh, cw = round(size * LINE_HEIGHT), size * 0.6

    OUT.joinpath("slides").mkdir(parents=True, exist_ok=True)
    for old in OUT.joinpath("slides").glob("*.html"):
        old.unlink()
    order = ["cover"]
    (OUT / "slides/cover.html").write_text(cover(states))
    counts = []
    for k, s in enumerate(states):
        runs, run = [], [toks[k][0]]
        for i in range(1, len(toks[k])):
            if cut[k][i - 1]:
                runs.append(run)
                run = []
            run.append(toks[k][i])
        runs.append(run)
        counts.append(len(runs))
        slide_id = "v" + s["versions"][0].replace(".", "-")
        order.append(slide_id)
        (OUT / f"slides/{slide_id}.html").write_text(slide(slide_id, s, runs, size, lh, cw, last=k == len(states) - 1))

    deck = {
        "v": 4,
        "createdOnFiles": {"v": 1, "at": "2026-09-26T12:00:00Z"},
        "title": "isPalindrome, Morphing",
        "order": order,
        "sections": {"morph": {"description": "The palindrome methods changing in place, Scala 2.5 to 3.9",
                               "start": "cover"}},
        "faces": {
            "ibm-plex-sans": {"family": "IBM Plex Sans",
                              "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&display=swap"},
            "ibm-plex-mono": {"family": "IBM Plex Mono",
                              "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&display=swap"},
        },
    }
    (OUT / "deck.json").write_text(json.dumps(deck, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(states)} code slides, font {size}px, runs per slide {counts} (limit 200)")


def label(versions: list[str]) -> str:
    rng = versions[0] if len(versions) == 1 else f"{versions[0]} – {versions[-1]}"
    return f"Scala {rng} · {YEARS[versions[0]]}"


def summary(state) -> str:
    notes = ROOT / state["dir"] / "NOTES.md"
    return notes.read_text().splitlines()[0].lstrip("# ").replace("`", "")


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def color(text: str) -> str | None:
    if text in KEYWORDS:
        return ACCENT
    if text.startswith("@"):
        return MUTED
    if text[0].isupper():
        return TYPE
    if text[0].isdigit() or text[0] == '"':
        return LITERAL
    return None


def run_html(run) -> str:
    parts, prev_end = [], None
    for t in run:
        if prev_end is not None:
            parts.append("&#160;" * (t["col"] - prev_end))
        c = color(t["text"])
        parts.append(f'<span style="color:{c}">{esc(t["text"])}</span>' if c else esc(t["text"]))
        prev_end = t["col"] + len(t["text"])
    return "".join(parts)


def slide(slide_id, state, runs, size, lh, cw, last) -> str:
    head = (f'<section id="{slide_id}" data-transition="{"fade" if last else "magic"}" style="background:{BG}; '
            f"color:{FG}; font-family:'IBM Plex Sans', Arial, sans-serif; padding:80px 128px; display:flex; "
            f'flex-direction:column">')
    rows = [head,
            '<div style="display:flex; flex-direction:row; justify-content:space-between; align-items:baseline; '
            'gap:48px">',
            f'<p style="font-size:24px; font-weight:600; letter-spacing:3px; text-transform:uppercase; '
            f'white-space:nowrap; color:{ACCENT}">{esc(label(state["versions"]))}</p>',
            f'<p style="font-size:24px; color:#C9CCD3; text-align:right">{esc(summary(state))}</p>',
            "</div>"]
    for run in runs:
        first, end = run[0], run[-1]["col"] + len(run[-1]["text"])
        w = round((end - first["col"]) * cw) + 4
        rows.append(f'<p id="t{first["id"]}" style="position:absolute; left:{round(LEFT + first["col"] * cw)}px; '
                    f'top:{CODE_TOP + first["line"] * lh}px; width:{w}px; font-family:\'IBM Plex Mono\', '
                    f'\'Courier New\', monospace; font-size:{size}px; line-height:{lh}px; white-space:nowrap">'
                    f"{run_html(run)}</p>")
    rows.append("</section>")
    return "\n".join(rows) + "\n"


def cover(states) -> str:
    first, last = states[0]["versions"][0], states[-1]["versions"][-1]
    return f"""<section id="cover" data-transition="fade" style="background:{BG}; color:#F7F5EF; font-family:'IBM Plex Sans', Arial, sans-serif; padding:128px; display:flex; flex-direction:column; justify-content:center; gap:40px">
<p style="font-size:28px; font-weight:600; letter-spacing:4px; text-transform:uppercase; color:{ACCENT}">A Brief History of Scala</p>
<h1 style="font-size:120px; font-weight:700; line-height:1.05">isPalindrome,<br>morphing</h1>
<p style="font-size:40px; line-height:1.35; color:#C9CCD3; width:1300px">The palindrome methods from Scala {first} to {last}, one version turning into the next</p>
</section>
"""


if __name__ == "__main__":
    build()
