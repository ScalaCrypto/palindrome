# A Brief History of Scala: the script

ScalaDays 2026, Berlin, Monday 12 October. 30 minutes, 60 slides, three reserve slides for the Q&A.
Martin Zachrison and Odd Möller.

## The cast

**MARTIN, the good cop.** The fan. Warm, nostalgic, sees the best in every release, defends the old code like an old
car that still starts. Never sarcastic; enthusiasm is the joke.

**ODD, the bad cop.** The code reviewer. Dry, deadpan, counts allocations, remembers every migration. Never shouts,
never sneers: just unimpressed. Over the talk Scala slowly wins Odd over: a first concession at 2.12 ("I concede"),
"almost moved" at 3.0, and "I'll give you that one" at the end. Play that arc; it's the story under the jokes.

The audience knows Scala very well. Never explain a feature they already know; name it and move on. The laughs come
from recognition: everybody in the room has lived through CanBuildFrom.

## How to read this file

- `MARTIN:`, `ODD:` and `BOTH:` lines are spoken. They, and only they, become the slides' speaker notes:
  `talk/deck.py` copies them into every slide's notes, so edit the dialogue here, not in the artifact.
- `[click]` inside a line: click there, mid-sentence if needed. `[brackets]` are never spoken.
- Lines starting with `>` are stage directions: who does what, and when to click.
- Each slide's heading gives its number, its id in the deck, and roughly how long it takes, with the clock at its
  start.

## Staging

- Martin stands left of the screen and holds the clicker; Odd stands right. When Odd's line needs a click, Odd nods
  or says "click" with a look, and Martin clicks. Make that a running gag only if it lands the first time.
- The presenter view (`talk/present.py`) shows these notes and the next click. Glance, don't read: by Monday the
  lines should be yours, and the notes only a prompt.
- Every "again" slide (the old code shown once more) is a two-second bridge: one line, click, and the new heading
  and the morph do the rest.
- Let the morphs finish before talking over them: the code moving is the show. In the local player a morph takes
  2.4 seconds; the artifact uses its own, shorter timing.
- Pause after a joke. Never explain one, and never laugh at your own.

## Timing

The dialogue runs about 21½ minutes, with room for laughs and the morphs already counted (the times below assume a
relaxed pace and a beat after each joke). That leaves 8 minutes of the 30 for questions, or for a slow start.
Checkpoints:

| At slide | Clock | If you're later than this |
|---|---|---|
| 12 · Scala 2.8 | 7:00 | Shorten the tag-cloud jokes to the version and the year |
| 23 · Scala 2.10 | 10:15 | From here, cut the last exchange on any slide that runs long |
| 41 · Scala 3.0 | 15:25 | Say only the first line of each "New in" slide |
| 55 · Scala 4.0 | 19:20 | Go straight from 4.0 to the takeaways |

---

## 1 · cover — A Brief History of Scala · 30 s · 0:00

> Both walk on together. Martin center-left, Odd right, arms crossed.

MARTIN: Hi Berlin! I'm Martin, and this is Odd.
ODD: The odd one.
MARTIN: We're taking a walk down memory lane: twenty years of Scala, told through one tiny function.
ODD: And I'm here to make sure nobody gets sentimental about it.
MARTIN: I'm the good cop.
ODD: I'm the code reviewer.

## 2 · oneliner — It starts as a one-liner · 60 s · 0:30

> One click: palindromize appears.

MARTIN: Here's the whole problem. Is a string a palindrome? It equals its reverse. Done. Ship it.
ODD: It allocates a reversed copy of the string, just to compare it with itself.
MARTIN: It's one line!
ODD: One expensive line. And in 2.7 it says "racecar" isn't a palindrome.
MARTIN: Because collection equality wasn't by content before 2.8. Fine. [click] And to make a palindrome, append the reverse.
ODD: "abc" becomes "abccba". Your palindromes are longer than they need to be.
MARTIN: You're going to be like this all talk, aren't you?
ODD: All thirty minutes.

## 3 · goal — Callable as methods · 55 s · 1:30

> Two clicks: palindromize's examples, then the case-insensitive ones.

MARTIN: So here's where we want to end up. Any sequence, any element type, called as a method.
ODD: Including on a String. Which isn't a Seq.
MARTIN: Including on a String. [click] And palindromize gives back what you gave it: a String stays a String, a Vector stays a Vector. And it only adds what it has to: "abcb" needs just one more a.
ODD: [click] And the caller decides what "equal" means.
MARTIN: Case-insensitive, and "Racecar" is a palindrome.
ODD: Hold that thought. That's where it gets interesting.

## 4 · eq — Seq[A] needs Equality for A · 25 s · 2:25

ODD: Generic elements need generic equality. And double-equals is hardwired.
MARTIN: So equality becomes a type class. One trait, one method: eqv.
ODD: And a case-insensitive Eq for Char that nobody has written yet.
MARTIN: Let's go back to 2007 and write it.

## 5 · tc2-5 — Scala 2.5 · 2007 · 20 s · 2:50

> The names fade in. Let them, for a beat.

MARTIN: Scala 2.5, May 2007. Two hundred and eighty-nine commits, by ten people.
ODD: Ten. That's not a community, that's a team lunch.
MARTIN: And yes, that's Martin Odersky. No relation. Sadly.

## 6 · f2-5 — New in Scala 2.5 · 30 s · 3:10

MARTIN: New in 2.5: type constructor polymorphism, placeholder lambdas, case clauses as functions.
ODD: And we use none of them. Look: nothing in amber.
MARTIN: That's the point. Generics, implicits, anonymous classes: Scala already had everything this design needs.
ODD: It just made you type a lot.

## 7 · e2-5 — Equality is a type class · 50 s · 3:40

> Three clicks, one per bubble.

MARTIN: Here's Eq in 2.5. [click] Every instance is an anonymous class.
ODD: "new Eq[A], open brace." The Java 1.4 experience.
MARTIN: [click] The default lives in the companion and is found through the implicit scope. You never import it.
ODD: The implicit scope: where things are found that nobody can find.
MARTIN: [click] And case-insensitive is opt-in: a plain val. Pass it, or put it in scope.
ODD: Opt-in. I like opt-in. Opt-in I can review.

## 8 · o2-5 — Method syntax through an implicit conversion · 45 s · 4:30

> Two clicks.

MARTIN: Now method syntax. Seq has no isPalindrome, and we can't change Seq.
ODD: So we wrap it. [click]
MARTIN: A wrapper that forwards. [click] And an implicit def the compiler slips in whenever you call something Seq doesn't have.
ODD: So every call allocates a wrapper. And conversions don't chain, so "racecar".isPalindrome won't compile until 2.13.
MARTIN: That's 2019.
ODD: Twelve years to call a method on a String.

## 9 · m0-again — What's wrong? · 40 s · 5:15

> Three clicks for the bubbles; the fourth click morphs into 2.5.

MARTIN: Remember our one-liners? What's wrong with them?
ODD: Where do I start. [click] It copies the whole string just to compare.
MARTIN: [click] It doesn't make the shortest palindrome.
ODD: [click] And it only takes a String. We want any Seq of A.
MARTIN: All right. Scala 2.5, show us a better way. [click]

## 10 · m2-5-is — A better way · 25 s · 5:55

> One click.

MARTIN: Generic, with an implicit Eq. [click] Two indices, walking inward.
ODD: Index arithmetic. In a functional language.
MARTIN: It's tail-recursive!
ODD: Says who? Nothing checks that yet.
MARTIN: The compiler turns it into a loop anyway. Quietly.
ODD: Quietly isn't a guarantee.

## 11 · m2-5 — A better way · 40 s · 6:20

> palindromize morphs in. Two clicks.

MARTIN: And palindromize, done properly. [click] Keep the palindromic tail, mirror only the rest: the shortest palindrome.
ODD: Nice. [click] And if I give it a String, what do I get back?
MARTIN: A Seq.
ODD: A Seq of Char. I gave you a String.
MARTIN: In 2007, generic code can only promise a Seq.
ODD: Put that on the tombstone.
MARTIN: Not yet. 2.8 is coming.

## 12 · tc2-8 — Scala 2.8 · 2010 · 15 s · 7:00

MARTIN: Scala 2.8, 2010. Two and a half thousand commits, thirty-one authors.
ODD: Six hundred of them by Paul Phillips. That man was a compiler.

## 13 · f2-8 — New in Scala 2.8 · 20 s · 7:15

MARTIN: 2.8 was the big one. The new collections, @tailrec, named and default arguments.
ODD: The release that broke everybody's code, and everybody upgraded anyway.
MARTIN: In amber, what we'll use: CanBuildFrom, @tailrec, and Char gets toLower.

## 14 · e2-5-again — Char gets toLower · 5 s · 7:35

MARTIN: First, a small one, in Eq. [click]

## 15 · e2-8 — Char gets toLower · 15 s · 7:40

> One click.

ODD: Character dot toLowerCase. Very Java.
MARTIN: [click] Char now has toLower.
ODD: The smallest win of the night. I'll allow it.

## 16 · m2-5-again — @tailrec · 5 s · 7:55

MARTIN: Back to our methods. 2.8 brings two upgrades. [click]

## 17 · m2-8-is — @tailrec · 20 s · 8:00

> One click.

MARTIN: First, @tailrec. [click] Now the compiler checks the loop.
ODD: Same bytecode as before.
MARTIN: Same bytecode. But now it's a promise you can't break.
ODD: A promise I can review. Fine.

## 18 · m2-8 — CanBuildFrom keeps the collection type · 50 s · 8:20

> palindromize morphs in. Two clicks. Odd reads the signature slowly, like a charge sheet.

MARTIN: And the big one: CanBuildFrom. [click] Repr is the caller's own type, and CanBuildFrom is a factory for builders of it.
ODD: Look at that signature. "SeqLike of A comma Repr. Implicit bf: CanBuildFrom of Repr, A, Repr."
MARTIN: [click] But palindromize of a String is a String!
ODD: It works. And it scared a generation of Scala developers away from the Scaladoc.
MARTIN: You got your String back.
ODD: I got my String back. And a therapist.

## 19 · tc2-9 — Scala 2.9 · 2011 · 15 s · 9:10

MARTIN: 2.9, 2011.
ODD: Paul Phillips: a thousand and twenty-three commits. I take it back. He wasn't a compiler. He was the compiler.

## 20 · f2-9 — New in Scala 2.9 · 15 s · 9:25

MARTIN: Parallel collections, the App trait, and the one we need: tails.
ODD: The release where one library method gets its own slide. Low bar.

## 21 · m2-8-again — tails finds the palindromic suffix · 10 s · 9:40

MARTIN: Remember that search, zero to length, with a find and a dot get? [click]

## 22 · m2-9 — tails finds the palindromic suffix · 25 s · 9:50

> One click.

MARTIN: [click] tails: every suffix in turn, and the first palindrome is where we start mirroring.
ODD: Same algorithm. Same cost.
MARTIN: But no index arithmetic, and no dot get.
ODD: Fewer ways to be wrong. The only metric I trust.

## 23 · tc2-10 — Scala 2.10 · 2013 · 15 s · 10:15

MARTIN: 2.10, January 2013. So many contributors, we can only show sixty.
ODD: And Eugene Burmako arrives, with macros. I have feelings about that.
MARTIN: Not today.

## 24 · f2-10 — New in Scala 2.10 · 20 s · 10:30

MARTIN: 2.10 gives us three things at once: implicit classes, value classes, and the plus-colon and colon-plus extractors.
ODD: And string interpolation. The one feature everybody actually uses.
MARTIN: Not in this talk.

## 25 · o2-8-again — Implicit value classes · 5 s · 10:50

MARTIN: Remember our wrapper, and its implicit def? [click]

## 26 · o2-10 — Implicit value classes · 35 s · 10:55

> One click.

MARTIN: [click] One declaration: an implicit class. And extends AnyVal makes it a value class: usually, no allocation at all.
ODD: "Usually." Put it in a collection and it boxes.
MARTIN: Usually beats always.
ODD: And the field has to be public. Every Seq now has a public member called xs.
MARTIN: That's 2.11's problem.

## 27 · m2-9-again — +: and :+ extractors · 5 s · 11:30

MARTIN: And now, the index loop. Odd's favourite. [click]

## 28 · m2-10 — +: and :+ extractors · 40 s · 11:35

> Two clicks.

MARTIN: [click] x plus-colon middle colon-plus y: peel off both ends, and compare them.
ODD: That's pretty. I'll admit that's pretty.
MARTIN: [click] One match replaces the whole loop, recursing on the middle.
ODD: And on a List, colon-plus walks the whole list, every time. On a String, it copies. Quietly n squared.
MARTIN: On a Vector it's fine!
ODD: Ask me about it in the Q&A.

## 29 · tc2-11 — Scala 2.11 · 2014 · 10 s · 12:15

MARTIN: 2.11, 2014. Jason Zaugg takes the lead in commits.
ODD: The calm after the storm.

## 30 · f2-11 — New in Scala 2.11 · 20 s · 12:25

MARTIN: A consolidation release: a modular library, case classes beyond twenty-two fields.
ODD: And the one we need: a value class may hide its field. My complaint from two slides ago.

## 31 · o2-10-again — Value classes may hide their field · 5 s · 12:45

MARTIN: So: that public field. [click]

## 32 · o2-11 — Value classes may hide their field · 15 s · 12:50

> One click.

MARTIN: [click] One word: private.
ODD: That's it? A whole release, for one word?
MARTIN: You asked for it.
ODD: I did. Thank you, 2.11.

## 33 · tc2-12 — Scala 2.12 · 2016 · 10 s · 13:05

MARTIN: 2.12, 2016. Built on Java 8.
ODD: Scala finally gets the JVM's lambdas. After Java. Let that sink in.

## 34 · f2-12 — New in Scala 2.12 · 20 s · 13:15

MARTIN: SAM conversion: a lambda can implement any trait with one abstract method.
ODD: Traits become interfaces, Either is finally right-biased.
MARTIN: And our anonymous classes are about to disappear.

## 35 · e2-8-again — SAM conversion: lambdas implement traits · 5 s · 13:35

MARTIN: Eq, with its anonymous classes. [click]

## 36 · e2-12 — SAM conversion: lambdas implement traits · 20 s · 13:40

> One click. Odd's first concession: take a breath before it.

MARTIN: [click] And now a lambda implements a one-method trait.
ODD: Two anonymous classes, two lines. ... All right. I concede. That's just better.
MARTIN: Can I get that in writing?
ODD: No.

## 37 · tc2-13 — Scala 2.13 · 2019 · 15 s · 14:00

> Martin finds Odd's name in the cloud and points at it.

MARTIN: 2.13, 2019. Wait. Odd. Is that your name in there?
ODD: Allegedly.
MARTIN: So you're partly responsible for what comes next.
ODD: No comment.

## 38 · f2-13 — New in Scala 2.13 · 15 s · 14:15

MARTIN: The second collections rewrite. CanBuildFrom is gone.
ODD: Rest in peace. Nobody cried.
MARTIN: In comes IsSeq and BuildFrom. And LazyList, and literal types.

## 39 · m2-10-again — IsSeq and BuildFrom · 5 s · 14:30

ODD: And the 2.12 code stops compiling for String. [click]

## 40 · m2-13 — IsSeq and BuildFrom · 50 s · 14:35

> Two clicks.

MARTIN: StringOps isn't a collection anymore, so we need IsSeq. [click] Anything that can be read as a Seq, String included.
ODD: And then this. A0. With a refinement: type A equals A0.
MARTIN: Scala 2 can't use isSeq.A in the same parameter list, so the element type sneaks in as an extra type parameter.
ODD: That's the wart.
MARTIN: [click] But BuildFrom builds the result in one call. And "racecar".isPalindrome finally compiles.
ODD: Twelve years.
MARTIN: You said that.

## 41 · tc3-0 — Scala 3.0 · 2021 · 20 s · 15:25

MARTIN: And then Scala 3, 2021. Dotty, since 2012: twenty-one thousand commits, three hundred and twenty-one authors.
ODD: A whole new compiler. What could possibly go wrong.
MARTIN: Surprisingly little.

## 42 · f3-0 — New in Scala 3.0 · 15 s · 15:45

MARTIN: given and using, extension methods, optional braces, top-level definitions.
ODD: Four of them in amber. This is where the ceremony collapses.
MARTIN: Are you... excited?
ODD: Cautiously.

## 43 · e2-12-again — given indentation and extensions · 5 s · 16:00

MARTIN: Our Eq, Scala 2 style. Watch. [click]

## 44 · e3-0 — given indentation and extensions · 40 s · 16:05

> Four clicks, one per bubble.

MARTIN: [click] Braces give way to indentation.
ODD: Python developers, you're welcome.
MARTIN: [click] And Eq gets an extension: x triple-equals y, wherever an Eq is a given in scope.
ODD: [click] implicit def becomes given. Same idea, honest name.
MARTIN: [click] And the lambdas shrink to placeholders.
ODD: Underscore equals-equals underscore. Very readable. If you already know what it means.

## 45 · m2-13-again — using extensions · 10 s · 16:45

MARTIN: Now the methods. And the implicit class we've been carrying around since 2.10. [click]

## 46 · m3-0-is — using extensions · 25 s · 16:55

> One click; the next click morphs palindromize.

MARTIN: isPalindrome becomes an extension. [click] An extension and a context bound replace the object, the wrapper class and the implicit.
ODD: And look down there: the class's isPalindrome is commented out.
MARTIN: Nobody calls it anymore. [click]

## 47 · m3-0-ops — using extensions · 25 s · 17:20

> Two clicks.

MARTIN: Now palindromize. [click] Triple-equals and isPalindrome: extensions, called like methods.
ODD: [click] And IsSeq moves into the extension's using clause, so the later clauses can see isSeq.A.
MARTIN: No A0. No refinement.
ODD: The wart is gone. I'm... almost moved.

## 48 · m3-0 — using extensions · 15 s · 17:45

> The click commented the whole class out; one more click brings its bubble.

MARTIN: And the class?
ODD: [click] Obsolete. The extensions do its job.
MARTIN: Shall we delete it?
ODD: Leave it commented out. For the archaeologists.

## 49 · tc3-6 — Scala 3.6 · 2024 · 10 s · 18:00

MARTIN: Scala 3.6, 2024.
ODD: Technically 3.6.2. 3.6.0 was published by accident.
MARTIN: We don't talk about 3.6.0.

## 50 · f3-6 — New in Scala 3.6 · 15 s · 18:10

MARTIN: The type class story gets finished: named context bounds, and a new given syntax.
ODD: SIP-64. Somebody really cared about this.

## 51 · e3-0-again — The new given syntax · 5 s · 18:25

MARTIN: Our given, one more time. [click]

## 52 · e3-6 — The new given syntax · 15 s · 18:30

> One click.

MARTIN: [click] given universal: for every A, an Eq of A.
ODD: It reads like the sentence you'd say out loud. That's new.

## 53 · m3-0-again — Context bounds get names · 5 s · 18:45

MARTIN: And the methods. [click]

## 54 · m3-6 — Context bounds get names · 30 s · 18:50

> One click.

MARTIN: [click] A context bound with a name: Repr, colon IsSeq, as isSeq. And isSeq.A still works.
ODD: The using clause folds into the type parameters.
MARTIN: isPalindrome doesn't change at all. And 3.7, 3.8, 3.9 change nothing we use. Which means: we're done.
ODD: Are we, though?

## 55 · cloud4-0 — Scala 4.0 · 15 s · 19:20

> Deadpan. Let the two names sit there.

MARTIN: Well. There is one more release.
ODD: Scala 4.0. Two authors.
MARTIN: A very exclusive community.
ODD: Fastest code review in Scala history.

## 56 · f4-0 — New in Scala 4.0 · 20 s · 19:35

MARTIN: One feature. Prolog extractors.
ODD: A variable named twice in a pattern must unify with the same value.
MARTIN: If you remember Prolog from university: you're welcome. If you don't: also welcome.

## 57 · m3-6-again — Prolog extractors · 5 s · 19:55

MARTIN: Here's 3.6's isPalindrome. Watch the match. [click]

## 58 · m4-0 — Prolog extractors · 30 s · 20:00

> One click.

MARTIN: [click] x on both ends. So both ends must be the same x.
ODD: No triple-equals. The comparison disappears into the pattern.
MARTIN: Beautiful.
ODD: It doesn't compile.
MARTIN: Yet.
ODD: And which equality would it use? Ours is the caller's Eq.
MARTIN: That's a 4.1 problem.

## 59 · takeaways — What the palindrome taught us · 45 s · 20:30

> Drop the comedy a notch. Slower, to the room.

MARTIN: So what did one tiny function teach us?
ODD: That the ideas were all there in 2007. Generics, type classes, implicit conversions.
MARTIN: And every release made them cheaper to write. The machinery arrived when the problem asked for it.
ODD: Not every step was a win. CanBuildFrom worked, and scared people. 2.13's refinement was a detour.
MARTIN: And Scala 3 simply says what Scala 2 had to spell out.
ODD: ... I'll give you that one.

## 60 · thanks — Thank you · 20 s · 21:15

> Stand together. Leave the QR code up for the questions.

MARTIN: Every version, from 2.5.1 to 3.9.0, compiles and is tested. It's all on GitHub.
ODD: Every diff in EVOLUTION.md. And every bad decision explained in DESIGN.md.
BOTH: Thank you! Questions?

---

# Reserve: only if the Q&A asks

Jump to these from the presenter view (type the number, then Enter), and back to 60 when done.

## 61 · r-indexedseq — On an IndexedSeq, index like it's 2007

> For "isn't the extractor slow?"

ODD: On a String, the extractor copies at every step. Forty thousand characters: over half a second.
MARTIN: And the fix is the 2007 index loop again, as an extension on IndexedSeq. Six hundredths of a millisecond.
ODD: Sometimes the old ways win.

## 62 · r-stringslice — Or make slicing free, like Java 6 did

> For "can't the slices share?"

MARTIN: Or let the slices share, the way java.lang.String did before Java 7u6. tail and init stop copying.
ODD: Until a three-character slice keeps a hundred-megabyte string alive. That's why Java dropped it.
MARTIN: Under a tenth of a millisecond, though.

## 63 · r-linear — Knuth–Morris–Pratt in O(n)

> For "can palindromize be linear?"

MARTIN: Yes: Knuth–Morris–Pratt. The longest palindromic suffix is the longest suffix that's also a prefix of the reverse.
ODD: One pass, still through Eq. Nineteen milliseconds instead of seven seconds, on forty thousand characters.
MARTIN: And fifteen lines of index tables. That's an algorithms talk, not a Scala one.
