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
- `[click]` inside a line: click there, mid-sentence if needed. In the speaker notes it's an asterisk, `*`. It marks
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

The dialogue runs about 22 minutes, with room for laughs and the morphs already counted (the times below assume a
relaxed pace and a beat after each joke). That leaves 8 minutes of the 30 for questions, or for a slow start.
Checkpoints:

| At slide | Clock | If you're later than this |
|---|---|---|
| 12 · Scala 2.8 | 6:30 | Shorten the tag-cloud jokes to the version and the year |
| 23 · Scala 2.10 | 10:15 | From here, cut the last exchange on any slide that runs long |
| 41 · Scala 3.0 | 15:25 | Say only the first line of each "New in" slide |
| 56 · Scala 4.0 | 19:35 | Go straight from 4.0 to the takeaways |

---

## 1 · cover — A Brief History of Scala · 30 s · 0:00

> Both walk on together. Martin center-left, Odd right, arms crossed.

MARTIN: Hi Berlin! I'm Martin.
ODD: And I'm odd...  That's also my name.
MARTIN: We're taking a stroll down memory lane: twenty years of Scala, told through one tiny function.
ODD: And I'm here to make sure nobody gets sentimental about it.

## 2 · oneliner — It starts as a one-liner · 45 s · 0:30

> One click: palindromize appears.

MARTIN: Here's the tiny function: isPalindrome. Is a String its own reverse? Compare, done. Ship it.
ODD: You'd expect a plain compare. But in 2007, reverse isn't a String: "racecar" would fail.
MARTIN: It's still a one liner!
ODD: One expensive line. It copies the whole string twice, just to compare it with itself.
MARTIN: Fine. [click] We need a second function; palindromize, just append the reverse. With the same mkString.
ODD: "abc" gets three more letters, when two would do.
MARTIN: Are you going to be like this all talk?
ODD: All thirty minutes.

## 3 · goal — Callable as methods · 45 s · 1:15

> Two clicks: palindromize's examples, then the case-insensitive ones.

MARTIN: So here's where we want to end up. Any sequence, any element type, called as a method.
ODD: Including on a String. Which isn't a Seq.
MARTIN: Including on a String. [click] And palindromize gives back what you gave it, adding only what it needs.
ODD: Same type out as in. That one sentence will cost us two collection redesigns.
ODD: [click] Case-insensitive, and Racecar with a capital R still counts.
MARTIN: And the caller decides what "equal" means.
ODD: Hold that thought. That's where it gets interesting.

## 4 · eq — Seq[A] needs Equality for A · 25 s · 2:00

ODD: Generic elements need generic equality, and double-equals can't be swapped out per call.
MARTIN: So equality becomes a type class. One trait, one method.
ODD: And a case-insensitive instance for Char that nobody has written yet.
MARTIN: Let's go back to 2007 and write it.

## 5 · tc2-5 — Scala 2.5 · 2007 · 20 s · 2:25

> The names fade in. Let them, for a beat.

MARTIN: Scala 2.5, May 2007. Two hundred and eighty-nine commits, by ten people.
ODD: Ten. That's not a community, that's a team lunch.

## 6 · f2-5 — New in Scala 2.5 · 25 s · 2:45

MARTIN: New in 2.5: type constructor polymorphism, placeholder lambdas, case clauses as functions.
ODD: And we use none of them.
MARTIN: That's the point. Scala already had everything this design needs.
ODD: Generics, implicits, anonymous classes. It just made you type a lot.

## 7 · e2-5 — Equality is a type class · 45 s · 3:10

> Three clicks, one per bubble.

MARTIN: Here's our Eq in 2.5. [click] Look at those instances.
ODD: Anonymous classes, braces and all. The Java 6 experience.
MARTIN: [click] And nobody imports the default?
ODD: It sits in Eq's companion, where the compiler always knows to look. Readers, not so much...
MARTIN: [click] And case-insensitive is opt-in.
ODD: A plain value. Nothing happens unless you ask for it. That I can review.

## 8 · o2-5 — Method syntax through an implicit conversion · 55 s · 3:55

> Two clicks.

MARTIN: Now method syntax. Seq has no isPalindrome function, and we can't change Seq.
ODD: So we wrap it. [click] A class that only forwards the calls.
MARTIN: [click] And this?
ODD: The implicit conversion: call something Seq lacks, and it gets slipped in for you. One allocation per call.
MARTIN: Does it work on a String?
ODD: Not with this wrapper. A String needs a conversion to become a Seq first, and conversions don't chain.
MARTIN: We could write a second wrapper, just for String.
ODD: Two wrappers for one method? I'll wait for a new Scala version.

## 9 · m0-again — What's wrong? · 30 s · 4:50

> Three clicks for the bubbles; the next click morphs into 2.5.

MARTIN: Remember our one-liners? What's wrong with them?
ODD: Where do I start. [click] A whole copy, just to compare.
MARTIN: [click] Palindromes longer than they need to be.
ODD: [click] And Strings only. We want any sequence, of anything.
MARTIN: All right. Scala 2.5, show us a better way.

## 10 · m2-5-is — A better way · 25 s · 5:20

> One click.

MARTIN: Generic, with an implicit Eq.
ODD: [click] Two indices working their way into the middle. Index arithmetic, in a functional language.
MARTIN: It's tail-recursive!
ODD: Says who? Nothing checks that that is actually true.
MARTIN: And palindromize, done properly.

## 11 · m2-5 — A better way · 45 s · 5:45

> palindromize morphs in. Two clicks.

MARTIN: [click] Find the longest suffix that is a palindrome, and mirror only what's before it.
ODD: Nice. [click] And if I give it a String, what do I get back?
MARTIN: A Seq.
ODD: A Seq of Char. I gave you a String.
MARTIN: In 2007, that's the best a generic signature can do.
ODD: Put that on the tombstone.
MARTIN: Not yet. 2.8 is coming.

## 12 · tc2-8 — Scala 2.8 · 2010 · 20 s · 6:30

MARTIN: 2.6 and 2.7 change nothing in our code. So: Scala 2.8, 2010. Two and a half thousand commits, thirty-one authors.
ODD: Six hundred of them by Paul Phillips. That man was a compiler.

## 13 · f2-8 — New in Scala 2.8 · 30 s · 6:50

MARTIN: 2.8 was the big one. The new collections, @tailrec, named and default arguments.
ODD: The release that broke everybody's code, and everybody upgraded anyway.
MARTIN: Why would a palindrome checker care about a collections rewrite?
ODD: Because palindromize builds a collection, and "give back what you were given" is exactly what 2.8 makes possible.
MARTIN: Let's see what we can use.

## 14 · e2-5-again — Char gets toLower · 5 s · 7:20

MARTIN: First, a small one, in Eq.
ODD: In 2.5 we lowercase through java.lang.Character. Very Java.

## 15 · e2-8 — Char gets toLower · 20 s · 7:25

> One click.

MARTIN: [click] And now Char does it itself.
ODD: The smallest win of the night. I'll allow it.

## 16 · m2-5-again — @tailrec · 5 s · 7:45

MARTIN: Back to our methods. 2.8 brings two upgrades. First, @tailrec.

## 17 · m2-8-is — @tailrec · 25 s · 7:50

> One click.

ODD: [click] If the recursion ever stops being a tail call, it's a compile error. Same bytecode as before.
MARTIN: Same bytecode. But a promise you can't break.
ODD: A promise that the compiler keeps. Fine.

## 18 · m2-8 — CanBuildFrom keeps the collection type · 50 s · 8:15

> palindromize morphs in. Two clicks. Odd points at the signature and counts its type parameters on his fingers.

MARTIN: And the big one: CanBuildFrom. [click]
ODD: Repr is whatever type the caller passed in, and CanBuildFrom supplies a builder for exactly that type.
MARTIN: [click] So a String comes back as a String!
ODD: Because in 2.8 a String's StringOps is a collection itself, with String as its Repr.
MARTIN: So reverse gives you back a String too. No more mkString!
ODD: It works. And it scared a generation of Scala developers away from the Scaladoc.
MARTIN: You got your String back.
ODD: I got my String back. And a therapist.

## 19 · tc2-9 — Scala 2.9 · 2011 · 15 s · 9:05

MARTIN: 2.9, 2011.
ODD: Paul Phillips: a thousand and twenty-three commits. I take it back. He wasn't a compiler. He was the compiler.

## 20 · f2-9 — New in Scala 2.9 · 15 s · 9:20

MARTIN: Parallel collections, the App trait, and the one we need: tails.
ODD: Everyone else upgraded for parallel collections. We came for tails.

## 21 · m2-8-again — tails finds the palindromic suffix · 10 s · 9:35

MARTIN: Remember that suffix search? A range of indices, and an unchecked get.

## 22 · m2-9 — tails finds the palindromic suffix · 30 s · 9:45

> One click.

MARTIN: [click] tails!
ODD: All the suffixes, longest first, down to the empty one. The position of the first that reads the same both ways tells us how much to mirror.
MARTIN: No indices. No get.
ODD: Same algorithm, same cost. But fewer ways to be wrong: the only metric I trust.

## 23 · tc2-10 — Scala 2.10 · 2013 · 20 s · 10:15

MARTIN: 2.10, January 2013. So many contributors, we can only show sixty.
ODD: And the first release that sorts before its predecessor. Alphabetically that is.
MARTIN: Nobody sorts versions alphabetically.
ODD: Every build script in 2013 did.

## 24 · f2-10 — New in Scala 2.10 · 20 s · 10:35

MARTIN: 2.10 gives us three things at once: implicit classes, value classes, and extractors for both ends of a sequence.
ODD: And string interpolation, the one feature everybody uses. And macros... I have feelings about macros...
MARTIN: Not in this talk.

## 25 · o2-8-again — Implicit value classes · 5 s · 10:55

MARTIN: Remember our wrapper, and its conversion?

## 26 · o2-10 — Implicit value classes · 30 s · 11:00

> One click.

MARTIN: [click] One declaration now, and no allocation!
ODD: Usually. Use it as a generic type, or put it in an array, and it boxes.
MARTIN: Usually beats always.
ODD: And a value class's field has to be public, so every Seq grows a public member.
MARTIN: That's 2.11's problem.

## 27 · m2-9-again — +: and :+ extractors · 5 s · 11:30

MARTIN: And now, the index loop. Odd's favourite.

## 28 · m2-10 — +: and :+ extractors · 45 s · 11:35

> Two clicks.

MARTIN: [click] Look at that pattern!
ODD: First element, the middle, last element, all in one case statement. That's pretty. I'll admit that's pretty.
MARTIN: [click] And the whole loop is one match on what's left.
ODD: But on a List the last element costs a walk, and on a String every step copies. Quietly n squared.
MARTIN: On a Vector it's fine; it's effectively constant!
ODD: Ask me about it in the Q&A.

## 29 · tc2-11 — Scala 2.11 · 2014 · 10 s · 12:20

MARTIN: 2.11, 2014. Jason Zaugg takes the lead in commits.
ODD: The calm after the storm.

## 30 · f2-11 — New in Scala 2.11 · 15 s · 12:30

MARTIN: A consolidation release: a modular library, case classes beyond twenty-two fields.
ODD: And the one we need: value classes can keep their field to themselves. My complaint from two slides ago.

## 31 · o2-10-again — Value classes may hide their field · 5 s · 12:45

MARTIN: So: that public field.

## 32 · o2-11 — Value classes may hide their field · 20 s · 12:50

> One click.

MARTIN: [click] One word.
ODD: That's it? A whole release, for one word?
MARTIN: You asked for it.
ODD: I did. Thank you, 2.11.

## 33 · tc2-12 — Scala 2.12 · 2016 · 10 s · 13:10

MARTIN: 2.12, 2016. Built on Java 8.
ODD: Scala finally gets the JVM's lambdas. After Java. Let that sink in.

## 34 · f2-12 — New in Scala 2.12 · 10 s · 13:20

MARTIN: SAM conversion, traits as interfaces, a right-biased Either.
ODD: Lambdas as implementations, that could be useful...

## 35 · e2-8-again — SAM conversion: lambdas implement traits · 5 s · 13:30

MARTIN: Eq, with its anonymous classes.

## 36 · e2-12 — SAM conversion: lambdas implement traits · 20 s · 13:35

> One click. Odd's first concession: take a breath before it.

MARTIN: [click] And now they're just lambdas!
ODD: Two anonymous classes, two lines. ... All right. I concede. That's just better.
MARTIN: Can I get that in writing?
ODD: No.

## 37 · tc2-13 — Scala 2.13 · 2019 · 20 s · 13:55

> Martin finds Odd's name in the cloud and points at it.

MARTIN: 2.13, 2019. Wait... Odd? Is that your name in there?
ODD: I was young and needed the commits.
MARTIN: In 2019? You weren't that young. So you're partly responsible for what comes next.
ODD: No comment.

## 38 · f2-13 — New in Scala 2.13 · 15 s · 14:15

MARTIN: The second collections rewrite. CanBuildFrom is gone.
ODD: Rest in peace. Nobody cried.
MARTIN: In come IsSeq and BuildFrom. And LazyList, and literal types.

## 39 · m2-10-again — IsSeq and BuildFrom · 10 s · 14:30

ODD: And our 2.12 palindromize now hands a wrapped String back, not a real String.

## 40 · m2-13 — IsSeq and BuildFrom · 45 s · 14:40

> Two clicks.

MARTIN: So, the 2.13 way. [click]
ODD: IsSeq reads anything as a sequence, String included. But the element type can't be used in the same parameter list.
MARTIN: Hence the extra type parameter?
ODD: Pinned to it with a refinement. That's a wart.
MARTIN: [click] But the result comes out of a single call. And method syntax on a String, at last!
ODD: In our code. The library could do it since 2.10. Nobody read that Scaladoc.
MARTIN: Including you.

## 41 · tc3-0 — Scala 3.0 · 2021 · 20 s · 15:25

MARTIN: And then the big bang: Scala 3, 2021. After eight and a half years of development, Dotty graduates. Twenty-one thousand commits, three hundred and twenty-one authors.
ODD: A whole new compiler. What could possibly go wrong.
MARTIN: Surprisingly little.

## 42 · f3-0 — New in Scala 3.0 · 15 s · 15:45

MARTIN: given and using, extension methods, optional braces, top-level definitions.
ODD: Four for us, and every one of them deletes code.
MARTIN: Are you... excited?
ODD: Show me the diff.

## 43 · e2-12-again — given indentation and extensions · 5 s · 16:00

MARTIN: Our Eq, Scala 2 style. Watch.

## 44 · e3-0 — given indentation and extensions · 40 s · 16:05

> Four clicks, one per bubble.

MARTIN: [click] The braces are gone!
ODD: Python developers, here we come...
MARTIN: [click] And Eq gets an operator.
ODD: One extension, and every type with an Eq can use the operator. [click] And implicit def is now given. Same thing, better name.
MARTIN: [click] And the lambdas shrink to underscores.
ODD: Very readable. For whoever wrote it.

## 45 · m2-13-again — using extensions · 10 s · 16:45

MARTIN: Now the methods. And the wrapper class we've carried around since 2.10.

## 46 · m3-0-is — using extensions · 20 s · 16:55

> One click; the next click morphs palindromize.

MARTIN: isPalindrome becomes an extension. [click]
ODD: No object, no wrapper, no conversion. And the isPalindrome method can be commented out.
MARTIN: Nobody calls it anymore.

## 47 · m3-0-ops — using extensions · 35 s · 17:15

> Two clicks.

MARTIN: Now palindromize. [click] Everything reads like a method call.
ODD: The beauty of extensions. [click] And IsSeq gets a clause of its own, so the next clause can use its element type.
MARTIN: No extra type parameter. No refinement.
ODD: Same IsSeq, same BuildFrom: the library didn't change, the language fixed the wart. I'm... almost moved.

## 48 · m3-0 — using extensions · 15 s · 17:50

> The click commented the whole class out; one more click brings its bubble.

MARTIN: And the class?
ODD: [click] Nothing left for it to do.
MARTIN: Shall we delete it?
ODD: Of course.

## 49 · m3-0-clean — using extensions · 5 s · 18:05

> The click to this slide morphs the commented-out class away. Let it play; nobody speaks.

## 50 · tc3-6 — Scala 3.6 · 2024 · 15 s · 18:10

MARTIN: 3.1 to 3.5 change nothing our code uses. So: Scala 3.6, 2024.
ODD: Technically 3.6.2. 3.6.0 was published by accident.
MARTIN: We don't talk about 3.6.0. Or 3.6.1.

## 51 · f3-6 — New in Scala 3.6 · 15 s · 18:25

MARTIN: The type class story gets finished: named context bounds, and a new given syntax.
ODD: Six releases later, the syntax catches up.

## 52 · e3-0-again — The new given syntax · 5 s · 18:40

MARTIN: Our given, one more time.

## 53 · e3-6 — The new given syntax · 15 s · 18:45

> One click.

MARTIN: [click] Now read that out loud.
ODD: "Any type gets an equality." It reads like the sentence you'd say anyway. That's new.

## 54 · m3-0-again — Context bounds get names · 5 s · 19:00

MARTIN: And the methods.

## 55 · m3-6 — Context bounds get names · 30 s · 19:05

> One click.

MARTIN: [click] The using clause is gone!
ODD: It moved into the type parameter and kept its name. I'm running out of things to complain about.
MARTIN: isPalindrome doesn't change at all. And 3.7, 3.8, 3.9 change nothing we use. Which means: we're done.
ODD: Are we, though?

## 56 · cloud4-0 — Scala 4.0 · 15 s · 19:35

> Deadpan. Let the two names sit there.

MARTIN: Well. There is one more release, Scala 4.0.
ODD: Only two authors this time.
MARTIN: A very exclusive community.
ODD: Two authors, three opinions...

## 57 · f4-0 — New in Scala 4.0 · 20 s · 19:50

MARTIN: One feature. Prolog extractors.
ODD: Use one name twice in a pattern, and both places have to match the same value.
MARTIN: If you remember Prolog from university: you're welcome. If you don't: also welcome.

## 58 · m3-6-again — Prolog extractors · 5 s · 20:10

MARTIN: Here's 3.6's isPalindrome. Watch the match.

## 59 · m4-0 — Prolog extractors · 25 s · 20:15

> One click.

MARTIN: [click] The same name at both ends, and the comparison disappears into the pattern. Isn't that beautiful?
ODD: Which equality would it use? We want the caller to decide.
MARTIN: That's a 4.1 problem.

## 60 · takeaways — What the palindrome taught us · 40 s · 20:40

> Drop the comedy a notch. Slower, to the room.

MARTIN: So what did one tiny function teach us?
ODD: That the ideas were all there in 2007. Generics, type classes, implicit conversions.
MARTIN: And every release made them cheaper to write.
ODD: Not every step was a pure win though... CanBuildFrom did its job but frightened everyone. 2.13's refinement was a detour.
MARTIN: And Scala 3 lets you just say it, where Scala 2 made you spell it out.
ODD: ... I'll give you that one.

## 61 · thanks — Thank you · 15 s · 21:20

> Stand together. Leave the QR code up for the questions.

MARTIN: Every version, from 2.5.1 to 3.9.0, compiles and is tested. It's all on GitHub.
ODD: Every diff in EVOLUTION.md. And every bad decision explained in DESIGN.md.
BOTH: Thank you! Questions?

---

# Reserve: only if the Q&A asks

Jump to these from the presenter view (type the number, then Enter), and back to 61 when done. Martin opens with
the heading's idea; Odd answers.

## 62 · r-indexedseq — Index like it's 2007

> For "isn't the extractor slow?"

MARTIN: Index like it's 2007.
ODD: Half a second on a long String with our pattern. The 2007 loop is ten thousand times faster.
MARTIN: Sometimes the old ways win.

## 63 · r-stringslice — Slice it like Java 6

> For "can't the slices share?"

MARTIN: Or make slicing free, like Java 6 did.
ODD: Every slice points into the original, so nothing is copied. The pattern is linear again.
MARTIN: Under a tenth of a millisecond!
ODD: Until a tiny slice keeps a huge string alive. That's why Java dropped it.

## 64 · r-linear — Knuth–Morris–Pratt saves the day

> For "can palindromize be linear?"

MARTIN: Or go linear, with Knuth–Morris–Pratt.
ODD: Finding the palindromic tail is just string matching against the reverse. One pass.
MARTIN: Nineteen milliseconds instead of seven seconds!
ODD: And fifteen lines of index tables. That's an algorithms talk.
