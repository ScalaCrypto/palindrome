#!/usr/bin/env python3
"""Generates the tag-cloud deck in talk/tag-cloud/project/: one slide per Scala release from 2.5 to 3.9, a cloud of
the authors of the commits that went into it, each name sized by its commit count within that release, and the
top committer in amber.

Usage: talk/tag-cloud.py

The data is talk/tag-cloud/authors.json: per release, the commit range, the totals and the top 60 authors, plus the
method, every merge of one person's aliases and every exclusion (bots, unattributable SVN commits). It was gathered
from history-only clones of github.com/scala/scala and github.com/scala/scala3 on 2026-09-28; see its "method".

Slides can't run scripts and text can't be under 24px, so each cloud is static: one <p> per name, in a centred,
wrapping row. The generator estimates each cloud's size and shows as many names as fit, shrinking the largest size
before it drops names. talk/render.py checks the result.
"""

import json
import math
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "talk/tag-cloud/authors.json"
OUT = ROOT / "talk/tag-cloud/project"

# The decks' palette: dark slate, amber accent, IBM Plex.
BG, TEXT, SOFT, MUTED, AMBER = "#1B1F2A", "#E8E6DF", "#C3C8D1", "#9AA3AF", "#F2A65A"
SANS = "'IBM Plex Sans', Arial, sans-serif"

# The years the talk deck's timeline uses (2.10.0's tag commit is from December 2012; it was released in January 2013).
YEARS = {"2.5": 2007, "2.6": 2007, "2.7": 2008, "2.8": 2010, "2.9": 2011, "2.10": 2013, "2.11": 2014, "2.12": 2016,
         "2.13": 2019, "3.0": 2021, "3.1": 2021, "3.2": 2022, "3.3": 2023, "3.4": 2024, "3.5": 2024, "3.6": 2024,
         "3.7": 2025, "3.8": 2026, "3.9": 2026}
FOOTNOTES = {
    "2.7": "No v2.7.0 tag: the range ends at the last commit before the 2.7.0 release on 2008-03-06.",
    "3.0": "Commits after the 2.13.0 release (2019-06-07) up to 3.0.0. All of Dotty since 2012: {all} commits by "
           "{all_authors} authors.",
    "3.6": "3.6.2 stands in for 3.6.0, which was published by accident; the Scala team treats 3.6.2 as the release.",
    "3.8": "Leaves out the 6,011 commits of Scala 2 library history imported into the repo during 3.8.",
}

# The cloud's box: the slide's 128px margins; below the heading (the release, 88px), above the stats line. The
# timeline runs below the bottom margin.
WIDTH, HEIGHT = 1664, 608
MIN_SIZE, GAP, PAD_X, LINE = 24, 6, 12, 1.12
EM = 0.6  # IBM Plex Sans averages a little under 0.6 em per character; bold a little over, hence this estimate


def sizes(top, largest):
    most = top[0][1]
    return [MIN_SIZE + (largest - MIN_SIZE) * math.sqrt(n / most) for _, n in top]


def centre_heavy(items):
    """The largest items in the middle: each next-largest goes alternately to the back and the front."""
    out = []
    for i, item in enumerate(items):
        out.insert(0, item) if i % 2 else out.append(item)
    return out


def height(words):
    """The height of words (text, size) packed into rows of WIDTH, the way a centred wrapping flex row lays them out."""
    rows, row_width, row_height = [], 0.0, 0.0
    for text, size in words:
        w = len(text) * size * EM + 2 * PAD_X
        if row_width and row_width + GAP + w > WIDTH:
            rows.append(row_height)
            row_width, row_height = 0.0, 0.0
        row_width += (GAP if row_width else 0) + w
        row_height = max(row_height, size * LINE)
    rows.append(row_height)
    return sum(rows) + GAP * (len(rows) - 1)


def fit(top):
    """The names and sizes to show: as many as fit, the largest size shrinking from 104px before names are dropped."""
    for count in range(len(top), 9, -1):
        for largest in range(104, 55, -4):
            shown = top[:count]
            words = centre_heavy(list(zip([n for n, _ in shown], sizes(shown, largest))))
            if height(words) <= HEIGHT:
                return shown, largest
    raise SystemExit("no cloud fits")


def word(name, n, size, rank):
    # The release's top committer in amber; the next two in bold white; the rest fading with rank.
    colour, weight = (AMBER, 700) if rank == 0 else (TEXT, 600) if rank < 3 else (SOFT, 500) if rank < 12 \
        else (MUTED, 400)
    return (f'<p style="font-size:{round(size)}px; font-weight:{weight}; line-height:{LINE}; color:{colour}; '
            f'white-space:nowrap; padding:0 {PAD_X}px">{escape(name)}</p>')


# The footer timeline: every release from 2.5 to 3.9, evenly spaced; the line runs on past 2.5 and fades out at the
# slide's left edge, with faded ticks and labels for the releases before it, which the deck doesn't cover.
LINE_Y, TL_LEFT, TL_RIGHT = 1000, 224, 1760
EARLIER = ["2.4", "2.3", "2.2", "2.1", "2.0"]


def timeline(versions, current=None):
    step = (TL_RIGHT - TL_LEFT) / (len(versions) - 1)
    x = lambda i: TL_LEFT + i * step
    top = LINE_Y - 22
    parts = [f'<defs><linearGradient id="fade" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{TL_LEFT}" y2="0">'
             f'<stop offset="0" stop-color="{MUTED}" stop-opacity="0"/>'
             f'<stop offset="1" stop-color="{MUTED}" stop-opacity="0.55"/></linearGradient></defs>',
             f'<rect x="0" y="21" width="{TL_LEFT}" height="2" fill="url(#fade)"/>',
             f'<rect x="{TL_LEFT}" y="21" width="{round(TL_RIGHT - TL_LEFT)}" height="2" fill="{MUTED}" fill-opacity="0.55"/>']
    for k in range(1, len(EARLIER) + 1):  # earlier releases, fading towards the edge
        xe = x(-k)
        if xe > 0:
            parts.append(f'<rect x="{round(xe - 1, 1)}" y="16" width="2" height="12" fill="{MUTED}" '
                         f'fill-opacity="{round(0.5 / k, 2)}"/>')
    for i, v in enumerate(versions):
        if v == current:
            parts.append(f'<circle cx="{round(x(i), 1)}" cy="22" r="8" fill="{AMBER}"/>')
        else:
            parts.append(f'<rect x="{round(x(i) - 1, 1)}" y="16" width="2" height="12" fill="{MUTED}"/>')
    svg = (f'<svg data-bleed="" aria-label="Timeline of Scala releases from {versions[0]} to {versions[-1]}" width="1920" height="44" '
           f'viewBox="0 0 1920 44" style="position:absolute; left:0px; top:{top}px; width:1920px; height:44px">'
           + "".join(parts) + "</svg>")
    label = lambda xc, text, style: (f'<p data-bleed="" style="position:absolute; left:{round(xc - 40)}px; '
                                     f'top:{LINE_Y + 10}px; width:80px; font-size:24px; line-height:1.2; '
                                     f'text-align:center; {style}">{text}</p>')
    rows = [svg]
    for k, v in enumerate(EARLIER, 1):
        if x(-k) - 40 >= 0:
            rows.append(label(x(-k), v, f"color:{MUTED}; opacity:{round(0.5 / k, 2)}"))
    for i, v in enumerate(versions):
        style = f"color:{AMBER}; font-weight:700" if v == current else f"color:{MUTED}"
        rows.append(label(x(i), v, style))
    return rows


def slide(r, shown, largest, versions, all_counts=None):
    ranks = {name: i for i, (name, _) in enumerate(shown)}
    words = centre_heavy(list(zip(shown, sizes(shown, largest))))
    shown_note = "" if len(shown) == r["authors"] else f", the top {len(shown)} shown"
    foot = FOOTNOTES.get(r["version"], "").format(**(all_counts or {}))
    stats = f'{r["commits"]:,} commits by {r["authors"]:,} authors'
    # 3.0's footnote states its range; the others lead with theirs.
    lead = f'{r["range"].split(" ^")[0]}{shown_note}.' if r["version"] != "3.0" else (f"The top {len(shown)} shown." if shown_note else "")
    rows = [
        f'<section id="s{r["version"].replace(".", "-")}" data-transition="push" style="background:{BG}; color:{TEXT}; '
        f'font-family:{SANS}; padding:128px 128px 128px; display:flex; flex-direction:column; gap:28px">',
        f'<h2 style="font-size:88px; font-weight:700; line-height:1.3; text-align:center; color:{AMBER}">'
        f'Scala {r["version"]} · {YEARS[r["version"]]}</h2>',
        '<div style="flex:1; display:flex; flex-direction:row; flex-wrap:wrap; justify-content:center; '
        f'align-items:center; gap:{GAP}px">',
        *(word(name, n, size, ranks[name]) for (name, n), size in words),
        "</div>",
        f'<p style="font-size:32px; font-weight:600; line-height:1.3; text-align:center; color:{AMBER}">{stats}</p>',
        *timeline(versions, r["version"]),
        # The range and its footnotes go to the speaker notes, to keep the slide to the cloud.
        "<aside>" + escape(f"{lead} {foot} ".lstrip() + "Most commits: "
                           + "; ".join(f"{name} {n}" for name, n in shown[:10]) + ".", quote=False) + "</aside>",
        "</section>",
    ]
    return "\n".join(rows) + "\n"


def cover(releases):
    total = sum(r["commits"] for r in releases)
    versions = [r["version"] for r in releases]
    return f"""<section id="cover" data-transition="push" style="background:{BG}; color:{TEXT}; font-family:{SANS}; padding:128px; display:flex; flex-direction:column; justify-content:center; gap:40px">
<p style="font-size:28px; font-weight:600; letter-spacing:4px; text-transform:uppercase; color:{AMBER}">A Brief History of Scala</p>
<h1 style="font-size:120px; font-weight:700; line-height:1.05">Who wrote Scala</h1>
<p style="font-size:40px; line-height:1.35; color:{SOFT}; width:1400px">The authors of every release from 2.5 to 3.9, one cloud per release, each name sized by its commits in that release. <span style="color:{AMBER}">The top committer</span> is in amber.</p>
<p style="font-size:24px; color:{MUTED}">{total:,} commits from github.com/scala/scala and github.com/scala/scala3, without merge commits and bots.</p>
{chr(10).join(timeline(versions))}
<aside>Each release counts the commits between the previous minor release and its own first release, for example v2.12.0..v2.13.0. Names follow each repository's .mailmap, with one person's aliases merged. Counts are commits, not lines. The data and its method are in talk/tag-cloud/authors.json.</aside>
</section>
"""


def build():
    data = json.loads(DATA.read_text())
    releases = []
    for v in data["versions"]:
        r = dict(v)
        extra = None
        if "since_2_13" in v:  # 3.0: the release cycle since 2.13, comparable with the others
            extra = {"all": f'{v["commits"]:,}', "all_authors": f'{v["authors"]:,}'}
            r.update(v["since_2_13"])
        releases.append((r, extra))

    OUT.joinpath("slides").mkdir(parents=True, exist_ok=True)
    for old in OUT.joinpath("slides").glob("*.html"):
        old.unlink()
    order = ["cover"]
    (OUT / "slides/cover.html").write_text(cover([r for r, _ in releases]))
    report = []
    for r, extra in releases:
        top = [(a["name"], a["commits"]) for a in r["top"]]
        shown, largest = fit(top)
        slide_id = "s" + r["version"].replace(".", "-")
        order.append(slide_id)
        versions = [x["version"] for x, _ in releases]
        (OUT / f"slides/{slide_id}.html").write_text(slide(r, shown, largest, versions, extra))
        report.append(f'{r["version"]}: {len(shown)}/{r["authors"]} names, largest {largest}px')

    deck = {
        "v": 4,
        "createdOnFiles": {"v": 1, "at": "2026-09-28T12:00:00Z"},
        "title": "Who Wrote Scala",
        "order": order,
        "sections": {
            "intro": {"description": "The authors of every Scala release, one cloud per release", "start": "cover"},
            "scala2": {"description": "Scala 2.5 to 2.13, from scala/scala", "start": "s2-5"},
            "scala3": {"description": "Scala 3.0 to 3.9, from scala/scala3", "start": "s3-0"},
        },
        "faces": {"ibm-plex-sans": {"family": "IBM Plex Sans",
                                    "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap"}},
    }
    (OUT / "deck.json").write_text(json.dumps(deck, indent=2, ensure_ascii=False) + "\n")
    print("\n".join(report))


if __name__ == "__main__":
    build()
