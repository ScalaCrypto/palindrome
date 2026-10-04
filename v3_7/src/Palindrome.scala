// Scala 3.7.4
import scala.annotation.tailrec
import scala.collection.BuildFrom
import scala.collection.generic.IsSeq

// Equality as a type class: the caller decides what "the same element" means.
trait Eq[A]:
  def eqv(x: A, y: A): Boolean
  // Infix syntax, wherever an Eq[A] is a given in scope: x === y.
  extension (x: A) def ===(y: A): Boolean = eqv(x, y)

object Eq:
  // The default, found in Eq's implicit scope: universal equality.
  given universal: [A] => Eq[A] = _ == _

  // Opt-in: pass it with `using`, or bring it into scope as a given.
  val caseInsensitive: Eq[Char] = _.toLower == _.toLower

// A top-level extension method: "racecar".isPalindrome, or called as a function, isPalindrome(xs).
extension [A: Eq](xs: Seq[A])
  // x +: middle :+ y peels off the first and the last element in one pattern.
  @tailrec
  def isPalindrome: Boolean = xs match
    case x +: middle :+ y => x === y && middle.isPalindrome
    case _ => true

// The shortest palindrome starting with xs: mirror only what comes before its longest palindromic suffix
// ("abcb".palindromize == "abcba"). The Eq decides what counts as a palindrome; the empty suffix always is one.
// IsSeq lets any Repr, String included, be read as a Seq; BuildFrom builds a new Repr.
extension [Repr: IsSeq as isSeq](xs: Repr)
  def palindromize(using eq: Eq[isSeq.A], bf: BuildFrom[Repr, isSeq.A, Repr]): Repr =
    val seq = isSeq(xs).toSeq
    val start = seq.tails.indexWhere(_.isPalindrome)
    bf.fromSpecific(xs)(seq.iterator ++ seq.take(start).reverseIterator)

