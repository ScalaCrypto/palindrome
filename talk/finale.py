#!/usr/bin/env python3
"""Records the talk's finale as one looping video, for the deck's finale slide.

Usage: talk/finale.py      after talk/deck.py; writes out/finale/finale.mp4 and its still, out/finale/finale.png

talk/deck.py writes the finale's frames as a deck of their own (out/finale/project/): the whole of 2.5 zoomed out, then a
slide per version, each morphing from the last. This plays them in the local player (talk/present/) in headless
Chrome, driven through its DevTools pipe, freezes each transition at evenly spaced moments (the player's test hook,
freezeAll) and screenshots each one. The frames, with how long each is shown, become an H.264 video: the overview,
its fade into 2.5 close up, each version's morph and a pause on it, and, after 4.0, a fade back to the overview, so
the slide, which plays it looping, never jumps. The still, which the slide shows wherever the video doesn't play
(thumbnails, downloads), is the overview, the loop's first frame.

A video, not an animated image: the Slides format plays a video on a slide, looping, while it's shown, and the
artifact's asset store takes uploads of a few MB at most (1 MB went up, 5 MB didn't). An animated GIF has 256 colours,
too few for anti-aliased code; a lossless animated WebP keeps it sharp but comes to about 10 MB. The video is about
2 MB, with the code as sharp as on the slides.

To put a new recording in the deck: upload out/finale/finale.mp4 and out/finale/finale.png to the deck's artifact as
assets, set FINALE_CLIP and FINALE_STILL in talk/deck.py to the urls they get (/_blob/<id>), copy each file to
talk/5.20-deck/assets/<id>.mp4 or .png (what talk/present.py and talk/render.py show for them, and the versioned
copies), delete the old ones, there and in the artifact, and rebuild.
"""

from __future__ import annotations

import base64
import http.server
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import present  # noqa: E402  (talk/present.py: the player's server)
import render  # noqa: E402  (talk/render.py: where Chrome is)

ROOT = render.ROOT
FRAMES = ROOT / "out/finale/project"  # deck.py's FINALE_FRAMES
OUT = ROOT / "out/finale"

# The loop's timing, in ms: a frame every STEP while something moves (the video's frame rate); the overview shown OVERVIEW, a version HOLD (the
# last LAST), a morph played in MORPH, and the fade from 4.0 back to the overview in BACK. The player's own durations
# (read from player.js) are only where in each transition a frame is frozen.
STEP, OVERVIEW, HOLD, LAST, MORPH, BACK = 50, 3000, 2000, 3000, 1500, 1000


class Chrome:
    """Headless Chrome with one page, driven through the DevTools protocol over a pipe (no third-party client)."""

    def __init__(self, profile: str):
        to_chrome, self.commands = os.pipe()
        self.replies, from_chrome = os.pipe()

        def fds():  # Chrome reads commands on fd 3 and writes replies on fd 4
            os.dup2(to_chrome, 3)
            os.dup2(from_chrome, 4)

        self.proc = subprocess.Popen(
            [render.chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={profile}",
             "--remote-debugging-pipe", "--window-size=1920,1080"],
            preexec_fn=fds, close_fds=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.close(to_chrome)
        os.close(from_chrome)
        self.buffer, self.last = b"", 0
        target = self.send("Target.createTarget", {"url": "about:blank"})["targetId"]
        self.session = self.send("Target.attachToTarget", {"targetId": target, "flatten": True})["sessionId"]
        self.send("Emulation.setDeviceMetricsOverride",
                  {"width": 1920, "height": 1080, "deviceScaleFactor": 1, "mobile": False}, page=True)

    def send(self, method: str, params: dict | None = None, page: bool = False) -> dict:
        self.last += 1
        message = {"id": self.last, "method": method, "params": params or {}}
        if page:
            message["sessionId"] = self.session
        os.write(self.commands, json.dumps(message).encode() + b"\0")
        while True:  # replies and events, each ending in a NUL; events are skipped
            while b"\0" not in self.buffer:
                chunk = os.read(self.replies, 1 << 20)
                if not chunk:
                    sys.exit("talk/finale.py: Chrome quit")
                self.buffer += chunk
            raw, self.buffer = self.buffer.split(b"\0", 1)
            reply = json.loads(raw)
            if reply.get("id") == self.last:
                if "error" in reply:
                    sys.exit(f"talk/finale.py: {method}: {reply['error']}")
                return reply["result"]

    def run(self, js: str):
        """Evaluates js in the page, awaiting it if it's a promise; its value."""
        result = self.send("Runtime.evaluate", {"expression": js, "awaitPromise": True, "returnByValue": True}, page=True)
        return result["result"].get("value")

    def open(self, url: str, ready: str):
        """Loads url, then waits until the expression `ready` holds and the fonts are in."""
        self.send("Page.navigate", {"url": url}, page=True)
        for _ in range(200):
            time.sleep(0.05)
            if self.run(f"!!document.querySelector('.host') && !!({ready})"):
                self.run("document.fonts.ready.then(() => true)")
                return
        sys.exit(f"talk/finale.py: the player didn't get ready at {url}")

    def shot(self) -> bytes:
        return base64.b64decode(self.send("Page.captureScreenshot", {"format": "png"}, page=True)["data"])

    def close(self):
        self.proc.kill()
        self.proc.wait()


def main() -> None:
    if not (FRAMES / "deck.json").is_file():
        sys.exit("talk/finale.py: no frames in out/finale/project/; run talk/deck.py first")
    if not (ffmpeg := shutil.which("ffmpeg")):
        sys.exit("talk/finale.py: ffmpeg not found (brew install ffmpeg)")
    player = (present.PAGES / "player.js").read_text()
    durations = dict(re.findall(r"\b(MAGIC|FADE) = (\d+)", player))
    magic, fade = int(durations["MAGIC"]), int(durations["FADE"])
    count = len(json.loads((FRAMES / "deck.json").read_text())["order"])

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), present.handler(FRAMES))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}/"
    shots = OUT / "frames"
    shutil.rmtree(shots, ignore_errors=True)
    shots.mkdir(parents=True)
    frames: list[tuple[Path, int]] = []  # each frame's file and how long it's shown

    def keep(png: bytes, ms: int):
        path = shots / f"{len(frames):04}.png"
        path.write_bytes(png)
        frames.append((path, ms))

    def transition(i: int, length: int, player_ms: int, hold: int):
        """The move from slide i to the next, played in `length` ms, then held for `hold`."""
        chrome.open(f"{base}?at={i}.0&next=1&freeze=0", "document.querySelector('.host').getAnimations({subtree: true}).length")
        n = length // STEP
        for k in range(1, n + 1):
            chrome.run(f"freezeAll(document.querySelector('.host'), {player_ms * k / n})")
            keep(chrome.shot(), hold if k == n else STEP)

    with tempfile.TemporaryDirectory() as profile:
        chrome = Chrome(profile)
        try:
            chrome.open(f"{base}?at=0.0", "document.querySelector('.layer section')")
            keep(chrome.shot(), OVERVIEW)
            transition(0, fade, fade, HOLD)  # the overview fades into 2.5 close up, at the player's own pace
            for i in range(1, count - 1):
                transition(i, MORPH, magic, LAST if i == count - 2 else HOLD)
            # back to the start, through the empty slide: 4.0 fades out under a cover the slide's colour, then the
            # overview fades in (frame n would be the overview, the loop's first)
            chrome.open(f"{base}?at={count - 1}.0", "document.querySelector('.layer section')")
            chrome.run("loadDeck().then(deck => { const s = document.querySelector('.layer section'); "
                       "const cover = document.createElement('div'); cover.style.cssText = "
                       "`position:absolute; inset:0; opacity:0; background:${getComputedStyle(s).backgroundColor}`; "
                       "s.append(cover); const layer = makeLayer(deck.slides[0], 0); layer.style.opacity = 0; "
                       "document.querySelector('.layer').after(layer); window.back = [cover, layer]; return true; })")
            n = BACK // STEP
            smooth = lambda t: t * t * (3 - 2 * t)
            for k in range(1, n):
                t = k / n
                cover, overview = (smooth(2 * t), 0) if t < 0.5 else (1, smooth(2 * t - 1))
                chrome.run(f"window.back[0].style.opacity = {cover}; window.back[1].style.opacity = {overview}")
                keep(chrome.shot(), STEP)
        finally:
            chrome.close()
            server.shutdown()

    # The frames as ffmpeg's concat list, each with how long it's shown (the last one listed twice, as concat needs),
    # into a video at a constant frame rate: a held frame repeats, which H.264 stores almost for free.
    listing = OUT / "frames.txt"
    lines = [f"file '{path}'\nduration {ms / 1000}" for path, ms in frames] + [f"file '{frames[-1][0]}'"]
    listing.write_text("\n".join(lines) + "\n")
    clip, still = OUT / "finale.mp4", OUT / "finale.png"
    subprocess.run([ffmpeg, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
                    "-vf", f"fps={1000 // STEP},format=yuv420p", "-c:v", "libx264", "-preset", "veryslow",
                    "-tune", "animation", "-crf", "24", "-movflags", "+faststart", str(clip)], check=True)
    shutil.copyfile(frames[0][0], still)
    seconds = sum(ms for _, ms in frames) / 1000
    print(f"{clip.relative_to(ROOT)}: {seconds:.1f} s a loop, {clip.stat().st_size / 1e6:.1f} MB; "
          f"its still {still.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
