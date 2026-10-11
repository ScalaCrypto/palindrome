# For Odd: an artifact task only your account can do

One job on the claude.ai artifacts is left over from the session of 2026-10-11. It needs your account: the talk deck's
artifact is yours, and Martin's account (writer access) can't delete the assets you uploaded (HTTP 403).

Check out `main` and ask Claude Code to do what this file says, for example: "Do the tasks in talk/TODO-odd.md".
When it's done, delete this file in the same PR that records it.

The talk deck: <https://claude.ai/artifact/25dnv7jYfipK6R27X8g94t>

## Delete the old finale video from the talk deck

The finale was recorded again (PR #83). The talk deck's finale slide uses the new video and still,
`/_blob/7ea46e81aac5270845d10c46cad1d77c` and `/_blob/00ffd4e8fd60be4596002a3720353148`. The old video is still in
the deck's asset store, and nothing references it:

- `a8dd69f192524dbadf99aad997994db6`: the old video (video/mp4, 2373019 bytes)

Steps:

1. List the talk deck's assets (`Artifact` list, `scope: "assets"`) and confirm the id is there with that size.
2. Read `project/slides/finale.html` from the talk deck and confirm it names the new ids, not this one.
3. Delete the asset (`Artifact` delete with the deck's `url` and the id as `path`).
