// Scala 3.0.2
import scala.annotation.tailrec
import scala.collection.BuildFrom
import scala.collection.generic.IsSeq

// Equality as a type class: the caller decides what "the same element" means.
trait Eq[A]:
  def eqv(x: A, y: A): Boolean

object Eq:
  // The default, found in Eq's implicit scope: universal equality.
  given universal[A]: Eq[A] = _ == _

  // Opt-in: pass it with `using`, or bring it into scope as a given.
  val caseInsensitive: Eq[Char] = _.toLower == _.toLower

// A top-level extension method: "racecar".isPalindrome, or called as a function, isPalindrome(xs).
extension [A](xs: Seq[A])(using eq: Eq[A])
  // x +: middle :+ y peels off the first and the last element in one pattern.
  @tailrec
  def isPalindrome: Boolean = xs match
    case x +: middle :+ y => eq.eqv(x, y) && middle.isPalindrome
    case _ => true

// The shortest palindrome starting with xs: mirror only what comes before its longest palindromic suffix
// ("abcb".palindromize == "abcba"). The Eq decides what counts as a palindrome; the empty suffix always is one.
// IsSeq lets any Repr, String included, be read as a Seq; BuildFrom builds a new Repr.
extension [Repr](xs: Repr)(using seq: IsSeq[Repr])
  def palindromize(using eq: Eq[seq.A], bf: BuildFrom[Repr, seq.A, Repr]): Repr =
    val ops = seq(xs)
    val start = (0 to ops.length).find(i => ops.toSeq.drop(i).isPalindrome).get
    val b = bf.newBuilder(xs)
    b ++= ops
    b ++= ops.reverseIterator.drop(ops.length - start)
    b.result()

