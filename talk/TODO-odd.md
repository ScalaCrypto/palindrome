# For Odd: artifact tasks only your account can do

Two jobs on the claude.ai artifacts are left over from the session of 2026-10-11. They need your account: the talk
deck's artifact is yours, and Martin's account (writer access) can't delete the assets you uploaded (HTTP 403) or
open the bullets deck's artifact at all ("not found or not shared"). Everything else is done and merged on `main`.

Check out `main` and ask Claude Code to do what this file says, for example: "Do the tasks in talk/TODO-odd.md".
When both are done, delete this file in the same PR that records it.

The artifacts:

- Talk deck: <https://claude.ai/artifact/25dnv7jYfipK6R27X8g94t>
- Bullets deck (the talk deck with `talk/bullets.md` as its speaker notes): <https://claude.ai/artifact/MNEpuzNizekFbUBie6rJUx>

## 1. Delete the old finale video from the talk deck

The finale was recorded again (PR #83). The talk deck's finale slide now uses the new video and still,
`/_blob/7ea46e81aac5270845d10c46cad1d77c` and `/_blob/00ffd4e8fd60be4596002a3720353148`. The old pair is still in
the deck's asset store, and nothing references it:

- `a8dd69f192524dbadf99aad997994db6`: the old video (video/mp4, 2373019 bytes)
- `1c039043ee62a418578ac19a84eb48cd`: the old still (image/png, 146249 bytes)

Steps:

1. List the talk deck's assets (`Artifact` list, `scope: "assets"`) and confirm both ids are there with those sizes.
2. Read `project/slides/finale.html` from the talk deck and confirm it names the new ids, not these.
3. Delete the two assets (`Artifact` delete with the deck's `url` and each id as `path`).

## 2. Bring the bullets deck up to date

The bullets deck was last published before PR #78. Since then `main` has changed, and the bullets deck has none of it:

- the notes in `talk/bullets.md` (PRs #78, #81, #82),
- the code slides: 2.5–2.7's `x.toLowerCase` and 2.8's rename to `toLower` (#81), the 2.13 bubbles (#78, #82),
- the finale's QR code (#80) and its new recording (#83).

Steps (`talk/README.md`, "The finale's video", step 3, and the bullets deck in its list of files):

1. Compare the bullets deck's `project/` files with a `talk/deck.py --notes talk/bullets.md` build of `main`. If any
   hand-written slide differs from that build in more than its notes, the bullets deck was edited in the browser:
   stop and ask before overwriting it.
2. Copy the finale's new video and still from the talk deck into the bullets deck's asset store, server side:
   `Artifact` publish with the bullets deck's `url`, `asset: true`, `from_url` the talk deck, and `asset_ids`
   `["7ea46e81aac5270845d10c46cad1d77c", "00ffd4e8fd60be4596002a3720353148"]`. Note the urls the copies get.
3. In `talk/deck.py`, set `FINALE_BULLETS` to the copies' urls (video for `FINALE_CLIP`, still for `FINALE_STILL`),
   and put back the comment above it that says their local copies are symlinks to the deck's.
4. In `talk/5.20-deck/assets/`, delete `39dc2aa238168769fe2574515e0930e4.mp4` and
   `b85d0046a6e5a93123a4a53167d82601.png` (files of the old recording, kept only because the bullets deck still
   showed it), and add symlinks from the copies' ids to the deck's files:
   `<video copy id>.mp4 -> 7ea46e81aac5270845d10c46cad1d77c.mp4` and
   `<still copy id>.png -> 00ffd4e8fd60be4596002a3720353148.png`.
5. Build the bullets deck and keep a copy, then rebuild the talk deck so the repo keeps the dialogue:
   `talk/deck.py --notes talk/bullets.md`, copy `talk/5.20-deck/project/` to a scratch folder,
   `talk/deck.py` again. `git status` should then show only the changes from steps 3 and 4.
6. Check: `talk/render.py`, `talk/present.py --check --notes talk/bullets.md`.
7. Publish the scratch copy's `project/` files to the bullets deck (its `url`, the scratch folder as `root`).
8. Delete the bullets deck's old finale copies, `39dc2aa238168769fe2574515e0930e4` and
   `b85d0046a6e5a93123a4a53167d82601`, after confirming its `finale.html` names the new copies.
9. Commit (steps 3 and 4, and this file deleted) on a `feature/` branch and open a PR against `main`.
