// Scala 2.12.21
import scala.annotation.tailrec
import scala.collection.SeqLike
import scala.collection.generic.CanBuildFrom

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

// Scala 2 has no top-level definitions, so the functions live in an object.
object Palindrome {
  // x +: middle :+ y peels off the first and the last element in one pattern.
  @tailrec
  def isPalindrome[A](xs: Seq[A])(implicit eq: Eq[A]): Boolean = xs match {
    case x +: middle :+ y => eq.eqv(x, y) && isPalindrome(middle)
    case _ => true
  }

  // The shortest palindrome starting with xs: mirror only what comes before its longest palindromic suffix
  // ("abcb" -> "abcba"). The Eq decides what counts as a palindrome; the empty suffix always is one.
  // CanBuildFrom supplies a builder for the input's own type (Repr), so a String gives a String.
  def palindromize[A, Repr](xs: SeqLike[A, Repr])(implicit eq: Eq[A], bf: CanBuildFrom[Repr, A, Repr]): Repr = {
    val start = (0 to xs.length).find(i => isPalindrome(xs.toSeq.drop(i))).get
    val b = bf(xs.repr)
    b ++= xs.iterator
    b ++= xs.reverseIterator.drop(xs.length - start)
    b.result
  }

  // Method syntax (xs.isPalindrome) through an implicit value class; Repr lets palindromize keep the type.
  implicit class PalindromeOps[A, Repr](private val xs: SeqLike[A, Repr]) extends AnyVal {
    def isPalindrome(implicit eq: Eq[A]): Boolean = Palindrome.isPalindrome(xs.toSeq)
    def palindromize(implicit eq: Eq[A], bf: CanBuildFrom[Repr, A, Repr]): Repr = Palindrome.palindromize(xs)
  }
}
