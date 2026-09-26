#!/usr/bin/env python3
"""Generates EVOLUTION.md: how the code changes from each Scala version to the next.

Usage: tools/evolution.py            regenerate EVOLUTION.md
       tools/evolution.py --check    fail if EVOLUTION.md is out of date (or a NOTES.md is missing or stray)

Everything except the prose comes from the code: the versions are the directories 2/<minor> and 3/<minor>, each
version is read from the `// Scala x.y.z` header of its src/Palindrome.scala, and the diffs compare each version's
source and test suite with the previous version's (ignoring the header line).

The prose comes from <version dir>/NOTES.md. The first version and every version whose source or tests differ from
the previous version's must have one; versions identical to the previous one must not. The first line of NOTES.md is
`# <one-line summary>`, used in the overview table and as the section title; the rest is the section's text.
"""

import difflib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "EVOLUTION.md"
SOURCE = "src/Palindrome.scala"
TESTS = "test/src/PalindromeSuite.scala"

# Below this similarity a diff is mostly noise (the 2 -> 3 rewrite), so both versions are shown in full instead.
MIN_DIFF_SIMILARITY = 0.5


class Version:
    def __init__(self, directory: Path):
        self.dir = directory
        self.rel = directory.relative_to(ROOT).as_posix()
        source = (directory / SOURCE).read_text()
        header, _, self.body = source.partition("\n")
        match = re.fullmatch(r"// Scala (\d+\.\d+\.\d+)", header)
        if not match:
            sys.exit(f"{self.rel}/{SOURCE}: expected a '// Scala x.y.z' header, found '{header}'")
        self.version = match.group(1)
        self.source = source
        self.tests = (directory / TESTS).read_text()
        notes = directory / "NOTES.md"
        self.notes = notes.read_text().strip() if notes.exists() else None

    @property
    def label(self) -> str:
        return f"Scala {self.version}"

    @property
    def anchor(self) -> str:
        return "scala-" + self.version.replace(".", "")

    def title_and_text(self) -> tuple[str, str]:
        first, _, rest = self.notes.partition("\n")
        if not first.startswith("# "):
            sys.exit(f"{self.rel}/NOTES.md: the first line must be '# <one-line summary>'")
        return first[2:].strip(), rest.strip()


def versions() -> list[Version]:
    dirs = [d for d in ROOT.glob("[0-9]/[0-9]*") if (d / SOURCE).exists()]
    found = [Version(d) for d in dirs]
    return sorted(found, key=lambda v: tuple(int(n) for n in v.version.split(".")))


def unified(before: str, after: str, before_name: str, after_name: str) -> str:
    return "".join(difflib.unified_diff(
        before.splitlines(keepends=True), after.splitlines(keepends=True), before_name, after_name, n=3))


def similarity(before: str, after: str) -> float:
    return difflib.SequenceMatcher(None, before.splitlines(), after.splitlines(), autojunk=False).ratio()


def fenced(language: str, text: str) -> str:
    return f"```{language}\n{text.rstrip()}\n```"


def change(label: str, previous: Version, current: Version, before: str, after: str, path: str, language: str) -> str:
    """The change to one file between two versions: a diff, or both files in full when they're too different."""
    if similarity(before, after) >= MIN_DIFF_SIMILARITY:
        return fenced("diff", unified(before, after, f"{previous.rel}/{path}", f"{current.rel}/{path}"))
    return (f"{label} rewritten; before ({previous.label}):\n\n{fenced(language, before)}\n\n"
            f"after ({current.label}):\n\n{fenced(language, after)}")


def render(all_versions: list[Version]) -> str:
    problems = []
    rows, sections = [], []
    introduced = None  # the version that introduced the current code

    for i, current in enumerate(all_versions):
        previous = all_versions[i - 1] if i > 0 else None
        source_changed = previous is None or previous.body != current.body
        tests_changed = previous is None or previous.tests != current.tests
        changed = source_changed or tests_changed

        if changed and current.notes is None:
            reason = "the first version" if previous is None else "different from the previous version"
            problems.append(f"{current.rel}/NOTES.md is missing: {current.label} is {reason}")
            continue
        if not changed:
            if current.notes is not None:
                problems.append(f"{current.rel}/NOTES.md is stray: {current.label} is identical to {previous.label}")
            rows.append(f"| {current.label} | — | — | identical to {introduced.label} |")
            continue

        introduced = current
        title, text = current.title_and_text()
        what = ", ".join(p for p, c in (("source", source_changed), ("tests", tests_changed)) if c)
        if previous is None:
            source_cell = tests_cell = "baseline"
        else:
            source_cell = "✓" if source_changed else "—"
            tests_cell = "✓" if tests_changed else "—"
        rows.append(f"| [{current.label}](#{current.anchor}) | {source_cell} | {tests_cell} | {title} |")

        parts = [f'<a id="{current.anchor}"></a>', f"## {current.label}: {title}", ""]
        if previous is not None:
            parts.append(f"*Compared with {previous.label}; changes: {what}.*\n")
        parts.append(text)
        if previous is None:
            parts += ["", f"`{current.rel}/{SOURCE}`:", "", fenced("scala", current.source)]
        else:
            if source_changed:
                parts += ["", "**Source**", "",
                          change("Source", previous, current, previous.body, current.body, SOURCE, "scala")]
            if tests_changed:
                parts += ["", "**Tests**", "",
                          change("Tests", previous, current, previous.tests, current.tests, TESTS, "scala")]
        sections.append("\n".join(parts))

    if problems:
        sys.exit("tools/evolution.py:\n  " + "\n  ".join(problems))

    last = all_versions[-1]
    final = "\n".join([
        '<a id="final"></a>',
        f"## Final: {last.label}",
        "",
        f"The complete `{last.rel}/{SOURCE}`, the end point of the tour:",
        "",
        fenced("scala", last.source),
    ])

    return "\n".join([
        "# Evolution of the Code Across Scala Versions",
        "",
        "<!-- Generated by tools/evolution.py from the version directories and their NOTES.md files.",
        "     Do not edit by hand: change the code or a NOTES.md, then run tools/evolution.py. -->",
        "",
        "How `Palindrome.scala` (and its test suite) changes from each Scala version to the next: the basis for the",
        "slides of *A Brief History of Scala* (`scaladays-2026-talk.md`). Every version implements the same design",
        "with the best features of its release (see `STATE.md` §4), so each diff shows only what the language changed.",
        "Diffs ignore the `// Scala x.y.z` header line.",
        "",
        "## Overview",
        "",
        "| Version | Source | Tests | What changes |",
        "|---------|--------|-------|--------------|",
        *rows,
        "",
        *[s + "\n" for s in sections],
        final,
        "",
    ])


def main() -> None:
    check = sys.argv[1:] == ["--check"]
    if sys.argv[1:] and not check:
        sys.exit(__doc__)
    content = render(versions())
    if check:
        if not OUTPUT.exists() or OUTPUT.read_text() != content:
            sys.exit("EVOLUTION.md is out of date: run tools/evolution.py")
        print("EVOLUTION.md is up to date")
    else:
        OUTPUT.write_text(content)
        print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
