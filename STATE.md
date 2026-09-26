# Project State & Architecture

This document maintains the complete state, module matrix, architecture, and conventions of the **palindrome** project so that assistants and developers do not need to re-analyze the entire repository on every session.

---

## 1. Project Overview

The project is a showcase ("A tour of Scala versions in the view of isPalindrome") containing **19 subprojects**, each implementing the same palindrome checker in a specific Scala release from `2.5` to `3.9`. It is the sample code for the ScalaDays 2026 talk *A Brief History of Scala* (`scaladays-2026-talk.md`; the choice of `isPalindrome` as the running example is in `scala-history-talk-problem-selection.md`).

Every version implements the same design: a generic `isPalindrome` over `Seq[A]`, element equality as an `Eq` type class, a `PalindromeResult` ADT that reports where a non-palindrome breaks, and method syntax (`xs.isPalindrome`). Each version writes that design with the best features its Scala release has, so the diff between neighbouring versions shows what the language gained (see section 4).

The point is the *comparison*: keep each variant small, self-contained, and focused on what changed between Scala versions, not on clever algorithms. Following the talk's thesis, don't add machinery the problem doesn't need. Design decisions and rejected alternatives are logged in `DESIGN.md`.

- **Repository**: `ScalaCrypto/palindrome`
- **Main Branch**: `main`
- **Build Tool**: Mill 1.1.10 with the declarative YAML format (`./mill`, `build.mill.yaml`). `mill-version` in `build.mill.yaml` pins it for both the `./mill` wrapper and a Mill 1.x launcher; Mill 0.x can't load this build. Mill can't build Scala 2.5–2.9, so those are built and tested by `legacy/test.sh` instead (see "Pre-2.10 Versions" in section 5).
- **JVM Configuration**: Default JVM `graalvm-oracle:25` in `build.mill.yaml`; Scala `3.0`, `3.1`, and `3.2` specify `jvmId: temurin:17` in their respective `package.mill.yaml`, because those compilers can't read JDK 25 class files. Mill downloads that JDK and uses it for both compiling and running tests.

---

## 2. Subproject & Version Matrix

What each version changes in the code, with the diffs, is in `EVOLUTION.md` (see "The Evolution Document" in section 4).

| Directory | Scala Version | Build | Test Framework | ScalaTest Version | Java / JVM Override |
|-----------|--------------|-------|----------------|-------------------|---------------------|
| `2/5`     | `2.5.1`      | `legacy/test.sh` | Stand-in `FunSuite` | — | JDK 8, JDK 7 `rt.jar` |
| `2/6`     | `2.6.1`      | `legacy/test.sh` | Stand-in `FunSuite` | — | JDK 8, JDK 7 `rt.jar` |
| `2/7`     | `2.7.7`      | `legacy/test.sh` | ScalaTest | `1.0` | JDK 8, JDK 7 `rt.jar` |
| `2/8`     | `2.8.2`      | `legacy/test.sh` | ScalaTest | `1.8` | JDK 8, JDK 7 `rt.jar` |
| `2/9`     | `2.9.3`      | `legacy/test.sh` | ScalaTest | `1.9.2` | JDK 8, JDK 7 `rt.jar` |
| `2/10`    | `2.10.7`     | Mill | ScalaTest      | `3.0.9`           | Default             |
| `2/11`    | `2.11.12`    | Mill | ScalaTest      | `3.2.18`          | Default             |
| `2/12`    | `2.12.21`    | Mill | ScalaTest      | `3.2.19`          | Default             |
| `2/13`    | `2.13.18`    | Mill | ScalaTest      | `3.2.19`          | Default             |
| `3/0`     | `3.0.2`      | Mill | ScalaTest      | `3.2.11`          | `temurin:17`        |
| `3/1`     | `3.1.3`      | Mill | ScalaTest      | `3.2.19`          | `temurin:17`        |
| `3/2`     | `3.2.2`      | Mill | ScalaTest      | `3.2.19`          | `temurin:17`        |
| `3/3`     | `3.3.8`      | Mill | ScalaTest      | `3.2.19`          | Default             |
| `3/4`     | `3.4.3`      | Mill | ScalaTest      | `3.2.19`          | Default             |
| `3/5`     | `3.5.2`      | Mill | ScalaTest      | `3.2.19`          | Default             |
| `3/6`     | `3.6.4`      | Mill | ScalaTest      | `3.2.19`          | Default             |
| `3/7`     | `3.7.4`      | Mill | ScalaTest      | `3.2.19`          | Default             |
| `3/8`     | `3.8.4`      | Mill | ScalaTest      | `3.2.19`          | Default             |
| `3/9`     | `3.9.0`      | Mill | ScalaTest      | `3.2.19`          | Default             |

---

## 3. Directory Layout & File Structure

```
palindrome/
├── build.mill.yaml                 # Root Mill configuration (mill-version: 1.1.10, default JVM)
├── mill                            # Mill executable script
├── mill-build/
│   └── src/
│       └── VersionModule.scala     # Shared trait VersionModule with test module & default scalaTestDep
├── legacy/
│   ├── test.sh                     # Builds and tests 2.5–2.9 without Mill
│   └── scalatest-stand-in/         # Minimal FunSuite + Runner stand-in for 2.5 and 2.6
├── 2/
│   ├── package.mill.yaml           # Scala 2 group module definition (empty, but required)
│   ├── <5..13>/
│   │   ├── package.mill.yaml       # Subproject build definition, 2.10–2.13 only (extends VersionModule, scalaVersion, etc.)
│   │   ├── NOTES.md                # What changed from the previous version (only where something did)
│   │   ├── src/
│   │   │   └── Palindrome.scala    # Implementation (starts with `// Scala <version>` comment)
│   │   └── test/
│   │       └── src/
│   │           └── PalindromeSuite.scala # Test suite (FunSuite for <=2.10, AnyFunSuite for >=2.11)
├── 3/
│   ├── package.mill.yaml           # Scala 3 group module definition (empty, but required)
│   └── <0..9>/
│       ├── package.mill.yaml       # Subproject build definition (extends VersionModule, scalaVersion, etc.)
│       ├── NOTES.md                # What changed from the previous version (only where something did)
│       ├── src/
│       │   └── Palindrome.scala    # Implementation (starts with `// Scala <version>` comment)
│       └── test/
│           └── src/
│               └── PalindromeSuite.scala # Test suite (AnyFunSuite)
├── tools/
│   └── evolution.py                # Generates EVOLUTION.md; --check fails if it's stale
├── .github/workflows/
│   └── evolution.yml               # CI: runs tools/evolution.py --check
├── .claude/settings.json           # Claude Code hook: regenerates EVOLUTION.md after edits to versions
├── STATE.md                        # This project state file
├── EVOLUTION.md                    # GENERATED: per-version diffs and notes, the basis for the slides
├── DESIGN.md                       # Design log: decisions, rejected alternatives, verification
├── scaladays-2026-talk.md          # Talk spec: proposal, thesis, the code progression (stages)
├── scala-history-talk-problem-selection.md # Why isPalindrome is the running example
├── CLAUDE.md                       # Claude Code entry point; imports this file
├── .junie/guidelines.md            # Junie entry point; points to this file
├── readme.md                       # Repository readme
└── LICENSE                         # Apache 2.0 License
```

- **Module names**: `2/13` is the Mill module `2.13`, `3/9` is `3.9`, and so on. Only 2.10–2.13 and 3.0–3.9 are Mill modules; `2/5`–`2/9` have no `package.mill.yaml` and are built by `legacy/test.sh`.
- **Group files**: `2/package.mill.yaml` and `3/package.mill.yaml` are empty but required; without them Mill doesn't discover the version modules below.
- **One file per version**: every version needs its own `package.mill.yaml`. Declaring the versions as nested `object`s in the group files doesn't work, because Mill 1.1.10 can't handle module names that start with a digit when declared that way.
- **`VersionModule`**: adds the nested ScalaTest `test` module and a `scalaTestDep` setting (default `org.scalatest::scalatest:3.2.19`). Each `package.mill.yaml` states only what's specific to its version: `scalaVersion`, plus `scalaTestDep` and `jvmId` where the defaults don't fit. No single ScalaTest release covers the whole range: 3.0 needs `3.2.11` (the last release built with Scala 3.0).

---

## 4. API & Implementation Patterns Across Versions

### Source Header Comment
Every `Palindrome.scala` file begins with the Scala version comment at line 1:
```scala
// Scala <version>
```

### The Common Design

Each `Palindrome.scala` defines, in every version:

- **`Eq[A]`**: equality as a type class (`def eqv(x: A, y: A): Boolean`). Its companion holds the default, `universal` (plain `==`), which is found through `Eq`'s implicit scope, and an opt-in `caseInsensitive: Eq[Char]`. The opt-in instance is a plain `val`, not an implicit/given: callers pass it explicitly, or put it in scope as an implicit/given, which beats the companion default because lexical scope is searched first.
- **`PalindromeResult`**: `Palindrome` or `BreaksAt(index)`, the index of the first mismatching element from the front.
- **`checkPalindrome(xs): PalindromeResult`** and **`isPalindrome(xs): Boolean`**, generic over `Seq[A]`, with an `Eq[A]`. A `String` is accepted through the standard `String` → `Seq[Char]` conversion.
- **Method syntax**: `xs.isPalindrome` and `xs.checkPalindrome` on any `Seq`.

The check compares elements pairwise through `Eq`, never whole collections with `==`. That keeps it correct on 2.5–2.7, where `==` between collections isn't content-based (before the 2.8 collections redesign, `"racecar".reverse == "racecar"` is `false`).

The tests are the same in every version, apart from the syntax of each version and these differences:
- **Method syntax on a `String`**: Scala 3 accepts `"racecar".isPalindrome`, because an extension method's receiver may be converted (`String` → `Seq[Char]`). Scala 2 can't do that: implicit views don't chain (`String` → `WrappedString` → `PalindromeOps`), so the Scala 2 tests call `isPalindrome("racecar")` or `"racecar".toList.isPalindrome`.
- **2.5–2.7** use `List` for every sequence: there's no `Vector` before 2.8, and no `Seq(...)` factory in 2.5 and 2.6.
- **3.7–3.9** add a test that uses named pattern matching.

### Mapping of the Talk Stages to Versions

| Talk stage (`scaladays-2026-talk.md` §3) | First version with that idiom in the code |
|---|---|
| 1. Generalize to `Seq[A]` | 2.5 |
| 2. Recursion: `@tailrec` / `x +: middle :+ y` | 2.8 (`@tailrec`) / 2.10 (extractors) |
| 3. `Eq` type class via `implicit` | 2.5 (lambda instances from 2.12) |
| 4. `given`/`using`, optional braces | 3.0 (`[A: Eq as eq]` from 3.6) |
| 5. Result ADT: `sealed trait` → `enum` | 2.5 → 3.0 |
| 6. Extension method: `implicit def` → `implicit class` → `extension` | 2.5 → 2.10 → 3.0 |

Stage 0 (`s == s.reverse`) is a slide, not a version: it doesn't work before 2.8, where `==` on collections isn't content-based. The talk's reserve material (opaque types, `@main`, `inline`, `CanEqual`, §4–§5 of the talk spec) is not in the code.

### The Evolution Document

`EVOLUTION.md` shows how the code changes from each version to the next. It is the basis for the talk's slides, and
the reference for what each version looks like. It is **generated** by `tools/evolution.py` and never edited by hand:

- **From the code**: the version list (from each `// Scala x.y.z` header), the overview table, the baseline and final
  sources, and the diffs of `src/Palindrome.scala` and the test suite against the previous version (ignoring the
  header). Where a file is mostly rewritten (2.13 → 3.0), both versions are shown in full instead of a diff.
- **From `<version dir>/NOTES.md`**: the prose. Line 1 is `# <one-line summary>`, used as the section title and in
  the overview. The rest explains the change and why the code looks that way. The script requires a `NOTES.md` for the
  first version and for every version whose source or tests differ from the previous one, and rejects one anywhere
  else. So adding, removing or merging a change forces the notes to follow.

---

## 5. Development & Contribution Conventions

- **Git Branching**: Create feature branches off `main` named `feature/<feature-name>`.
- **Commit Attribution**: Add trailer `--trailer "Co-authored-by: <Author> <<email>>"`.
- **Pull Requests**: Push feature branches to `origin` and open PR against `main`. Don't commit feature work directly to `main`.
- **Keep `EVOLUTION.md` current**: after changing any `Palindrome.scala`, `PalindromeSuite.scala` or `NOTES.md`, run
  `tools/evolution.py` and commit the regenerated `EVOLUTION.md` with the change. Also check that the affected
  `NOTES.md` still describes the diff; the script can only enforce that a note exists, not what it says. CI
  (`.github/workflows/evolution.yml`) fails when `EVOLUTION.md` is stale. In Claude Code, a `PostToolUse` hook in
  `.claude/settings.json` runs the generator automatically after every Write/Edit to one of those files, and reports
  a missing or stray `NOTES.md` back to Claude. Other assistants and manual edits must run it themselves.
- **Keep this file current**: `STATE.md` is the single source of project facts for all assistants (`CLAUDE.md` and `.junie/guidelines.md` point here). When a change makes something here stale (a version, a signature, a code example), update it in the same PR.

### Common Commands

```bash
./mill __.compile        # compile every version
./mill 3.9.compile       # compile one version
./mill 3.9.test          # run one version's tests
./mill __.test           # run all Mill-built tests (2.10–2.13, 3.0–3.9)
./mill resolve __.test   # list test modules
legacy/test.sh           # build and test 2.5–2.9 without Mill
legacy/test.sh 2.7 2.9   # ... only some of them
tools/evolution.py       # regenerate EVOLUTION.md
tools/evolution.py --check  # fail if EVOLUTION.md is stale
```

All 19 versions pass: 14 through `./mill __.test` and 5 through `legacy/test.sh`.

### Pre-2.10 Versions (2.5–2.9)

Mill can't build Scala 2.5–2.9, for three independent reasons:

1. **No `scala-reflect`**: Mill always adds `scala-reflect` to the Scala 2 compiler classpath, but it only exists from Scala 2.10 (`scala-library` and `scala-compiler` do exist for 2.5–2.9).
2. **No Zinc compiler bridge**: Mill compiles through Zinc, which needs a `compiler-bridge` per Scala version, and those are published only for 2.10–2.13. This is the fundamental blocker: even with 1 worked around, Mill couldn't compile these versions.
3. **ScalaTest artifact names (2.8, 2.9)**: before 2.10, libraries were published with the full Scala version (`scalatest_2.8.2:1.8`, `scalatest_2.9.3:1.9.2`), not the binary version `::` requests (`scalatest_2.8`).

Scala 2.10 is the dividing line: it split out `scala-reflect`, introduced binary-version artifact names (`_2.10`), and is the oldest version current build tooling supports.

So `2/5`–`2/9` have no `package.mill.yaml`; `legacy/test.sh` builds and tests them by calling each version's own `scalac` directly. It needs coursier's `cs` on the `PATH` (plus `curl` and `tar`), and caches everything under `out/legacy/`:

- **JDK**: these compilers can't read JDK 8+ class files ("bad constant pool tag 18"), and JDK 6/7 aren't available for Apple Silicon. So `scalac` runs on JDK 8 (`cs java-home --jvm zulu:8`) but reads the Java standard library from a JDK 7 `rt.jar` (Azul Zulu 7u352, pinned by SHA-256; x86_64, but it's only read, never run). The option is `-javabootclasspath` on 2.8/2.9 and `-bootclasspath` on 2.5–2.7.
- **ScalaTest**: a ScalaTest release must be built with the same Scala version, because older compilers can't read newer Scala signatures. 2.7 uses ScalaTest `1.0`, 2.8 `1.8`, and 2.9 `1.9.2`, all fetched intransitively.
- **Stand-in for 2.5 and 2.6**: no ScalaTest release with `FunSuite` can be read by those compilers, so `legacy/scalatest-stand-in/` provides a minimal `org.scalatest.FunSuite` (`test`, `assert`) and `org.scalatest.tools.Runner`, compiled together with each version's sources. The test files are the same as for the other versions.
- **Consistency check**: the script's version table must match each `// Scala x.y.z` header comment, or it fails.
