# ScalaDays 2026 — "A Brief History of Scala"

Working spec for the talk. Co-presented by Odd and Martin. This document captures the
finalized proposal plus the design decisions and code progression worked out while
drafting it, so the repo has a single source of truth to build slides and samples from.

---

## 1. Proposal (as submitted / to submit)

> **Note:** the title below is written `A brief history Scala`. This is almost
> certainly meant to be **A Brief History of Scala** (restores grammar and the
> *A Brief History of Time* allusion; 24 chars, still within the 60-char limit).
> Confirm before submission.

**Title:** A brief history Scala

**Abstract** (333 chars):

> What can one tiny function teach you about twenty years of Scala? We rewrite
> isPalindrome version by version and let the code tell the story. Watch it grow from
> classic 2.x into the modern 3.x — tail recursion, type classes, extension methods,
> all earning their place. A palindrome reads the same both ways; Scala's history does not.

**Description:**

> Scala has spent over two decades reinventing how to write code. New syntax arrives
> while other idioms slip into retirement, and the obvious way to express something in
> 2010 can look very different by 2026. Rather than march through the changelog, we tell
> that story with the help of a simple function: isPalindrome, as it evolves with new
> Scala versions.
>
> We start with a one-liner and let the problem itself pull in new language machinery,
> one feature at a time — only adding things when they are needed. We will look into
> generalizing from String to Seq[A], using tail recursion with @tailrec, and sequence
> extractors that peel a palindrome from both ends in a single pattern. Asking what
> "equal" even means walks us through type classes as implicits, their given/using
> reincarnation. We close by letting the answer say something more than just true or
> false, contrasting sealed-trait ADTs with Scala 3 enums, and wrapping the whole thing
> as a fluent extension method.
>
> Each step fits on a single slide, and together they become a tour of Scala's evolving
> style — generics, recursion, the implicits-to-givens transition, ADTs, and extension
> methods — showing what the community decided "elegant" should mean.
>
> Audience members leave with a concrete mental timeline of Scala's syntax and idioms,
> a clearer sense of why features were added rather than merely that they were. No prior
> history required — just a fondness for strings that read the same both ways.

---

## 2. Talk thesis and shape

**Thesis:** don't add machinery until the problem demands it. The talk's structure
mirrors its own argument — each generalization of `isPalindrome` drags in exactly the
language feature that solves it, era by era. Occam as method, not just slogan.

**Narrative arc:** concrete → abstract → polished. Start in `String`-land with a real
mess to clean up, generalize to `Seq[A]`, then refine equality, output, and ergonomics.
This reads better than opening abstract.

**Format:** deliberate double act — one presenter defends the old ways, the other
evangelizes the new — to keep trade-offs honest rather than hagiographic. Be upfront
that not every change was an unambiguous win.

**Budget:** 30 minutes. The code progression below is already full; treat the "held in
reserve" items in §5 as cut-first material.

---

## 3. Core code progression (the spine)

Each stage is one slide. The through-line: change one thing, let the consequence pull in
a feature. Honest caveats are called out per stage — say them on stage; they're what
makes it credible rather than nostalgic.

### Stage 0 — the one-liner (early Scala 2)

```scala
def isPalindrome(s: String): Boolean = s == s.reverse
```

Hook: this *already* contains an implicit — `s.reverse` only works because `String` is
enriched to `StringOps` via `augmentString`. Implicits were in the room from line one;
the talk just makes them visible.

Caveat: `s.reverse` allocates a full reversed copy — the "elegant" version is also the
wasteful one.

### Stage 1 — generalize the input (Scala 2)

```scala
def isPalindrome[A](xs: Seq[A]): Boolean = xs == xs.reverse
```

One change (`String` → `Seq[A]`), strictly more capable for free. Still leans on
universal equality — the thread pulled on later.

### Stage 2 — recursive, extractors + `@tailrec` (Scala 2)

```scala
import scala.annotation.tailrec

@tailrec
def isPalindrome[A](xs: Seq[A]): Boolean = xs match {
  case x +: middle :+ y => x == y && isPalindrome(middle)
  case _                => true
}
```

`x +: middle :+ y` peels first and last in one pattern; `@tailrec` proves it's a loop.
The pattern generalized from Stage 1 untouched — `+:`/`:+` never cared it used to be a
`String`.

Caveat: on `List`, `:+` (last/init) is O(n), so this lovely version is quietly O(n²).
Perfect one-slide tie-in to "elegant by default, but know when the data structure
betrays you" — `IndexedSeq`/`Vector` fixes it.

### Stage 3 — equality as a type class (Scala 2 implicits)

Motivation: universal `==` is hardwired; you can't ask for case-insensitive palindromes
without a hook. Equality as a type class, carried by an implicit:

```scala
trait Eq[A] {
  def eqv(x: A, y: A): Boolean
}

object Eq {
  implicit val charCI: Eq[Char] = (x, y) => x.toLower == y.toLower
}

@tailrec
def isPalindrome[A](xs: Seq[A])(implicit eq: Eq[A]): Boolean = xs match {
  case x +: middle :+ y => eq.eqv(x, y) && isPalindrome(middle)
  case _                => true
}
```

Lesson: implicits *are* Scala's type-class mechanism — a defining idea for a history talk.

### Stage 4 — same idea, Scala 3 (`given`/`using`, optional braces)

```scala
import scala.annotation.tailrec

trait Eq[A]:
  def eqv(x: A, y: A): Boolean

given Eq[Char] = (x, y) => x.toLower == y.toLower

@tailrec
def isPalindrome[A](xs: Seq[A])(using eq: Eq[A]): Boolean = xs match
  case x +: middle :+ y => eq.eqv(x, y) && isPalindrome(middle)
  case _                => true
```

The diff between Stage 3 and Stage 4 *is* the headline of the 2→3 transition — read in
seconds. `given` for `implicit val`, `using` for `implicit`, braces gone.

### Stage 5 — make one: the collections redesigns (2.8 `CanBuildFrom`, 2.13 `BuildFrom`)

So far we only *read* collections, which is why the biggest library change in Scala's
history — the 2.8 collections redesign — hasn't shown up. Turn the question around: once
we can check palindromes, *build* one: the shortest palindrome that starts with the input.
`palindromize("abcb") == "abcba"`. It finds the longest suffix that's already a palindrome,
with our own `isPalindrome`, and mirrors only what comes before it. So it takes an `Eq`,
and the type-class thread meets the collections thread in one signature. Only one new
demand comes from the problem: give back the same kind of collection you were given.

The name sits with `isPalindrome`, and it's a verb like the
collection operations it's built from (`reverse`, `map`). It adds the fewest elements
possible, which is also what "palindromize" means on puzzle sites.

```scala
// Scala 2.7 — generic code can only promise a Seq; the empty suffix always matches, so .get is safe
def palindromize[A](xs: Seq[A])(implicit eq: Eq[A]): Seq[A] = {
  val start = (0 to xs.length).find(i => isPalindrome(xs.drop(i))).get
  xs ++ xs.take(start).reverse                                    // "abcb" gives a Seq[Char]
}

// Scala 2.8 — CanBuildFrom: a builder for the caller's own collection type
def palindromize[A, Repr](xs: SeqLike[A, Repr])(implicit eq: Eq[A], bf: CanBuildFrom[Repr, A, Repr]): Repr = {
  val start = (0 to xs.length).find(i => isPalindrome(xs.toSeq.drop(i))).get
  val b = bf(xs.repr)
  b ++= xs.iterator
  b ++= xs.reverseIterator.drop(xs.length - start)
  b.result
}                                                                 // "abcb" gives the String "abcba"

// Scala 2.13 — CanBuildFrom is gone; IsSeq + BuildFrom (and a type-refinement wart)
def palindromize[Repr, A0](xs: Repr)(
    implicit seq: IsSeq[Repr] { type A = A0 }, eq: Eq[A0], bf: BuildFrom[Repr, A0, Repr]): Repr = { ... }

// Scala 3 — same library, but a later using clause may depend on an earlier one
extension [Repr](xs: Repr)(using seq: IsSeq[Repr])
  def palindromize(using eq: Eq[seq.A], bf: BuildFrom[Repr, seq.A, Repr]): Repr =
    val ops = seq(xs)
    val start = (0 to ops.length).find(i => ops.toSeq.drop(i).isPalindrome).get
    val b = bf.newBuilder(xs)
    b ++= ops
    b ++= ops.reverseIterator.drop(ops.length - start)
    b.result()
```

`reverseIterator.drop(length - start)` yields the elements before the suffix, reversed.
The `start` line is the same search in every version: "find the longest palindromic
suffix". Say out loud that it's O(n²): a linear version exists
(based on the KMP string-matching algorithm), but like Manacher's it's an algorithm topic,
not a language one.

Beats, in order:
- **2.7 → 2.8:** "the answer keeps your type". The signature grows `Repr` and an
  implicit, which is the famous "`CanBuildFrom` in the Scaladoc" moment. Be honest here:
  it worked, but the signatures scared people.
- **2.12 → 2.13:** the 2.8 version *stops compiling* for `String`: "found
  `WrappedString`, required `String`", because `StringOps` is no longer a collection.
  `IsSeq`/`BuildFrom` replace it, and the body barely changes (`bf(xs.repr)` →
  `bf.newBuilder(xs)`). Ordinary code lost `CanBuildFrom` entirely, because `List(...).map`
  gets its type from `SeqOps[A, CC, C]`. It survives only where the source isn't a
  collection class, like `String`.
- **Method syntax rides along** (`xs.palindromize`), and the wrapper changes shape with each
  redesign. It wraps a `Seq[A]` up to 2.7, a `SeqLike[A, Repr]` in 2.8–2.12, and in 2.13 any
  `Repr` with an `IsSeq`, via an `implicit def` to `PalindromeOps[Repr, seq.type]`. That
  last one is no longer a value class and needs `import scala.language.implicitConversions`,
  but it finally makes `"abc".palindromize` and `"racecar".isPalindrome` work on a Scala 2
  `String`. Worth one sentence on the 2.13 slide; the code is in the repo, not on the slide.
- **2.13 → 3:** the `{ type A = A0 }` refinement, the wrapper class, the `seq.type` trick
  and the feature import all disappear, because a `using` clause can depend on an earlier
  one. One extension gives both `"abc".palindromize` and `palindromize("abc")`.

Cost: one slide for 2.7/2.8 and one for 2.13/3. If the clock is tight, show only the 2.8
signature and the Scala 3 version, and mention 2.13 in one line.

### Stage 6 — the closer: extension method (`implicit class` → `extension`)

```scala
// Scala 2 — the function lives in object Palindrome; the value class delegates to it
implicit class PalindromeOps[A](private val xs: Seq[A]) extends AnyVal {
  def isPalindrome(implicit eq: Eq[A]): Boolean = Palindrome.isPalindrome(xs)
}

// Scala 3 — the extension *is* the function: isPalindrome(xs) and xs.isPalindrome both work
extension [A](xs: Seq[A])(using eq: Eq[A])
  @tailrec
  def isPalindrome: Boolean = xs match
    case x +: middle :+ y => eq.eqv(x, y) && middle.isPalindrome
    case _                => true
```

End on `Seq("a", "b", "a").isPalindrome` — the function has grown from a string-only
one-liner into a generic, fluent method, every feature having earned its place.

Bonus contrast: in Scala 3 `"racecar".isPalindrome` also works, because an extension's
receiver may be converted (`String` → `Seq[Char]`). The Scala 2 implicit class can't do
that — implicit views don't chain — so Scala 2 needs `"racecar".toList.isPalindrome`.

---

## 3a. The samples in this repo

Each version directory (`2/5` … `3/9`) implements the *end state* of §3 with the best
features of that release, so neighbouring versions differ only in what the language
changed. `STATE.md` §4 maps each stage to the version that first shows it; `DESIGN.md`
explains the choices. The samples differ from the slides above in two ways:

- **`Eq` default.** The slides make case-insensitive `Eq[Char]` *the* instance. The
  samples use a universal default (`==`) in `Eq`'s companion plus an opt-in
  `Eq.caseInsensitive`, passed explicitly or put in scope. This keeps
  `Seq("a", "b", "a")` working and case-sensitive checks the default.
- **Scala 2 wrapper shape.** For `xs.palindromize` to keep the collection type, the Scala 2
  wrapper carries `Repr`: `SeqLike[A, Repr]` in 2.8–2.12, and an `IsSeq`-based wrapper in
  2.13. The slides show only the `palindromize` signatures.

---

## 4. CanEqual — reframed (include only if pacing allows)

Originally pitched as "stop me comparing a number to a string." **That pitch is wrong
for this example** and should not be used: inside `isPalindrome[A](xs: Seq[A])` both
elements have static type `A`, so a cross-type comparison cannot occur.

The accurate and more interesting point: under `strictEquality`, `A == A` for an
**abstract** type does not compile, because there is no ambient reflexive
`given [A]: CanEqual[A, A]` (deliberately — such an instance would gut the feature).
`CanEqual` answers "is this type meant to be compared with `==` at all?", not "are these
two types compatible?".

```scala
import scala.language.strictEquality
import scala.annotation.tailrec

@tailrec
def isPalindrome[A](xs: Seq[A])(using CanEqual[A, A]): Boolean = xs match
  case x +: middle :+ y => x == y && isPalindrome(middle)
  case _                => true
```

Where it bites: **generic code**. A `class Widget` with only reference identity has no
`CanEqual`, so `isPalindrome(Seq(Widget(), Widget()))` is rejected — strict equality
forces generic authors to declare their elements genuinely equatable. `derives CanEqual`
on your own ADTs is the natural follow-up beat.

Framing for the slide: "here's the surprising tax strict equality puts on polymorphism,
and why it's worth paying" — not "1 == \"1\" is now an error."

**Proposal alignment note:** CanEqual and opaque types were trimmed from the submitted
description (Option A) to keep the 30-min scope lean. If either is added back on stage,
update the description's paragraph-3 tour list accordingly ("equality safety",
"type modelling").

---

## 5. Held in reserve (cut-first / optional)

- **Opaque types vs value classes** (strong 2→3 beat). Natural home for input
  normalization ("A man, a plan, a canal: Panama") — encode "already normalized" in the
  type. Punchline: value classes *promise* zero-cost but box in generic/`Array`/pattern
  contexts; opaque types deliver the promise. Flows best while still in `String`-land,
  before the `Seq[A]` generalization.

  ```scala
  // Scala 2 — value class
  class Normalized(val value: String) extends AnyVal
  object Normalized {
    def apply(s: String): Normalized =
      new Normalized(s.filter(_.isLetter).map(_.toLower))
  }

  // Scala 3 — opaque type
  opaque type Normalized = String
  object Normalized:
    def apply(s: String): Normalized = s.filter(_.isLetter).map(_.toLower)
    extension (n: Normalized) def value: String = n
  ```

- **`@main` vs `object Demo extends App`** (almost free). Even the demo entry point is a
  2→3 diff. One throwaway line for a smile.

- **`inline` compile-time check** (finale / gag). Reject a non-palindrome string literal
  at *compile time* via `inline` + `compiletime.error`. Pure spectacle for Scala 3
  metaprogramming. Fiddly to demo live — strictly bonus if the clock allows.

- **Variance + `Nothing`** (skippable). One `Nil` serves every element type because
  `Seq` is covariant and `Nothing` is the bottom type. A *depth* aside, not an
  *evolution* beat (variance is unchanged since early 2.x).

**Deliberately NOT included:** abstracting the container to `F[_]` with a higher-kinded
type class. Tempting and very Scala, but it violates the Occam discipline the talk
preaches. Works better as a *joke* — "we could keep generalizing… we're not going to" —
than an actual stage. Manacher's algorithm is likewise out: it's an algorithm/perf
topic, not a language-history one, and would staple a second talk onto this one.

---

## 6. Open items

- [ ] Confirm title: `A brief history Scala` → **A Brief History of Scala**?
- [ ] Decide whether Stage 5 (`palindromize`, the 2.8 and 2.13 collections redesigns) stays:
      it adds about two slides to a budget §2 already calls full. If it stays, consider
      adding "the collections redesigns" to the description's paragraph-3 tour list.
- [ ] The description (§2) still promises "contrasting sealed-trait ADTs with Scala 3
      enums", but the code has no result ADT any more. Either say it in one line on the
      3.0 slide (`sealed trait` + `case object`/`case class` → `enum`) or drop "ADTs"
      from the description if it can still be edited.
- [ ] Decide final scope: keep §4 CanEqual and/or §5 opaque types in, or leave cut
      (and keep description paragraph-3 list in sync either way).
- [ ] Map the old-ways/new-ways split concretely to Odd vs Martin for the double act.
- [x] Fill in the delegations in Stage 6 from the canonical implementation (the
      `Eq`-carrying recursive version; see §3a and the repo's version directories).
