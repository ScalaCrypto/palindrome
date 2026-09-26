// Scala 3.1.3
import scala.annotation.tailrec
import scala.collection.BuildFrom
import scala.collection.generic.IsSeq
import PalindromeResult.*

// Equality as a type class: the caller decides what "the same element" means.
trait Eq[A]:
  def eqv(x: A, y: A): Boolean

object Eq:
  // The default, found in Eq's implicit scope: universal equality.
  given universal[A]: Eq[A] = _ == _

  // Opt-in: pass it with `using`, or bring it into scope as a given.
  val caseInsensitive: Eq[Char] = _.toLower == _.toLower

// The answer says more than true or false: where a non-palindrome breaks.
enum PalindromeResult:
  case Palindrome
  case BreaksAt(index: Int)

// Top-level extension methods: "racecar".isPalindrome, or called as a function, isPalindrome(xs).
extension [A](xs: Seq[A])(using eq: Eq[A])
  def checkPalindrome: PalindromeResult =
    // x +: middle :+ y peels off the first and the last element in one pattern.
    @tailrec
    def loop(ys: Seq[A], from: Int): PalindromeResult = ys match
      case x +: middle :+ y =>
        if eq.eqv(x, y) then loop(middle, from + 1) else BreaksAt(from)
      case _ => Palindrome
    loop(xs, 0)

  def isPalindrome: Boolean = xs.checkPalindrome == Palindrome

// The shortest palindrome starting with xs: mirror only what comes before its longest palindromic suffix
// ("abcb".palindromize == "abcba"). The Eq decides what counts as a palindrome.
// IsSeq lets any Repr, String included, be read as a Seq; BuildFrom builds a new Repr.
extension [Repr](xs: Repr)(using seq: IsSeq[Repr])
  def palindromize(using eq: Eq[seq.A], bf: BuildFrom[Repr, seq.A, Repr]): Repr =
    val ops = seq(xs)
    val start = palindromicSuffixStart(ops.toSeq)
    val b = bf.newBuilder(xs)
    b ++= ops
    b ++= ops.reverseIterator.drop(ops.length - start)
    b.result()

// Where the longest palindromic suffix starts; xs.drop(xs.length) is empty, hence a palindrome.
private def palindromicSuffixStart[A](xs: Seq[A])(using Eq[A]): Int =
  (0 to xs.length).find(i => xs.drop(i).isPalindrome).get
