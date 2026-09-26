// Scala 2.10.7
import scala.annotation.tailrec
import scala.collection.SeqLike
import scala.collection.generic.CanBuildFrom

// Equality as a type class: the caller decides what "the same element" means.
trait Eq[A] {
  def eqv(x: A, y: A): Boolean
}

object Eq {
  // The default, found in Eq's implicit scope: universal equality.
  implicit def universal[A]: Eq[A] = new Eq[A] {
    def eqv(x: A, y: A): Boolean = x == y
  }

  // Opt-in: pass it explicitly, or bring it into scope as an implicit.
  val caseInsensitive: Eq[Char] = new Eq[Char] {
    def eqv(x: Char, y: Char): Boolean = x.toLower == y.toLower
  }
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

  // The shortest palindrome starting with xs: mirror only what comes before its longest palindromic suffix
  // ("abcb" -> "abcba"). The Eq decides what counts as a palindrome.
  // CanBuildFrom supplies a builder for the input's own type (Repr), so a String gives a String.
  def palindromize[A, Repr](xs: SeqLike[A, Repr])(implicit eq: Eq[A], bf: CanBuildFrom[Repr, A, Repr]): Repr = {
    val start = palindromicSuffixStart(xs.toSeq)
    val b = bf(xs.repr)
    b ++= xs.iterator
    b ++= xs.reverseIterator.drop(xs.length - start)
    b.result
  }

  // Where the longest palindromic suffix starts; xs.drop(xs.length) is empty, hence a palindrome.
  private def palindromicSuffixStart[A](xs: Seq[A])(implicit eq: Eq[A]): Int =
    (0 to xs.length).find(i => isPalindrome(xs.drop(i))).get

  // Method syntax (xs.isPalindrome) through an implicit value class; Repr lets palindromize keep the type.
  implicit class PalindromeOps[A, Repr](val xs: SeqLike[A, Repr]) extends AnyVal {
    def checkPalindrome(implicit eq: Eq[A]): PalindromeResult = Palindrome.checkPalindrome(xs.toSeq)
    def isPalindrome(implicit eq: Eq[A]): Boolean = Palindrome.isPalindrome(xs.toSeq)
    def palindromize(implicit eq: Eq[A], bf: CanBuildFrom[Repr, A, Repr]): Repr = Palindrome.palindromize(xs)
  }
}
