# Project State & Architecture

This document maintains the complete state, module matrix, architecture, and conventions of the **palindrome** project so that assistants and developers do not need to re-analyze the entire repository on every session.

---

## 1. Project Overview

The project is a showcase ("A tour of Scala versions in the view of isPalindrome") containing **19 subprojects**, each implementing a palindrome checker function in a specific Scala release from `2.5` to `3.9`, demonstrating language evolution (overloading, default arguments, extension methods, top-level definitions).

- **Repository**: `ScalaCrypto/palindrome`
- **Main Branch**: `main`
- **Build Tool**: Mill 1.1.10 (`./mill`, `build.mill.yaml`)
- **JVM Configuration**: Default JVM `graalvm-oracle:25` in `build.mill.yaml`; Scala `3.0`, `3.1`, and `3.2` specify `jvmId: temurin:17` in their respective `package.mill.yaml`.

---

## 2. Subproject & Version Matrix

| Directory | Scala Version | Test Framework | ScalaTest Version | Java / JVM Override | Language Features Used |
|-----------|--------------|----------------|-------------------|---------------------|------------------------|
| `2/5`     | `2.5.1`      | ScalaTest      | `0.9.5`           | Default             | `object Palindrome`, method overloading (no default args, no extensions) |
| `2/6`     | `2.6.1`      | ScalaTest      | `0.9.5`           | Default             | `object Palindrome`, method overloading |
| `2/7`     | `2.7.7`      | ScalaTest      | `1.3`             | Default             | `object Palindrome`, method overloading |
| `2/8`     | `2.8.2`      | ScalaTest      | `1.8`             | Default             | `object Palindrome`, default argument values (`ignore: List[Char] = Nil`) |
| `2/9`     | `2.9.3`      | ScalaTest      | `1.9.2`           | Default             | `object Palindrome`, default arguments |
| `2/10`    | `2.10.7`     | ScalaTest      | `3.0.9`           | Default             | `object Palindrome`, default arguments |
| `2/11`    | `2.11.12`    | ScalaTest      | `3.2.18`          | Default             | `object Palindrome`, default arguments |
| `2/12`    | `2.12.21`    | ScalaTest      | `3.2.19`          | Default             | `object Palindrome`, default arguments |
| `2/13`    | `2.13.18`    | ScalaTest      | `3.2.19`          | Default             | `object Palindrome`, default arguments |
| `3/0`     | `3.0.2`      | ScalaTest      | `3.2.11`          | `temurin:17`        | Top-level functions, `extension (s: String)`, `object Palindrome` wrapper |
| `3/1`     | `3.1.3`      | ScalaTest      | `3.2.19`          | `temurin:17`        | Top-level functions, `extension (s: String)`, `object Palindrome` wrapper |
| `3/2`     | `3.2.2`      | ScalaTest      | `3.2.19`          | `temurin:17`        | Top-level functions, `extension (s: String)`, `object Palindrome` wrapper |
| `3/3`     | `3.3.8`      | ScalaTest      | `3.2.19`          | Default             | Top-level functions, `extension (s: String)`, `object Palindrome` wrapper |
| `3/4`     | `3.4.3`      | ScalaTest      | `3.2.19`          | Default             | Top-level functions, `extension (s: String)`, `object Palindrome` wrapper |
| `3/5`     | `3.5.2`      | ScalaTest      | `3.2.19`          | Default             | Top-level functions, `extension (s: String)`, `object Palindrome` wrapper |
| `3/6`     | `3.6.4`      | ScalaTest      | `3.2.19`          | Default             | Top-level functions, `extension (s: String)`, `object Palindrome` wrapper |
| `3/7`     | `3.7.4`      | ScalaTest      | `3.2.19`          | Default             | Top-level functions, `extension (s: String)`, `object Palindrome` wrapper |
| `3/8`     | `3.8.4`      | ScalaTest      | `3.2.19`          | Default             | Top-level functions, `extension (s: String)`, `object Palindrome` wrapper |
| `3/9`     | `3.9.0`      | ScalaTest      | `3.2.19`          | Default             | Top-level functions, `extension (s: String)`, `object Palindrome` wrapper |

---

## 3. Directory Layout & File Structure

```
palindrome/
├── build.mill.yaml                 # Root Mill configuration (mill-version: 1.1.10, default JVM)
├── mill                            # Mill executable script
├── mill-build/
│   └── src/
│       └── VersionModule.scala     # Shared trait VersionModule with test module & default scalaTestDep
├── 2/
│   ├── package.mill.yaml           # Scala 2 group module definition
│   ├── <5..13>/
│   │   ├── package.mill.yaml       # Subproject build definition (extends VersionModule, scalaVersion, etc.)
│   │   ├── src/
│   │   │   └── Palindrome.scala    # Implementation (starts with `// Scala <version>` comment)
│   │   └── test/
│   │       └── src/
│   │           └── PalindromeSuite.scala # Test suite (FunSuite for <=2.7, AnyFunSuite for >=2.8)
├── 3/
│   ├── package.mill.yaml           # Scala 3 group module definition
│   └── <0..9>/
│       ├── package.mill.yaml       # Subproject build definition (extends VersionModule, scalaVersion, etc.)
│       ├── src/
│       │   └── Palindrome.scala    # Implementation (starts with `// Scala <version>` comment)
│       └── test/
│           └── src/
│               └── PalindromeSuite.scala # Test suite (AnyFunSuite)
├── STATE.md                        # This project state file
├── readme.md                       # Repository readme
└── LICENSE                         # Apache 2.0 License
```

---

## 4. API & Implementation Patterns Across Versions

### Source Header Comment
Every `Palindrome.scala` file begins with the Scala version comment at line 1:
```scala
// Scala <version>
```

### Scala 2.5 – 2.7 (No Default Arguments, No Extensions)
```scala
// Scala 2.5.1
object Palindrome {
  def isPalindrom(s: String): Boolean = isPalindrom(s, Nil)

  def isPalindrom(s: String, ignore: List[Char]): Boolean = {
    if (s == null) false
    else {
      val clean = s.filter(c => !ignore.contains(c))
      clean == clean.reverse
    }
  }

  def isPalindrome(s: String): Boolean = isPalindrom(s)
  def isPalindrome(s: String, ignore: List[Char]): Boolean = isPalindrom(s, ignore)
}
```

### Scala 2.8 – 2.13 (Default Parameters)
```scala
// Scala 2.13.18
object Palindrome {
  def isPalindrom(s: String, ignore: List[Char] = Nil): Boolean = {
    if (s == null) false
    else {
      val clean = s.filter(c => !ignore.contains(c))
      clean == clean.reverse
    }
  }

  def isPalindrome(s: String, ignore: List[Char] = Nil): Boolean = isPalindrom(s, ignore)
}
```

### Scala 3.0 – 3.9 (Extensions, Top-Level Functions, Companion Object)
```scala
// Scala 3.9.0
extension (s: String) {
  def isPalindrom: Boolean = isPalindrom(Nil)
  def isPalindrom(ignore: List[Char]): Boolean = {
    if (s == null) false
    else {
      val clean = s.filter(c => !ignore.contains(c))
      clean == clean.reverse
    }
  }

  def isPalindrome: Boolean = isPalindrom
  def isPalindrome(ignore: List[Char]): Boolean = isPalindrom(ignore)
}

def isPalindrom(s: String, ignore: List[Char] = Nil): Boolean = s.isPalindrom(ignore)
def isPalindrome(s: String, ignore: List[Char] = Nil): Boolean = s.isPalindrome(ignore)

object Palindrome {
  def isPalindrom(s: String, ignore: List[Char] = Nil): Boolean = s.isPalindrom(ignore)
  def isPalindrome(s: String, ignore: List[Char] = Nil): Boolean = s.isPalindrome(ignore)
}
```

---

## 5. Development & Contribution Conventions

- **Git Branching**: Create feature branches off `main` named `feature/<feature-name>`.
- **Commit Attribution**: Add trailer `--trailer "Co-authored-by: <Author> <<email>>"`.
- **Pull Requests**: Push feature branches to `origin` and open PR against `main`.
- **Testing**: Run tests via Mill: `./mill 2.13.test`, `./mill 3.9.test`, etc.
