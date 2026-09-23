# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A tour of Scala versions through the lens of a single function: `isPalindrome`. Each variant shows how the same
problem is expressed idiomatically with the language features and standard library of a particular Scala version.
The point is the *comparison* — keep variants small, self-contained, and focused on what changed between versions,
not on clever algorithms.

## Build

Mill **1.1.10** with the declarative YAML format. The version is pinned by
`mill-version` in `build.mill.yaml`, which both the checked-in `./mill` wrapper and a Mill 1.x launcher read. Mill
0.x can't load this build.

### Layout

One module per Scala minor version, nested by major version. `2/package.mill.yaml` and `3/package.mill.yaml` are
empty but required: without them Mill doesn't discover the version modules below.

```
build.mill.yaml                             # mill-version, mill-jvm-version (graalvm-oracle:25)
mill-build/src/VersionModule.scala          # shared trait for all version modules
2/<minor>/package.mill.yaml                 # 2.5 … 2.13  -> module 2.<minor>
2/<minor>/src/Palindrome.scala
2/<minor>/test/src/PalindromeSuite.scala
3/<minor>/package.mill.yaml                 # 3.0 … 3.9   -> module 3.<minor>
3/<minor>/...
```

Every version module extends `millbuild.VersionModule`, which adds the nested `test` module using **ScalaTest**.
Each `package.mill.yaml` only states what's specific to that version: its exact `scalaVersion` (e.g. `2.13` →
`2.13.18`), plus `scalaTestDep` when it can't use the default `org.scalatest::scalatest:3.2.19` (no single release
covers the whole range; 3.0 needs `3.2.11`, the last one built with it; 2.5–2.7 use the Java-style
`org.scalatest:scalatest`), and `jvmId` when it needs another JDK.

Each version still needs its own file: declaring the versions as nested `object`s in `2/` or `3/package.mill.yaml`
doesn't work, because Mill 1.1.10 can't handle module names that start with a digit when they're declared that way.

### JDK per version

Modules run on Mill's JDK (GraalVM 25) unless they set `jvmId`. Scala 3.0–3.2 can't read JDK 25 class files, so
those three set `jvmId: temurin:17`; Mill downloads that JDK and uses it for both compiling and running tests. (In
Mill 1.x `jvmId` alone is enough — no `-release` flag needed.)

### Known failures

`./mill __.test` passes for 2.10, 2.12, 2.13 and 3.0–3.9. It fails for:

- **2.11**: the test imports `org.scalatest.FunSuite`, which ScalaTest 3.2.18 doesn't have.
- **2.5–2.9**: dependency resolution fails — Mill needs `scala-reflect`, which doesn't exist before Scala 2.10.

Use `-k` to keep going past these when running everything.

### Common commands

```bash
./mill __.compile        # compile every version
./mill 3.9.compile       # compile one version
./mill 3.9.test          # run one version's tests
./mill -k __.test        # run all tests, continuing past failing versions
./mill resolve __.test   # list test modules
```

## Code

Each `src/Palindrome.scala` starts with a `// Scala x.y.z` comment naming its exact version.

- **Scala 3:** the logic lives in a top-level `extension (s: String)` (`"racecar".isPalindrome`), and
  `object Palindrome` wraps it (`Palindrome.isPalindrome(s)`).
- **Scala 2:** only `object Palindrome`, since Scala 2 has no extensions or top-level definitions. From 2.8 the empty
  `ignore` default is a default argument; 2.5–2.7 predate default arguments, so they use an overload instead.

Every variant offers both spellings: `isPalindrom` (the original) and `isPalindrome` (an alias). Both take an
optional `ignore` collection of characters to skip, e.g. a space for sentence palindromes like `"race car"`.

## Workflow

- Don't commit directly to `main` for feature work — use a branch and a PR.
