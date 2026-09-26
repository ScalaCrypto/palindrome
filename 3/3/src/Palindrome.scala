// Scala 3.3.8
import scala.annotation.tailrec
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
