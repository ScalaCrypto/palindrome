# A Brief History of Scala: the bullets

The alternative to `script.md`: the same talk, slides, clicks and timing, with talking points instead of lines.
Martin and Odd try both and keep one.

## How to read this file

- Each `MARTIN:` or `ODD:` line is one point to make in your own words, not a line to learn. In the presenter
  view they're the speaker notes, as in `script.md`: Odd's on the left in blue, Martin's on the right in orange,
  in the order they come up. A `BOTH:` point is said together.
- Words in "quotes" are the punchlines: say those as written, or skip them. Everything else is a prompt.
- The roles are the script's: Martin, the enthusiast, introduces each step and holds the clicker; Odd, the skeptic,
  says how it works and what it costs, and comes round to Scala over the talk (2.12: "I concede", 3.0: "almost
  moved", the end: "I'll give you that one").
- `**bold**` marks a line's key words: a glance at them should give its gist. The presenter view shows them bold
  (E switches it off and on), as do the practice PDFs; the artifact's plain-text notes drop the marks. Bold the
  concepts, not the filler: a few words per line, never a whole line.
- `[click]` at the start of a point: click, then make it. The slide has exactly as many as it has builds; the build
  fails otherwise. The click to the next slide comes after the last point, unmarked.
- Lines starting with `>` are stage directions. Each slide's heading gives its number, its id in the deck, roughly
  how long it takes, and the clock at its start. The timing checkpoints are `script.md`'s.
- A bubble is on screen while you talk, so no point repeats one's words (the build checks four words in a row).

---

## 1 · cover — A Brief History of Scala · 30 s · 0:00

> Odd says "And I'm Odd." in Martin's rhythm, then a beat, then "That's also my name."

MARTIN: **Hi Berlin**, I'm Martin
ODD: "And I'm Odd. ... **That's also my name**."
MARTIN: **Twenty years of Scala**, told through **one tiny function**
ODD: Here to make sure **nobody gets sentimental**

## 2 · oneliner — It starts as a one-liner · 45 s · 0:30

MARTIN: **isPalindrome**: a String **equals its reverse**. Ship it
ODD: In 2007 **reverse isn't a String**, so the comparison **always fails**
MARTIN: [click] **Fixed**, and still **one line**
ODD: It **copies the string twice** to compare it with itself
MARTIN: [click] **palindromize**: **append the reverse**
ODD: "abc" gets **three more letters** when **two would do**

## 3 · goal — Callable as methods · 45 s · 1:15

MARTIN: The goal: **any sequence**, **any element type**, called as **methods**
ODD: Including **on a String**, which **isn't a Seq**
MARTIN: [click] palindromize **returns the type you gave it**, adding only what it needs
ODD: **Same type out as in**: that costs **two collection redesigns**
MARTIN: [click] **Case-insensitive**: **Racecar** still counts
ODD: So the **caller decides** what **"equal"** means

## 4 · eq — Seq[A] needs Equality for A · 25 s · 2:00

ODD: Double-equals **never asks the caller**
MARTIN: So equality becomes a **type class**
ODD: Plus a **case-insensitive instance for Char**
MARTIN: **Back to 2007** to write it

## 5 · tc2-5 — Scala 2.5 · 2007 · 20 s · 2:25

MARTIN: **2.5, May 2007**: 289 commits by **ten people**
ODD: "That's not a community, that's a **team lunch**."

## 6 · f2-5 — New in Scala 2.5 · 25 s · 2:45

MARTIN: **Type constructor polymorphism**, **placeholder lambdas**, **case clauses as functions**
ODD: We use **none of them**
MARTIN: Scala **already has everything** this design needs
ODD: **Generics, implicits, anonymous classes**: all there, just **a lot of typing**

## 7 · e2-5 — Equality is a type class · 40 s · 3:10

MARTIN: **Our Eq** in 2.5
MARTIN: [click] The **instances**
ODD: **Anonymous classes**, braces and all: the **Java 6** experience
MARTIN: [click] The **default needs no import**
ODD: In the **companion**: the compiler always looks there, **readers don't**
MARTIN: [click] Case-insensitive is **opt-in**
ODD: A **plain value**: nothing happens **unless you ask**

## 8 · o2-5 — Method syntax through an implicit conversion · 55 s · 3:50

MARTIN: **Method syntax**: Seq has no isPalindrome, and we **can't change Seq**
ODD: [click] So we **wrap it**: a class that **only forwards**
ODD: [click] The **compiler wraps for you**: a **new object on every call**
ODD: **Not on a String**: that takes **two conversions**, and the compiler **does one**
MARTIN: We could write a **second wrapper** just for String
ODD: "**Two wrappers for one method**? I'll wait for a **new Scala version**."

## 9 · m0-again — What's wrong? · 30 s · 4:45

MARTIN: Our **one-liners** again: **what's wrong** with them?
ODD: [click] A **whole copy**, just to compare
MARTIN: [click] Palindromes **longer than they need** to be
ODD: [click] **Strings only**: we want **any sequence**, of anything
MARTIN: 2.5, show us a **better way**

## 10 · m2-5-is — A better way · 25 s · 5:15

MARTIN: **Generic**, with an **implicit Eq**
ODD: [click] **Index arithmetic**, in a **functional language**
MARTIN: It's **tail-recursive**!
ODD: Says who? **Nothing checks it**
MARTIN: Now **palindromize, done properly**

## 11 · m2-5 — A better way · 45 s · 5:40

MARTIN: [click] Find the **longest palindromic suffix**, **mirror only what's before it**
ODD: [click] I **gave it a String** and got a **Seq of Char** back
MARTIN: The best a 2007 **generic signature** can do. **2.8 is coming**
ODD: "Put that on the **tombstone**."

## 12 · tc2-8 — Scala 2.8 · 2010 · 15 s · 6:25

MARTIN: 2.6 and 2.7 **change nothing** in our code. **2.8, 2010**: two and a half thousand commits
ODD: Six hundred by **Paul Phillips**: "That man **was a compiler**."

## 13 · f2-8 — New in Scala 2.8 · 30 s · 6:40

MARTIN: The **big one**: **new collections**, **@tailrec**, **named and default arguments**
ODD: **Broke everybody's code**, and everybody **upgraded anyway**
MARTIN: Why would a palindrome checker **care about collections**?
ODD: palindromize **builds one**, and from 2.8 it can build **the kind you gave it**

## 14 · e2-5-again — Char gets toLower · 5 s · 7:10

MARTIN: First a **small one, in Eq**
ODD: Lowercasing through **java.lang.Character**: **very Java**

## 15 · e2-8 — Char gets toLower · 20 s · 7:15

MARTIN: [click] **Char does it itself** now
ODD: The **smallest win** of the night: allowed

## 16 · m2-5-again — @tailrec · 5 s · 7:35

MARTIN: **Two upgrades** for our methods. First, **@tailrec**

## 17 · m2-8-is — @tailrec · 25 s · 7:40

ODD: [click] Stop being a **tail call** and it's a **compile error**. **Same bytecode**
MARTIN: A **promise you can't break**
ODD: And the **compiler keeps it**. Fine

## 18 · m2-8 — CanBuildFrom keeps the collection type · 50 s · 8:05

> Odd counts the signature's type parameters on his fingers.

MARTIN: The big one: **CanBuildFrom** [click]
ODD: **Repr is the caller's type**; CanBuildFrom supplies a **builder for exactly that**
MARTIN: [click] A **String comes back as a String**!
ODD: **StringOps** wraps it, and its **Repr is String**: reverse too, **no more mkString**
ODD: It works, and it **scared a generation** away from the **Scaladoc**
MARTIN: You got your **String back**
ODD: "I got my String back. And a **therapist**."

## 19 · tc2-9 — Scala 2.9 · 2011 · 15 s · 8:55

MARTIN: **2.9, 2011**
ODD: Paul Phillips, **1,023 commits**: "He wasn't a compiler. **He was the compiler**."

## 20 · f2-9 — New in Scala 2.9 · 15 s · 9:10

MARTIN: **Parallel collections**, the **App trait**, and the one we need: **tails**
ODD: Everyone else upgraded for **parallel collections**. **We came for tails**

## 21 · m2-8-again — tails finds the palindromic suffix · 10 s · 9:25

MARTIN: The **suffix search**: a **range of indices** and an **unchecked get**

## 22 · m2-9 — tails finds the palindromic suffix · 30 s · 9:35

MARTIN: [click] **tails**! **No indices, no get**
ODD: **Every suffix, longest first**; the **first palindrome** says **how much to mirror**
ODD: **Same cost**, **fewer ways to be wrong**: the only metric I trust

## 23 · tc2-10 — Scala 2.10 · 2013 · 20 s · 10:05

MARTIN: **2.10, January 2013**: so many contributors we can show only **sixty**
ODD: The first release that **sorts before its predecessor**. ... "**Alphabetically**."
MARTIN: **Nobody sorts versions alphabetically**
ODD: "**Every build script** in 2013 did."

## 24 · f2-10 — New in Scala 2.10 · 20 s · 10:25

MARTIN: **Three at once**: **implicit classes**, **value classes**, **extractors for both ends** of a sequence
ODD: And **string interpolation**. And **macros**: "I have feelings about macros."
MARTIN: **Not in this talk**

## 25 · o2-8-again — Implicit value classes · 5 s · 10:45

MARTIN: Our **wrapper**, and its **conversion**

## 26 · o2-10 — Implicit value classes · 30 s · 10:50

MARTIN: [click] **One declaration**, and **no allocation**!
ODD: **Usually**: as a **generic type** or in an **array**, it **boxes**
ODD: And its **field must be public**: **every Seq grows a public member**
MARTIN: That's **2.11's problem**

## 27 · m2-9-again — +: and :+ extractors · 5 s · 11:20

MARTIN: Now the **index loop**: **Odd's favourite**

## 28 · m2-10 — +: and :+ extractors · 45 s · 11:25

MARTIN: [click] Look at **that pattern**!
ODD: **First, middle and last** in **one case**. **Pretty**, I admit
MARTIN: [click] The **whole loop** is **one match** on what's left
ODD: On a **List** the **last element costs a walk**, on a **String every step copies**: quietly **n squared**
MARTIN: On a **Vector** it's **effectively constant**
ODD: Ask me in the **Q&A**

## 29 · tc2-11 — Scala 2.11 · 2014 · 10 s · 12:10

MARTIN: **2.11, 2014**: **Jason Zaugg** leads the commits
ODD: The **calm after the storm**

## 30 · f2-11 — New in Scala 2.11 · 15 s · 12:20

MARTIN: **Consolidation**: a **modular library**, case classes beyond **22 fields**
ODD: And ours: **value classes can hide their field**. My 2.10 complaint

## 31 · o2-10-again — Value classes may hide their field · 5 s · 12:35

MARTIN: That **public field**

## 32 · o2-11 — Value classes may hide their field · 20 s · 12:40

MARTIN: [click] **One word**
ODD: **A whole release, for one word**?
MARTIN: You **asked for it**
ODD: "**Thank you, 2.11**."

## 33 · tc2-12 — Scala 2.12 · 2016 · 10 s · 13:00

MARTIN: **2.12, 2016**: built on **Java 8**
ODD: Lambdas **compile to Java's**: Scala **catching up with Java**

## 34 · f2-12 — New in Scala 2.12 · 10 s · 13:10

MARTIN: **SAM conversion**, **traits as interfaces**, a **right-biased Either**
ODD: **Lambdas instead of anonymous classes**? Could be useful

## 35 · e2-8-again — SAM conversion: lambdas implement traits · 5 s · 13:20

MARTIN: Eq, with its **anonymous classes**

## 36 · e2-12 — SAM conversion: lambdas implement traits · 20 s · 13:25

> Odd's first concession: a breath before it.

MARTIN: [click] Now they're **just lambdas**!
ODD: Two anonymous classes, **two lines**. ... "All right. **I concede**. That's just better."
MARTIN: Can I get that **in writing**?
ODD: "**No.**"

## 37 · tc2-13 — Scala 2.13 · 2019 · 20 s · 13:45

> Martin finds Odd's name in the cloud and points at it.

MARTIN: **2.13, 2019**. Wait, Odd, is that **your name** in there?
ODD: "I was **young** and **needed the commits**."
MARTIN: In 2019? "You **weren't that young**." So you're **partly responsible** for what comes next
ODD: "**No comment**."

## 38 · f2-13 — New in Scala 2.13 · 15 s · 14:05

MARTIN: The **second collections rewrite**: **CanBuildFrom is gone**
ODD: "**Rest in peace**. Nobody cried."
MARTIN: In come **IsSeq and BuildFrom**, **LazyList**, **literal types**

## 39 · m2-10-again — IsSeq and BuildFrom · 10 s · 14:20

ODD: Our 2.12 palindromize now hands back a **wrapped String**, **not a String**

## 40 · m2-13 — IsSeq and BuildFrom · 45 s · 14:30

MARTIN: The **2.13 way** [click]
ODD: **IsSeq reads anything as a sequence**, **String too**
ODD: But its **element type** can't be used in the **same parameter list**: an **extra type parameter**, pinned by a **refinement**. A **wart**
MARTIN: [click] The result in a **single call**, and **method syntax on a String**, at last!
ODD: **In our code**. The library could **since 2.10**: **nobody read that Scaladoc**
MARTIN: **Including you**

## 41 · tc3-0 — Scala 3.0 · 2021 · 15 s · 15:15

MARTIN: The **big bang**: **Scala 3, 2021**. **Dotty graduates** after eight and a half years
ODD: A **whole new compiler**: what could possibly **go wrong**
MARTIN: **Surprisingly little**

## 42 · f3-0 — New in Scala 3.0 · 20 s · 15:30

MARTIN: **given and using**, **extension methods**, **optional braces**, **top-level definitions**
ODD: We use **all four**, and every one **deletes code**
MARTIN: Are you... **excited**?
ODD: "**Show me the diff**."

## 43 · e2-12-again — given indentation and extensions · 5 s · 15:50

MARTIN: **Our Eq**, Scala 2 style. **Watch**

## 44 · e3-0 — given indentation and extensions · 40 s · 15:55

MARTIN: [click] The **braces are gone**!
ODD: "**Python developers**, here we come."
MARTIN: [click] Eq gets **an operator**
ODD: **One extension**, for **every type with an Eq**
ODD: [click] **implicit def becomes given**: same thing, **better name**
MARTIN: [click] The **lambdas shrink to underscores**
ODD: "**Very readable**. For **whoever wrote it**."

## 45 · m2-13-again — using extensions · 10 s · 16:35

MARTIN: The **methods**, and the **wrapper class** we've carried since 2.10

## 46 · m3-0-is — using extensions · 20 s · 16:45

MARTIN: isPalindrome **becomes an extension** [click]
ODD: **No object, no wrapper, no conversion**; the old one is **commented out**
MARTIN: **Nobody calls it** anymore

## 47 · m3-0-ops — using extensions · 35 s · 17:05

MARTIN: Now **palindromize** [click] Everything reads like a **method call**
ODD: [click] **IsSeq gets a clause of its own**, so the next clause can use its **element type**
MARTIN: **No extra type parameter, no refinement**
ODD: Same library: the **language fixed the wart**. "I'm... **almost moved**."

## 48 · m3-0 — using extensions · 15 s · 17:40

MARTIN: And **the class**?
ODD: [click] **Nothing left** for it to do
MARTIN: Shall we **delete it**?
ODD: "**Please**."

## 49 · m3-0-clean — using extensions · 5 s · 17:55

> The click to this slide morphs the class away. Let it play; nobody speaks.

## 50 · tc3-6 — Scala 3.6 · 2024 · 15 s · 18:00

MARTIN: 3.1 to 3.5 **change nothing** we use. **Scala 3.6, 2024**
ODD: Technically **3.6.2**: 3.6.0 was **published by accident**
MARTIN: "**We don't talk about 3.6.0**. Or 3.6.1."

## 51 · f3-6 — New in Scala 3.6 · 15 s · 18:15

MARTIN: The **type class story** is finished: **named context bounds**, a **new given syntax**
ODD: **Six releases later**, the **syntax catches up**

## 52 · e3-0-again — The new given syntax · 5 s · 18:30

MARTIN: **Our given**, one more time

## 53 · e3-6 — The new given syntax · 15 s · 18:35

MARTIN: [click] **Read that out loud**
ODD: It reads like the **sentence you'd say anyway**. That's new

## 54 · m3-0-again — Context bounds get names · 5 s · 18:50

MARTIN: And the **methods**

## 55 · m3-6 — Context bounds get names · 30 s · 18:55

MARTIN: [click] The **using clause is gone**!
ODD: Moved into the **type parameter**, and **kept its name**. "I'm **running out of things to complain about**."
MARTIN: isPalindrome **doesn't change**, nor do 3.7 to 3.9 for us: **we're done**
ODD: "**Are we, though?**"

## 56 · cloud4-0 — Scala 4.0 · 15 s · 19:25

> Deadpan. Let the two names sit there.

MARTIN: There is **one more release**: **Scala 4.0**
ODD: Only **two authors** this time
MARTIN: A **very exclusive community**
ODD: "Two authors, **three opinions**."

## 57 · f4-0 — New in Scala 4.0 · 20 s · 19:40

MARTIN: **One feature**: **Prolog extractors**
ODD: **One name twice** in a pattern: both places must **match the same value**
MARTIN: "If you **remember Prolog** from university: **you're welcome**. If you don't: **also welcome**."

## 58 · m3-6-again — Prolog extractors · 5 s · 20:00

MARTIN: **3.6's isPalindrome**. **Watch the match**

## 59 · m4-0 — Prolog extractors · 25 s · 20:05

MARTIN: [click] The **comparison disappears into the pattern**. **Beautiful**!
ODD: **Which equality** would it use? The **caller should decide**
MARTIN: "That's a **4.1 problem**."

## 60 · takeaways — What the palindrome taught us · 40 s · 20:30

> Drop the comedy a notch. Slower, to the room.

MARTIN: **What did one tiny function teach us**?
ODD: The **ideas were all there in 2007**: **generics, type classes, implicit conversions**
MARTIN: Every release made them **cheaper to write**
ODD: **Not every step a pure win**: CanBuildFrom **frightened everyone**, 2.13's refinement was a **detour**
MARTIN: In Scala 3 the code **reads the way we'd explain it**
ODD: ... "I'll **give you that one**."

## 61 · thanks — Thank you · 15 s · 21:10

> Stand together. Leave the QR code up for the questions.

MARTIN: **Every version**, 2.5.1 to 3.9.0, **compiles and is tested**, on **GitHub**
ODD: Every diff in **EVOLUTION.md**, every bad decision in **DESIGN.md**
BOTH: **Thank you! Questions?**

---

# Reserve: only if the Q&A asks

## 62 · r-indexedseq — Index like it's 2007

> For "isn't the extractor slow?"

MARTIN: **Index like it's 2007**
ODD: The pattern takes **half a second** on a long String; the 2007 loop is **ten thousand times faster**

## 63 · r-stringslice — Slice it like Java 6

> For "can't the slices share?"

MARTIN: Or make **slicing free**, like **Java 6**
ODD: Every slice **points into the original**: **nothing copied**, **linear again**, under a **tenth of a millisecond**
ODD: Until a **tiny slice keeps a huge string alive**: why **Java dropped it**

## 64 · r-linear — Knuth–Morris–Pratt saves the day

> For "can palindromize be linear?"

MARTIN: Or **go linear**, with **Knuth–Morris–Pratt**
ODD: The **palindromic tail** is **string matching against the reverse**: **one pass**, **19 ms instead of 7 s**
ODD: The price: **fifteen lines of index tables**. That's an **algorithms talk**
