// Scala 2.12.21
import scala.annotation.tailrec

// Equality as a type class: the caller decides what "the same element" means.
trait Eq[A] {
  def eqv(x: A, y: A): Boolean
}

object Eq {
  // The default, found in Eq's implicit scope: universal equality.
  implicit def universal[A]: Eq[A] = (x, y) => x == y

  // Opt-in: pass it explicitly, or bring it into scope as an implicit.
  val caseInsensitive: Eq[Char] = (x, y) => x.toLower == y.toLower
}

// The answer says more than true or false: where a non-palindrome breaks.
sealed trait PalindromeResult
object PalindromeResult {
  case object Palindrome extends PalindromeResult
  final case class BreaksAt(index: Int) extends PalindromeResult
}

// Scala 2 has no top-level definitions, so the functions live in an object.
object Palindrome {
  def checkPalindrome[A](xs: Seq[A])(implicit eq: Eq[A]): PalindromeResult = {
    // x +: middle :+ y peels off the first and the last element in one pattern.
    @tailrec
    def loop(ys: Seq[A], from: Int): PalindromeResult = ys match {
      case x +: middle :+ y =>
        if (eq.eqv(x, y)) loop(middle, from + 1) else PalindromeResult.BreaksAt(from)
      case _ => PalindromeResult.Palindrome
    }
    loop(xs, 0)
  }

  def isPalindrome[A](xs: Seq[A])(implicit eq: Eq[A]): Boolean =
    checkPalindrome(xs) == PalindromeResult.Palindrome

  // Method syntax (xs.isPalindrome) through an implicit value class.
  implicit class PalindromeOps[A](private val xs: Seq[A]) extends AnyVal {
    def checkPalindrome(implicit eq: Eq[A]): PalindromeResult = Palindrome.checkPalindrome(xs)
    def isPalindrome(implicit eq: Eq[A]): Boolean = Palindrome.isPalindrome(xs)
  }
}
