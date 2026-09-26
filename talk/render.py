#!/usr/bin/env python3
"""Renders the deck in talk/deck/ with headless Chrome and checks its layout.

Usage: talk/render.py                 measure every slide; exit 1 if anything overflows
       talk/render.py --screenshots   also write one PNG per slide, plus contact sheets, to out/talk-render/

Each slide is laid out on the deck's fixed 1920x1080 canvas with the deck's own fonts, then measured:
- OUTSIDE MARGINS: an element crosses the 128px margins (fails the check).
- TEXT OVERFLOWS: text runs past its container, e.g. a code line past its panel (fails the check).
- HEADING WRAPS: a heading without a <br> takes more than one line (reported, not a failure: some are meant to).
- The lowest content edge per slide, to show how much vertical room is left.

This approximates the Slides artifact's own renderer; it doesn't run it. Fonts come from the Google Fonts links in
deck.json and are cached under out/talk-render/fonts. Needs Python 3 and Google Chrome (or Chromium); set CHROME to
its path if it isn't found.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECK = ROOT / "talk/deck/project"
OUT = ROOT / "out/talk-render"
BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

# Browser defaults the slide format doesn't have: no margins, border-box sizing, ruled table cells.
RESET = """<style>
*{margin:0;box-sizing:border-box} html,body{width:1920px;background:#555}
section{width:1920px;height:1080px;position:relative;overflow:hidden}
table{border-collapse:collapse;width:100%} td,th{padding:0.35em 0.6em;border-bottom:1px solid rgba(0,0,0,0.15)}
th{font-weight:600} aside{display:none}
</style>"""

MEASURE = """<script>
document.fonts.ready.then(() => setTimeout(() => {
  const L = 128, T = 128, R = 1920 - 128, B = 1080 - 128, report = {};
  for (const s of document.querySelectorAll('section')) {
    const out = [], top0 = s.getBoundingClientRect().top;
    for (const el of s.querySelectorAll('*')) {
      if (el.closest('aside')) continue;
      const b = el.getBoundingClientRect();
      if (!b.width && !b.height) continue;
      const top = b.top - top0, bottom = b.bottom - top0, tag = el.tagName.toLowerCase();
      const txt = (el.textContent || '').trim().slice(0, 60);
      if (b.right > R + 1 || bottom > B + 1 || b.left < L - 1 || top < T - 1)
        out.push(`OUTSIDE MARGINS ${tag} [${Math.round(b.left)},${Math.round(top)} to ${Math.round(b.right)},${Math.round(bottom)}] "${txt}"`);
      if (['p', 'h1', 'h2', 'h3', 'td', 'th'].includes(tag)) {
        const parent = el.parentElement, pb = parent.getBoundingClientRect();
        const innerRight = pb.right - parseFloat(getComputedStyle(parent).paddingRight);
        const over = Math.max(el.scrollWidth - el.clientWidth, b.right - innerRight);
        if (over > 1) out.push(`TEXT OVERFLOWS ${tag} by ${Math.round(over)}px "${txt}"`);
        const lines = Math.round(b.height / parseFloat(getComputedStyle(el).lineHeight));
        if (/^h[123]$/.test(tag) && lines > 1 && !el.querySelector('br'))
          out.push(`HEADING WRAPS to ${lines} lines ${tag} "${txt}"`);
      }
    }
    let lowest = 0;
    for (const c of s.children) if (c.tagName !== 'ASIDE') lowest = Math.max(lowest, c.getBoundingClientRect().bottom - top0);
    report[s.id] = {problems: out, lowest: Math.round(lowest)};
  }
  document.getElementById('report').textContent = JSON.stringify(report);
}, 300));
</script>"""


def chrome() -> str:
    candidates = [os.environ.get("CHROME"),
                  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                  "/Applications/Chromium.app/Contents/MacOS/Chromium",
                  shutil.which("google-chrome"), shutil.which("chromium"), shutil.which("chromium-browser")]
    for c in candidates:
        if c and Path(c).exists():
            return c
    sys.exit("talk/render.py: Chrome not found; set CHROME to its path")


def run_chrome(profile: Path, args: list[str], done) -> str:
    """Runs headless Chrome until done(stdout so far) holds, then stops it.

    Headless Chrome can finish its work (print the DOM, write the screenshot) and then not exit, at least on macOS,
    so waiting for the process would stall every call; polling for the result doesn't."""
    cmd = [chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={profile}",
           "--virtual-time-budget=5000", *args]
    with tempfile.TemporaryFile() as out:
        proc = subprocess.Popen(cmd, stdout=out, stderr=subprocess.DEVNULL)
        try:
            for _ in range(1200):  # at most 120 s
                out.seek(0)
                text = out.read().decode(errors="replace")
                if done(text) or proc.poll() is not None:
                    return text
                time.sleep(0.1)
            sys.exit(f"talk/render.py: Chrome timed out: {' '.join(args)}")
        finally:
            proc.kill()
            proc.wait()


def screenshot_written(path: Path):
    """done() for a screenshot: the PNG exists and has stopped growing."""
    last = [-1]
    def done(_):
        size = path.stat().st_size if path.exists() else -1
        finished = size > 0 and size == last[0]
        last[0] = size
        return finished
    return done


def local_fonts(deck: dict) -> str:
    """Downloads the deck's Google Fonts (Latin subsets) once and returns a stylesheet pointing at the local files.

    Local files keep Chrome's virtual time deterministic; with network fonts, headless Chrome can hang."""
    fonts = OUT / "fonts"
    fonts.mkdir(parents=True, exist_ok=True)
    rules = []
    for key, face in deck.get("faces", {}).items():
        if "href" not in face:
            print(f"note: face {face.get('family')} has no Google Fonts href; rendering falls back", file=sys.stderr)
            continue
        request = urllib.request.Request(face["href"], headers={"User-Agent": BROWSER_UA})
        css = urllib.request.urlopen(request, timeout=30).read().decode()
        for i, (subset, block) in enumerate(re.findall(r"/\* ([\w-]+) \*/\s*(@font-face \{.*?\})", css, re.S)):
            if subset not in ("latin", "latin-ext"):
                continue
            url = re.search(r"url\((https://[^)]+)\)", block).group(1)
            file = fonts / f"{key}-{subset}-{i}.woff2"
            if not file.exists():
                urllib.request.urlretrieve(url, file)
            rules.append(block.replace(url, file.as_uri()))
    return "<style>" + "\n".join(rules) + "</style>"


def page(fonts: str, sections: str, script: str = "") -> str:
    return (f'<!doctype html><html><head><meta charset="utf-8">{fonts}{RESET}</head>'
            f'<body>{sections}<pre id="report" style="display:none"></pre>{script}</body></html>')


def main() -> None:
    screenshots = sys.argv[1:] == ["--screenshots"]
    if sys.argv[1:] and not screenshots:
        sys.exit(__doc__)
    deck = json.loads((DECK / "deck.json").read_text())
    slides = {sid: (DECK / f"slides/{sid}.html").read_text() for sid in deck["order"]}
    fonts = local_fonts(deck)
    OUT.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        profile = Path(tmp) / "profile"
        all_slides = OUT / "all.html"
        all_slides.write_text(page(fonts, "".join(slides.values()), MEASURE))
        dom = run_chrome(profile, ["--window-size=1920,1080", "--dump-dom", all_slides.as_uri()],
                         lambda text: "</html>" in text)
        found = re.search(r'<pre id="report"[^>]*>([^<]*)</pre>', dom)
        if not found or not found.group(1):
            sys.exit("talk/render.py: Chrome returned no measurements")
        report = json.loads(found.group(1).replace("&quot;", '"').replace("&amp;", "&"))

        failed = False
        for n, sid in enumerate(deck["order"], 1):
            r = report[sid]
            status = "ok" if not r["problems"] else ""
            print(f"{n:2} {sid:18} lowest edge {r['lowest']:4}/952  {status}")
            for p in r["problems"]:
                print(f"     {p}")
                failed |= not p.startswith("HEADING WRAPS")

        if screenshots:
            shots = OUT / "shots"
            shutil.rmtree(shots, ignore_errors=True)
            shots.mkdir()
            names = []
            for n, (sid, html) in enumerate(slides.items(), 1):
                name = f"{n:02}-{sid}"
                single = OUT / f"{name}.html"
                single.write_text(page(fonts, html))
                png = shots / f"{name}.png"
                run_chrome(profile, ["--window-size=1920,1080", f"--screenshot={png}", single.as_uri()],
                           screenshot_written(png))
                single.unlink()
                names.append(name)
            for i in range(0, len(names), 6):
                cells = "".join(
                    f'<div style="position:relative"><img src="shots/{n}.png" style="width:960px;height:540px;display:block">'
                    f'<span style="position:absolute;left:8px;top:8px;background:#ff0;font:bold 22px sans-serif;'
                    f'padding:2px 8px">{n}</span></div>' for n in names[i:i + 6])
                sheet = OUT / f"sheet{i // 6 + 1}.html"
                sheet.write_text(f'<!doctype html><body style="margin:0;background:#555;display:grid;'
                                 f'grid-template-columns:960px 960px">{cells}</body>')
                png = OUT / f"sheet{i // 6 + 1}.png"
                png.unlink(missing_ok=True)
                run_chrome(profile, ["--window-size=1920,1620", f"--screenshot={png}", sheet.as_uri()],
                           screenshot_written(png))
            print(f"\nScreenshots: {shots.relative_to(ROOT)}/ and contact sheets {OUT.relative_to(ROOT)}/sheet*.png")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
