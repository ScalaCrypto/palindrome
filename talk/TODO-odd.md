# For Odd: artifact tasks only your account can do

Two jobs on the claude.ai artifacts are left over from the sessions of 2026-10-11 and 2026-10-13. They need your
account: the talk deck's artifact is yours, and Martin's account (writer access) can't delete the assets in it (HTTP
403, or a blocked delete), and can't open the bullets deck's artifact at all.

Check out `main` and ask Claude Code to do what this file says, for example: "Do the tasks in talk/TODO-odd.md".
When it's done, delete this file in the same PR that records it.

The talk deck: <https://claude.ai/artifact/25dnv7jYfipK6R27X8g94t>

## Delete the old finale videos from the talk deck

The finale was recorded again, twice (PR #83, and the 4.0 slide's `case _ => false`). The talk deck's finale slide
uses the newest video and the still, `/_blob/a8ed2ac6bec27991a2fb7f39c3011aee` and
`/_blob/00ffd4e8fd60be4596002a3720353148` (`FINALE_CLIP` and `FINALE_STILL` in `talk/deck.py`). The two older videos
are still in the deck's asset store, and nothing references them:

- `a8dd69f192524dbadf99aad997994db6`: the first video (video/mp4, 2373019 bytes)
- `7ea46e81aac5270845d10c46cad1d77c`: the second video (video/mp4, 2350859 bytes)

Steps:

1. List the talk deck's assets (`Artifact` list, `scope: "assets"`) and confirm both ids are there with those sizes.
2. Read `project/slides/finale.html` from the talk deck and confirm it names the new ids, not these.
3. Delete each asset (`Artifact` delete with the deck's `url` and the id as `path`).

## Put the new finale video in the bullets deck

The bullets deck's finale still plays the second video, its copy `/_blob/7a8acf232561b13a80ec8df2e9ce19f1`
(`FINALE_BULLETS` in `talk/deck.py`). Its still, `e699ef8f52966f76d6de44d1435dcb72`, is unchanged.

Steps:

1. Upload `talk/5.20-deck/assets/a8ed2ac6bec27991a2fb7f39c3011aee.mp4` to the bullets deck's artifact as an asset.
2. In `talk/deck.py`, set `FINALE_BULLETS`'s video entry to the url it gets (`/_blob/<new id>`).
3. In `talk/5.20-deck/assets/`, replace the symlink `7a8acf232561b13a80ec8df2e9ce19f1.mp4` with one named
   `<new id>.mp4` pointing to `a8ed2ac6bec27991a2fb7f39c3011aee.mp4`.
4. Build with `talk/deck.py --notes talk/bullets.md`, publish the changed slides (at least `m3-6-again`, `m4-0` and
   `finale`) to the bullets deck, then run `talk/deck.py` again so the repo's slides have the dialogue back.
5. Delete the old video `7a8acf232561b13a80ec8df2e9ce19f1` from the bullets deck's assets.
