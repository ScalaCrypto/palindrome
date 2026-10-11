# A Brief History of Scala: the script

ScalaDays 2026, Berlin, Monday 12 October. 30 minutes, 61 slides, three reserve slides for the Q&A.
Martin Zachrison and Odd Möller.

## The cast

**MARTIN, the enthusiast.** The fan, and the one who wrote the code. Warm, nostalgic, sees the best in every release,
defends the old code like an old car that still starts. He introduces each step and asks what the room is thinking;
he doesn't explain the machinery. Never sarcastic; enthusiasm is the joke.

**ODD, the skeptic.** The code reviewer, and the one who knows how it works underneath: what the compiler inserts,
what it costs, where it breaks. Dry, deadpan, counts allocations, remembers every migration. Never shouts, never
sneers: just unimpressed. Over the talk Scala slowly wins Odd over: a first concession at 2.12 ("I concede"), "almost
moved" at 3.0, and "I'll give you that one" at the end. Play that arc; it's the story under the jokes.

The audience knows Scala very well. Never explain a feature they already know; name it and move on. The laughs come
from recognition: everybody in the room has lived through CanBuildFrom.

## How to read this file

- `MARTIN:`, `ODD:` and `BOTH:` lines are spoken. They, and only they, become the slides' speaker notes:
  `talk/deck.py` copies them into every slide's notes, so edit the dialogue here, not in the artifact. The presenter
  view shows them without the names: Odd's on the left in blue, Martin's on the right in orange.
  A spoken line may go on over several lines: indent the ones after the first.
- `**bold**` marks a line's key words: a glance at them should give its gist. The presenter view shows them bold
  (E switches it off and on), as do the practice PDFs; the artifact's plain-text notes drop the marks. Bold only
  what's central, as many points as the line has. Where a technical point's keyword alone would lose its meaning,
  bold it as a short phrase that says something on its own (**double-equals never asks the caller**, not
  **double-equals** … **caller**); a joke or a turn needs only its cue word, and a line that only sets up the next
  gets none. About a third of the words (shorter lines, as in the bullets, run higher).
- `[click]` inside a line: click there, mid-sentence if needed. In the speaker notes it's `(click)`. It marks
  only the clicks that bring something onto the slide (a bubble, a line of code), so a slide has exactly as many as
  it has builds; the build fails otherwise. The click to the next slide always comes after the slide's last line, and
  isn't marked. Other `[brackets]` are never spoken, and stay out of the notes.
- Lines starting with `>` are stage directions: who does what, and when to click.
- Each slide's heading gives its number, its id in the deck, and roughly how long it takes, with the clock at its
  start.

## Writing the lines

- Never read code out as it's written: say what it does ("both ends in one pattern"), not its symbols. Names of
  types, methods and features (IsSeq, @tailrec, tails) are fine.
- A bubble is on screen while you talk: say the same thing in other words, never the bubble's words.
- Keep each slide's notes to what fits the presenter view without scrolling: a handful of short turns.

## Staging

- Martin stands left of the screen and holds the clicker; Odd stands right. When Odd's line needs a click, Odd nods
  or says "click" with a look, and Martin clicks. Make that a running gag only if it lands the first time.
- The presenter view (`talk/present.py`) shows these notes and the next click. Glance, don't read: by Monday the
  lines should be yours, and the notes only a prompt.
- Every "again" slide (the old code shown once more, under the next step's heading) is a two-second bridge: one
  line, then the click that starts the morph.
- Let the morphs finish before talking over them: the code moving is the show. In the local player a morph takes
  2.4 seconds; the artifact uses its own, shorter timing.
- Pause after a joke. Never explain one, and never laugh at your own.

## Timing

The dialogue runs about 21¾ minutes, with room for laughs and the morphs already counted (the times below assume a
relaxed pace and a beat after each joke). That leaves 8¼ minutes of the 30 for questions, or for a slow start.
Checkpoints:

| At slide | Clock | If you're later than this |
|---|---|---|
| 12 · Scala 2.8 | 6:25 | Shorten the tag-cloud jokes to the version and the year |
| 23 · Scala 2.10 | 10:15 | From here, cut the last exchange on any slide that runs long |
| 41 · Scala 3.0 | 15:35 | Say only the first line of each "New in" slide |
| 56 · Scala 4.0 | 19:45 | Go straight from 4.0 to the takeaways |

---

## 1 · cover — A Brief History of Scala · 30 s · 0:00

> Both walk on together. Martin center-left, Odd right, arms crossed.
> Odd says "And I'm Odd." exactly as Martin said his own name: same rhythm, a friendly nod, no pause before
> "Odd". A beat, deadpan, while Martin glances at Odd; then "That's also my name.", stressing "also", so the room
> hears the first line again as "I'm odd". Martin goes on once the laugh starts, or after a second without one.

MARTIN: **Hi Berlin**! I'm Martin.
ODD: And I'm Odd. ... That's **also my name**.
MARTIN: We're taking a stroll down memory lane: **twenty years of Scala**, told through **one tiny function**.
ODD: And I'm here to make sure nobody gets **sentimental** about it.

## 2 · oneliner — It starts as a one-liner · 45 s · 0:30

> Two clicks: .mkString("") appears, then palindromize.

MARTIN: Here's the tiny function: **isPalindrome**. Is a String its **own reverse**? Compare, done. Ship it.
ODD: You'd expect the plain comparison to work. But in 2007, reverse **doesn't return a String**, so it **always fails**.
MARTIN: I can fix that [click] and it's **still a one-liner**!
ODD: One expensive line. It **copies the whole string twice**, just to compare it with itself.
MARTIN: Fine. We look at its dual function [click] **palindromize**: make a palindrome of any string.
ODD: But **"abc"** becomes **"abc cba"**, when it ought to be **"abc ba"**.
MARTIN: Are you going to be like this the whole talk?
ODD: All **thirty minutes**.

## 3 · goal — Callable as methods · 45 s · 1:15

> Two clicks: palindromize's examples, then the case-insensitive ones.

MARTIN: So here's where we want to end up. **Any sequence**, **any element type**, called as a **method**.
ODD: Including **on a String**. Which **isn't a Scala Seq**.
MARTIN: Including on a String. [click] And palindromize gives back **what you gave it**, adding only what's needed.
ODD: **Same type** out as in. That one feature will cost Scala **two collection redesigns**.
MARTIN: [click] **Case-insensitive**, and Racecar with a capital R is a palindrome.
ODD: So the **caller** should decide what **"equal"** means.
MARTIN: Hold that thought. That's where it gets interesting.

## 4 · eq — Seq[A] needs Equality for A · 25 s · 2:00

MARTIN: For this, equality needs to become a **type class**. One trait, one method.
ODD: And a **case-insensitive instance for Char** that isn't written yet.
MARTIN: Let's go back to **2007** and write it.

## 5 · tc2-5 — Scala 2.5 · 2007 · 20 s · 2:25

> The names fade in. Let them, for a beat.

MARTIN: Scala **2.5**, May 2007. Two hundred and eighty-nine commits, by **ten people**.
ODD: Ten. That's not a community, that's a **team lunch**.

## 6 · f2-5 — New in Scala 2.5 · 25 s · 2:45

MARTIN: **New in 2.5**: type constructor polymorphism, placeholder lambdas, case clauses as functions.
ODD: And we use **none** of them.
MARTIN: That's the point. Scala already had **everything** this design needs.
ODD: True. **Generics, implicits**, anonymous classes, all there. It just made you **type a lot**.

## 7 · e2-5 — Equality is a type class · 40 s · 3:10

> Two clicks, one per bubble.

MARTIN: Here's our **Equality** in 2.5. [click]
ODD: We create a **new instance** for each **usage**
MARTIN: [click] And case-insensitive is **opt-in**.
ODD: A **plain value**. Nothing happens unless you ask for it. That I can live with.

## 8 · o2-5 — Method syntax through an implicit conversion · 55 s · 3:50

> Two clicks.

MARTIN: Now **method syntax**. Seq has no isPalindrome method, and we **can't change Seq**, so we **wrap it**. [click] A class that **only forwards the calls**.
ODD: When you call isPalindrome on a Seq, the **compiler creates a wrapper for you** [click].
MARTIN: Does it work on a **String**?
ODD: Not this one. A String would need **two conversions**, and the compiler **can only do one**.
MARTIN: We could write a **second wrapper**, just for String.
ODD: **Two wrappers** for one method? I'll wait for Scala **to catch up**.

## 9 · m0-again — What's wrong? · 30 s · 4:45

> Three clicks for the bubbles; the next click morphs into 2.5.

MARTIN: Remember our **one-liners**? What's **wrong** with them?
ODD: Where do I start. [click] **Copying** just to compare.
ODD: [click] Palindromes **longer** than they need to be.
ODD: [click] And **Strings only**. We want **any sequence**, of anything.
MARTIN: All right. Scala 2.5, show us a **better way**.

## 10 · m2-5-is — A better way · 25 s · 5:15

> One click.

MARTIN: **Generic**, with an **implicit Equality**. [click]
ODD: **Index arithmetic**, in a functional language.
MARTIN: It's **tail-recursive**!
ODD: Says who? **Nothing checks it**.
MARTIN: And now **palindromize**, done properly.

## 11 · m2-5 — A better way · 45 s · 5:40

> palindromize morphs in. Two clicks.

MARTIN: Here it is! [click]
ODD: Ok. And if I give it a **String**, what do I **get back**?
MARTIN: A **Seq**.
ODD: A **Seq of Char**, but I gave you a **String**...
MARTIN: In 2007, that's the **best a generic signature can do**. [click]
ODD: That's a **bummer**
MARTIN: Unfortunately, neither 2.6 nor 2.7 helps us with this.

## 12 · tc2-8 — Scala 2.8 · 2010 · 15 s · 6:25

MARTIN: So: Scala **2.8, released in 2010**.
ODD: Two and a half thousand commits. Six hundred of them by **Paul Phillips**. That man was a **compiler**.

## 13 · f2-8 — New in Scala 2.8 · 30 s · 6:40

MARTIN: 2.8 was a **big one**. New **collections**, **@tailrec**, named and default arguments.
ODD: The release that **broke everyone's code**, and everyone **upgraded anyway**.
MARTIN: But palindromize **needs** the new collections.
ODD: Because it **builds a collection**. And from 2.8, it can build the **kind you asked for**.
MARTIN: Let's see how we can use that.

## 14 · e2-5-again — Char gets toLower · 5 s · 7:10

MARTIN: First, a small one, in **Equality**.
ODD: In 2.5 we call **toLowerCase** on each Char.

## 15 · e2-8 — Char gets toLower · 30 s · 7:15

> One click.

MARTIN: Now **toLower**, right on the Char [click].
ODD: Same method as in **2007**. It's a **rename**.
MARTIN: A **shorter** rename!
ODD: The **smallest win** of the night. I'll allow it.

## 16 · m2-5-again — @tailrec · 5 s · 7:45

MARTIN: Back to our methods. 2.8 brings **two upgrades**. First, **@tailrec**.

## 17 · m2-8-is — @tailrec · 25 s · 7:50

> One click.

ODD: If the recursion ever stops being a **tail call**, it's a **compile time error**. **Same bytecode** as before.
MARTIN: Same bytecode. But a **promise** you can't break. [click]
ODD: A promise that the **compiler keeps**. I like that.
MARTIN: Now, on to the big one: **CanBuildFrom**.

## 18 · m2-8 — CanBuildFrom keeps the collection type · 50 s · 8:15

> palindromize morphs in. Two clicks. Odd points at the signature and counts its type parameters on his fingers.

ODD: **Repr** is whatever **type the caller passed in**, [click] and CanBuildFrom supplies a **builder for exactly that type**.
MARTIN: [click] So a **String comes back as a String**!
ODD: Because 2.8 wraps a String in **StringOps**, and its **Repr is String**.
MARTIN: **reverse** gives you back a String too. No more **mkString**!
ODD: This works. And it **scared** a generation of Scala developers.
MARTIN: You got your String back.
ODD: I got my String back. And a **therapist**.

## 19 · tc2-9 — Scala 2.9 · 2011 · 15 s · 9:05

MARTIN: **2.9, from 2011**.
ODD: Paul Phillips: now a thousand and twenty-three commits. I take it back. He wasn't a compiler. He was **the compiler**.

## 20 · f2-9 — New in Scala 2.9 · 15 s · 9:20

MARTIN: **Parallel collections**, the App trait, and the one we need: **tails**.
ODD: Everyone else upgraded for parallel collections. **We came for tails**.

## 21 · m2-8-again — tails finds the palindromic suffix · 10 s · 9:35

MARTIN: Remember that **suffix search**? A range over indices, and an **unchecked get**.

## 22 · m2-9 — tails finds the palindromic suffix · 30 s · 9:45

> One click.

MARTIN: [click] **tails**! **No indices. No get.**
ODD: Same algorithm, same cost. But **fewer ways to be wrong**: the only metric I trust.

## 23 · tc2-10 — Scala 2.10 · 2013 · 20 s · 10:15

> A beat before "Alphabetically": the room needs a second to see 2.10 sort before 2.9.

MARTIN: **2.10**, January 2013. So many contributors, we can only show **sixty**.
ODD: And the first release that **sorts before** its predecessor. **Alphabetically**, that is.
MARTIN: Nobody sorts versions alphabetically.
ODD: Every **build script** in those days did.

## 24 · f2-10 — New in Scala 2.10 · 20 s · 10:35

MARTIN: 2.10 gives us three things: **implicit classes**, **value classes**, and **sequence extractors**.
ODD: And **string interpolation**, the one feature everyone uses. And **macros**... I have feelings about macros...
MARTIN: Not in this talk.

## 25 · o2-8-again — Implicit value classes · 5 s · 10:55

MARTIN: Remember our **wrapper**, and its conversion?

## 26 · o2-10 — Implicit value classes · 30 s · 11:00

> One click.

MARTIN: [click] One declaration now, and **no allocation**!
ODD: Usually. Use it as a **generic type**, or put it in an **array**, and **it boxes**.
MARTIN: Usually beats always.
ODD: And every Seq now has a **public member**.
MARTIN: That's **2.11's problem**.

## 27 · m2-9-again — +: and :+ extractors · 5 s · 11:30

MARTIN: And now, the **index loop**. Odd's favourite.

## 28 · m2-10 — +: and :+ extractors · 45 s · 11:35

> Two clicks.

MARTIN: [click] Look at that **pattern**!
ODD: First, middle, last, all in **one case** statement. That's **pretty**.
MARTIN: [click] And the whole loop becomes a **match**.
ODD: But on a **String every step copies**. Quietly **n squared**.
MARTIN: On a **Vector** it's fine; it's **effectively constant**!
ODD: Let's talk about it in the **Q&A**.

## 29 · tc2-11 — Scala 2.11 · 2014 · 10 s · 12:20

MARTIN: **2.11**, April **2014**: the month of **Heartbleed**.
ODD: A good time to **hide your privates**.

## 30 · f2-11 — New in Scala 2.11 · 15 s · 12:30

MARTIN: A **consolidation** release: a **modular library**, case classes beyond twenty-two fields.
ODD: And the one we need: **value classes** can keep their **field to themselves**. My complaint from 2.10.

## 31 · o2-10-again — Value classes may hide their field · 5 s · 12:45

MARTIN: So: that **public field**.

## 32 · o2-11 — Value classes may hide their field · 20 s · 12:50

> One click.

MARTIN: [click] **One word**.
ODD: That's it? A whole release, for **one word**?
MARTIN: You asked for it.
ODD: I did. **Thank you**, 2.11.

## 33 · tc2-12 — Scala 2.12 · 2016 · 10 s · 13:10

MARTIN: **2.12**, released in 2016. Built on **Java 8**.
ODD: Scala lambdas now compile to proper JVM **lambdas**. Scala, **catching up with Java**...

## 34 · f2-12 — New in Scala 2.12 · 10 s · 13:20

MARTIN: **SAM conversion**, **traits as interfaces**, a right-biased Either.
ODD: **Lambdas** instead of anonymous classes? That sounds useful.

## 35 · e2-8-again — SAM conversion: lambdas implement traits · 5 s · 13:30

MARTIN: Equality, with its **anonymous classes**.

## 36 · e2-12 — SAM conversion: lambdas implement traits · 20 s · 13:35

> One click. Odd's first concession: take a breath before it.

MARTIN: And now they're just **lambdas**! [click]
ODD: Two anonymous classes, **two lines**. ... All right. **I concede**. That's just better.
MARTIN: Can I get that in **writing**?
ODD: **No.**

## 37 · tc2-13 — Scala 2.13 · 2019 · 20 s · 13:55

> Martin finds Odd's name in the cloud and points at it. A beat after "You weren't that young.", before the rest.

MARTIN: The year is 2019, we get **2.13**. Wait... Odd? Is that **your name** in there?
ODD: I was young and **needed the commits**.
MARTIN: In 2019? You weren't that young. So you're **partly responsible** for what comes next.
ODD: **No comment**.

## 38 · f2-13 — New in Scala 2.13 · 15 s · 14:15

MARTIN: The second **collections rewrite**. **CanBuildFrom is gone**.
ODD: **Rest in peace**. No one cried.
MARTIN: In comes **IsSeq** and **BuildFrom**.

## 39 · m2-10-again — IsSeq and BuildFrom · 10 s · 14:30

MARTIN: Here is palindromize, 2.10 style.

## 40 · m2-13 — IsSeq and BuildFrom · 55 s · 14:40

> One click.

MARTIN: 2.13 replaces CanBuildFrom with **IsSeq** and **BuildFrom**. [click]
ODD: But you can only have **one** implicit parameter list, so we use **type refinement** for the element type.
MARTIN: Is that why we need the A0 type?
ODD: Yes, but kind of a **wart**.

## 41 · tc3-0 — Scala 3.0 · 2021 · 15 s · 15:35

MARTIN: And now the big bang: **Scala 3**, 2021. After eight and a half years, **Dotty** graduates.
ODD: A whole **new compiler**. What could possibly go wrong.
MARTIN: **Surprisingly little did**.

## 42 · f3-0 — New in Scala 3.0 · 20 s · 15:50

MARTIN: **given** and using, **extension methods**, **optional braces**, **top-level** definitions.
ODD: We use **all four**, and every one of them **reduces boilerplate**.
MARTIN: Are you... **excited**?
ODD: Show me the **diff**.

## 43 · e2-12-again — given indentation and extensions · 5 s · 16:10

MARTIN: Our Equality, Scala 2 style. **Watch**.

## 44 · e3-0 — given indentation and extensions · 40 s · 16:15

> Four clicks, one per bubble.

MARTIN: [click] The **braces** are gone!
ODD: **Python** developers, here we come.
MARTIN: [click] And Equality gets an **operator** [click].
ODD: An implicit def is now a **given**. Same thing, better name.
MARTIN: [click] And the lambdas shrink to **underscores**.
ODD: Very readable. For **the one who wrote it**.

## 45 · m2-13-again — using extensions · 10 s · 16:55

MARTIN: Now the methods. And the **wrapper class** we've carried around since 2.10.

## 46 · m3-0-is — using extensions · 20 s · 17:05

> One click; the next click morphs palindromize.

MARTIN: isPalindrome becomes an **extension**. [click]
ODD: **No object, no wrapper, no conversion**. And the implicit method is **commented out** since no one calls it anymore.
MARTIN: Now **palindromize**.

## 47 · m3-0-ops — using extensions · 35 s · 17:25

> One click.

MARTIN: Everything reads like a **method call**.
ODD: [click] And **IsSeq gets a using clause of its own**, so the other using clause **can refer to its element type**.
MARTIN: No extra type parameter. **No refinement**.
ODD: Same IsSeq, same BuildFrom: the library didn't change, the **language fixed the wart**. I'm... **almost moved**.

## 48 · m3-0 — using extensions · 15 s · 18:00

> The click commented the whole class out; one more click brings its bubble.

MARTIN: And the **implicit class**?
ODD: [click] **Nothing left**, no use for it.
MARTIN: Shall we **delete** it?
ODD: **Please do**.

## 49 · m3-0-clean — using extensions · 5 s · 18:15

> The click to this slide morphs the commented-out class away. Let it play; nobody speaks.

## 50 · tc3-6 — Scala 3.6 · 2024 · 15 s · 18:20

MARTIN: 3.1 to 3.5 **change nothing** in our code. So: Scala **3.6, in 2024**.
ODD: Technically **3.6.2**. 3.6.0 was published **by accident**.
MARTIN: We **don't talk about** 3.6.0.

## 51 · f3-6 — New in Scala 3.6 · 15 s · 18:35

MARTIN: The type class story gets finished: **named context bounds**, and a new **given syntax**.
ODD: Six releases later, the **syntax finally catches up**.

## 52 · e3-0-again — The new given syntax · 5 s · 18:50

MARTIN: Our **given**, one more time.

## 53 · e3-6 — The new given syntax · 15 s · 18:55

> One click.

MARTIN: [click] Now read that **out loud**.
ODD: "**Any type gets an equality**." It reads like you say it. That's nice.

## 54 · m3-0-again — Context bounds get names · 5 s · 19:10

MARTIN: And the methods.

## 55 · m3-6 — Context bounds get names · 30 s · 19:15

> One click.

MARTIN: [click] The **using clause is gone**!
ODD: It **moved into the type parameter and kept its name**. I'm running out of things to complain about.
MARTIN: isPalindrome **doesn't change** at all. And 3.7, 3.8, 3.9 change nothing we use. Which means: we're **done**.
ODD: **Are we, though?**

## 56 · cloud4-0 — Scala 4.0 · 15 s · 19:45

> Deadpan. Let the two names sit there.

MARTIN: Well. There is **one more release**, **Scala 4.0**.
ODD: Only **two authors** this time.
MARTIN: A very **exclusive** community.
ODD: Two authors, **three opinions**.

## 57 · f4-0 — New in Scala 4.0 · 20 s · 20:00

MARTIN: One feature. **Prolog extractors**.
ODD: Use **one name twice in a pattern**, and both places have to **match the same value**.
MARTIN: If you remember **Prolog** from university: you're **welcome**. If you don't: also welcome.

## 58 · m3-6-again — Prolog extractors · 5 s · 20:20

MARTIN: Here's 3.6's isPalindrome. **Watch the match**.

## 59 · m4-0 — Prolog extractors · 25 s · 20:25

> One click.

MARTIN: The **same name** at both ends, and the **comparison disappears** into the pattern. Isn't that **beautiful**? [click]
ODD: Sure, but **which equality would it use**? We still want the **caller to decide**, remember?
MARTIN: That's a **4.1 problem**...

## 60 · takeaways — What the palindrome taught us · 40 s · 20:50

> Drop the comedy a notch. Slower, to the room.

MARTIN: So what did two tiny functions **teach** us?
ODD: That the **machinery was there already** in 2007. **Generics, type classes, implicit conversions**.
MARTIN: And every release made them **cheaper** to write.
ODD: **Not every step was a pure win**, though. CanBuildFrom did its job but **frightened everyone**. 2.13's **refinement was a detour**.
MARTIN: And in Scala 3, the code finally **reads the way we'd explain it**.
ODD: ... I finally **agree**.

## 61 · thanks — Thank you · 15 s · 21:30

> Stand together. Leave the QR code up for the questions.

MARTIN: Every version, from 2.5 to 3.9, **compiles and is tested**. It's all on **GitHub**.
ODD: Every diff in **EVOLUTION.md**. And every bad decision explained in **DESIGN.md**.
MARTIN: **Thank you!**
ODD: **Questions?**

---

# Finale: the code, 2.5 to 4.0

## 62 · finale — The whole code, 2.5 to 4.0

> The finale, without words: one slide that plays by itself, the whole of 2.5, then each version morphing into the
> next, 2.5 to 4.0, and round again, with the repository's QR code in a corner. Click to it once the applause starts
> and let it run; it can stay up for the questions.

---

# Reserve: only if the Q&A asks

Jump to these from the presenter view (type the number, then Enter), and back to 61 when done. Martin opens with
the heading's idea; Odd answers.

## 63 · r-indexedseq — Index like it's 2007

> For "isn't the extractor slow?"

MARTIN: **Index like it's 2007**.
ODD: Our pattern takes **half a second** on a long String. The 2007 loop is **ten thousand times faster**.
MARTIN: Sometimes the **old ways** win.

## 64 · r-stringslice — Slice it like Java 6

> For "can't the slices share?"

MARTIN: Or make **slicing free**, like **Java 6** did.
ODD: Every slice points into the **original**, so **nothing is copied**. The pattern is **linear** again.
MARTIN: Under a **tenth of a millisecond**!
ODD: Until a tiny slice keeps a **huge string alive**. That's why **Java dropped it**.

## 65 · r-linear — Knuth–Morris–Pratt saves the day

> For "can palindromize be linear?"

MARTIN: Or go **linear**, with **Knuth–Morris–Pratt**.
ODD: Finding the palindromic tail is just **string matching** against the reverse. **One pass**.
MARTIN: **Nineteen milliseconds** instead of **seven seconds**!
ODD: And **fifteen lines** of index tables. That's an **algorithms talk**.
