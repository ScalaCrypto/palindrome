# Project State & Architecture

This document maintains the complete state, module matrix, architecture, and conventions of the **palindrome** project so that assistants and developers do not need to re-analyze the entire repository on every session.

---

## 1. Project Overview

The project is a showcase ("A tour of Scala versions in the view of isPalindrome") containing **19 subprojects**, each implementing a palindrome checker function in a specific Scala release from `2.5` to `3.9`, demonstrating language evolution (overloading, default arguments, extension methods, top-level definitions).

The point is the *comparison*: keep each variant small, self-contained, and focused on what changed between Scala versions, not on clever algorithms.

- **Repository**: `ScalaCrypto/palindrome`
- **Main Branch**: `main`
- **Build Tool**: Mill 1.1.10 with the declarative YAML format (`./mill`, `build.mill.yaml`). `mill-version` in `build.mill.yaml` pins it for both the `./mill` wrapper and a Mill 1.x launcher; Mill 0.x can't load this build. Mill can't build Scala 2.5–2.9, so those are built and tested by `legacy/test.sh` instead (see "Pre-2.10 Versions" in section 5).
- **JVM Configuration**: Default JVM `graalvm-oracle:25` in `build.mill.yaml`; Scala `3.0`, `3.1`, and `3.2` specify `jvmId: temurin:17` in their respective `package.mill.yaml`, because those compilers can't read JDK 25 class files. Mill downloads that JDK and uses it for both compiling and running tests.

---

## 2. Subproject & Version Matrix

| Directory | Scala Version | Build | Test Framework | ScalaTest Version | Java / JVM Override | Language Features Used |
|-----------|--------------|-------|----------------|-------------------|---------------------|------------------------|
| `2/5`     | `2.5.1`      | `legacy/test.sh` | Stand-in `FunSuite` | — | JDK 8, JDK 7 `rt.jar` | `object Palindrome`, method overloading (no default args, no extensions), `sameElements` (no content-based collection equality) |
| `2/6`     | `2.6.1`      | `legacy/test.sh` | Stand-in `FunSuite` | — | JDK 8, JDK 7 `rt.jar` | `object Palindrome`, method overloading, `sameElements` |
| `2/7`     | `2.7.7`      | `legacy/test.sh` | ScalaTest | `1.0` | JDK 8, JDK 7 `rt.jar` | `object Palindrome`, method overloading, `sameElements` |
| `2/8`     | `2.8.2`      | `legacy/test.sh` | ScalaTest | `1.8` | JDK 8, JDK 7 `rt.jar` | `object Palindrome`, default argument values (`ignore: Set[Char] = Set.empty`) |
| `2/9`     | `2.9.3`      | `legacy/test.sh` | ScalaTest | `1.9.2` | JDK 8, JDK 7 `rt.jar` | `object Palindrome`, default arguments |
| `2/10`    | `2.10.7`     | Mill | ScalaTest      | `3.0.9`           | Default             | `object Palindrome`, default arguments |
| `2/11`    | `2.11.12`    | Mill | ScalaTest      | `3.2.18`          | Default             | `object Palindrome`, default arguments |
| `2/12`    | `2.12.21`    | Mill | ScalaTest      | `3.2.19`          | Default             | `object Palindrome`, default arguments |
| `2/13`    | `2.13.18`    | Mill | ScalaTest      | `3.2.19`          | Default             | `object Palindrome`, default arguments |
| `3/0`     | `3.0.2`      | Mill | ScalaTest      | `3.2.11`          | `temurin:17`        | Significant indentation (optional braces), top-level `extension (s: String)`, top-level `def isPalindrome` (`@targetName`) |
| `3/1`     | `3.1.3`      | Mill | ScalaTest      | `3.2.19`          | `temurin:17`        | Significant indentation (optional braces), top-level `extension (s: String)`, top-level `def isPalindrome` (`@targetName`) |
| `3/2`     | `3.2.2`      | Mill | ScalaTest      | `3.2.19`          | `temurin:17`        | Significant indentation (optional braces), top-level `extension (s: String)`, top-level `def isPalindrome` (`@targetName`) |
| `3/3`     | `3.3.8`      | Mill | ScalaTest      | `3.2.19`          | Default             | Significant indentation (optional braces), top-level `extension (s: String)`, top-level `def isPalindrome` (`@targetName`) |
| `3/4`     | `3.4.3`      | Mill | ScalaTest      | `3.2.19`          | Default             | Significant indentation (optional braces), top-level `extension (s: String)`, top-level `def isPalindrome` (`@targetName`) |
| `3/5`     | `3.5.2`      | Mill | ScalaTest      | `3.2.19`          | Default             | Significant indentation (optional braces), top-level `extension (s: String)`, top-level `def isPalindrome` (`@targetName`) |
| `3/6`     | `3.6.4`      | Mill | ScalaTest      | `3.2.19`          | Default             | Significant indentation (optional braces), top-level `extension (s: String)`, top-level `def isPalindrome` (`@targetName`) |
| `3/7`     | `3.7.4`      | Mill | ScalaTest      | `3.2.19`          | Default             | Significant indentation (optional braces), top-level `extension (s: String)`, top-level `def isPalindrome` (`@targetName`) |
| `3/8`     | `3.8.4`      | Mill | ScalaTest      | `3.2.19`          | Default             | Significant indentation (optional braces), top-level `extension (s: String)`, top-level `def isPalindrome` (`@targetName`) |
| `3/9`     | `3.9.0`      | Mill | ScalaTest      | `3.2.19`          | Default             | Significant indentation (optional braces), top-level `extension (s: String)`, top-level `def isPalindrome` (`@targetName`) |

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
│   │   ├── src/
│   │   │   └── Palindrome.scala    # Implementation (starts with `// Scala <version>` comment)
│   │   └── test/
│   │       └── src/
│   │           └── PalindromeSuite.scala # Test suite (FunSuite for <=2.10, AnyFunSuite for >=2.11)
├── 3/
│   ├── package.mill.yaml           # Scala 3 group module definition (empty, but required)
│   └── <0..9>/
│       ├── package.mill.yaml       # Subproject build definition (extends VersionModule, scalaVersion, etc.)
│       ├── src/
│       │   └── Palindrome.scala    # Implementation (starts with `// Scala <version>` comment)
│       └── test/
│           └── src/
│               └── PalindromeSuite.scala # Test suite (AnyFunSuite)
├── STATE.md                        # This project state file
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

All versions in each group below are identical apart from the header comment. Every variant implements `isPalindrome`, with an optional `ignore` collection of characters to skip (e.g. a space for sentence palindromes like `"race car"`).

### Scala 2.5 – 2.7 (No Default Arguments, No Extensions)
`object Palindrome` only; default arguments arrived in 2.8, so the empty `ignore` default is an overload.

The comparison is `clean.sameElements(clean.reverse)`, not `==`: before the 2.8 collections redesign, `String.filter` returns an `ArrayBuffer` and `.reverse` a lazy `RandomAccessSeq` view, and `==` between different collection types is `false` even when their elements match (on 2.7, even `"racecar".reverse == "racecar"` is `false`). From 2.8, `filter`/`reverse` on a `String` return a `String` and collections compare by content, so 2.8+ use `==`.
```scala
// Scala 2.5.1
object Palindrome {
  def isPalindrome(s: String): Boolean = isPalindrome(s, Set.empty[Char])

  def isPalindrome(s: String, ignore: Set[Char]): Boolean = {
    if (s == null) false
    else {
      val clean = s.filter(c => !ignore.contains(c))
      clean.sameElements(clean.reverse)
    }
  }
}
```

### Scala 2.8 – 2.13 (Default Parameters)
```scala
// Scala 2.13.18
object Palindrome {
  def isPalindrome(s: String, ignore: Set[Char] = Set.empty): Boolean = {
    if (s == null) false
    else {
      val clean = s.filter(c => !ignore.contains(c))
      clean == clean.reverse
    }
  }
}
```

### Scala 3.0 – 3.9 (Significant Indentation, Top-Level Extension and Def)
Written with significant indentation (optional braces), e.g. `if … then … else`. Scala 3 allows top-level definitions, so there's no `object Palindrome`: the logic lives in a top-level `extension (s: String)` (`"racecar".isPalindrome`, `"race car".isPalindrome(Set(' '))`), and a top-level `def isPalindrome(s, ignore = Set.empty)` wraps it (`isPalindrome("race car", Set(' '))`).

- **Why the extension holds the logic**: inside an extension, an unqualified `isPalindrome(...)` means `s.isPalindrome(...)`, so the extension can't call a top-level `def` of the same name, but the top-level `def` can call the extension.
- **Why `@targetName`**: an extension method compiles to an ordinary method with the receiver as its first parameter, so `isPalindrome(s)(ignore)` and the top-level `isPalindrome(s, ignore)` have the same JVM signature. `@targetName("isPalindromeOf")` gives the top-level `def` a different JVM name.
- **One-argument calls**: `isPalindrome("racecar")` resolves to the extension's `isPalindrome(s)` (Scala prefers the alternative that doesn't need a default argument). Both give the same result.
```scala
// Scala 3.9.0
import scala.annotation.targetName

extension (s: String)
  def isPalindrome: Boolean = isPalindrome(Set.empty[Char])
  def isPalindrome(ignore: Set[Char]): Boolean =
    if s == null then false
    else
      val clean = s.filter(c => !ignore.contains(c))
      clean == clean.reverse

// Same JVM signature as the extension's isPalindrome(s)(ignore), hence the @targetName.
@targetName("isPalindromeOf")
def isPalindrome(s: String, ignore: Set[Char] = Set.empty): Boolean = s.isPalindrome(ignore)
```

---

## 5. Development & Contribution Conventions

- **Git Branching**: Create feature branches off `main` named `feature/<feature-name>`.
- **Commit Attribution**: Add trailer `--trailer "Co-authored-by: <Author> <<email>>"`.
- **Pull Requests**: Push feature branches to `origin` and open PR against `main`. Don't commit feature work directly to `main`.
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
