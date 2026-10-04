#!/usr/bin/env python3
"""Presents a deck (the talk's deck, talk/5.12-deck/, unless another is named) from this computer, with a presenter
view: the slides full screen on the external display, and on the laptop the current slide, what the next click
shows, the speaker notes and a timer.

Usage: talk/present.py                  serve the talk's deck and open the presenter view in the default browser
       talk/present.py talk/tag-cloud   the same for another deck
       talk/present.py --port 8800      another port (default 8765)
       talk/present.py --no-open        don't open a browser

Then, in the presenter view, click "Open slides window", move that window to the external display, and press F in
it for full screen. Drive the talk from the presenter view: → or space for the next click, ← back, a slide number
then Enter to jump, B to black out the slides, T to start or pause the timer, + and − for the notes' size.

The deck is read from its files on every page load, so reload after talk/deck.py. The fonts come from the cache
talk/render.py keeps in out/talk-render/fonts, so once they're there (after one run of either script with a network)
the talk needs no network at all. talk/present/ holds the pages and the player; its comments say what the player
does with the Slides format.
"""

import argparse
import http.server
import json
import sys
import threading
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render  # noqa: E402  (talk/render.py: the talk's deck, and the deck's fonts cached for offline use)

ROOT = render.ROOT
PAGES = ROOT / "talk/present"
TYPES = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
         ".css": "text/css; charset=utf-8", ".woff2": "font/woff2", ".json": "application/json"}


def deck_payload(deck_dir: Path) -> bytes:
    deck = json.loads((deck_dir / "deck.json").read_text())
    slides = [{"id": sid, "html": (deck_dir / f"slides/{sid}.html").read_text()} for sid in deck["order"]]
    return json.dumps({"title": deck.get("title", ""), "slides": slides}).encode()


def fonts_css(deck_dir: Path) -> bytes:
    """The deck's @font-face rules, pointing at the cached font files this server serves under fonts/."""
    css = render.local_fonts(json.loads((deck_dir / "deck.json").read_text()))
    css = css.removeprefix("<style>").removesuffix("</style>")
    return css.replace(render.FONTS.as_uri() + "/", "fonts/").encode()


def handler(deck_dir: Path):
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            path = self.path.split("?")[0]
            if path in ("/", "/index.html"):
                return self.send(PAGES / "index.html")
            if path in ("/presenter", "/presenter.html"):
                return self.send(PAGES / "presenter.html")
            if path in ("/player.js", "/present.css"):
                return self.send(PAGES / path[1:])
            if path == "/deck.json":
                return self.reply(deck_payload(deck_dir), TYPES[".json"])
            if path == "/fonts.css":
                return self.reply(fonts_css(deck_dir), TYPES[".css"])
            name = path.removeprefix("/fonts/")
            if path.startswith("/fonts/") and "/" not in name and (render.FONTS / name).is_file():
                return self.send(render.FONTS / name)
            self.send_error(404)

        def send(self, file: Path):
            self.reply(file.read_bytes(), TYPES.get(file.suffix, "application/octet-stream"))

        def reply(self, body: bytes, kind: str):
            self.send_response(200)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("deck", nargs="?", help="a deck's directory (default: the talk's deck)")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-open", action="store_true", help="don't open a browser")
    args = parser.parse_args()
    deck_dir = (ROOT / args.deck).resolve() / "project" if args.deck else render.DECK
    if not (deck_dir / "deck.json").is_file():
        sys.exit(f"talk/present.py: no deck at {deck_dir}")
    fonts_css(deck_dir)  # fetch the fonts now, while there's a network, rather than on the first page load

    server = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler(deck_dir))
    url = f"http://localhost:{args.port}/"
    print(f"Presenting {deck_dir.parent.relative_to(ROOT)}\n"
          f"  presenter view: {url}presenter\n"
          f"  slides:         {url}  (or the presenter view's \"Open slides window\")\n"
          f"Ctrl-C to stop.")
    if not args.no_open:
        threading.Timer(0.3, lambda: webbrowser.open(url + "presenter")).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
