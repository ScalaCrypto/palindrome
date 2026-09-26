// Scala 2.13.18
import scala.annotation.tailrec
import scala.collection.BuildFrom
import scala.collection.generic.IsSeq
import scala.language.implicitConversions

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

  // The shortest palindrome starting with xs: mirror only what comes before its longest palindromic suffix
  // ("abcb" -> "abcba"). The Eq decides what counts as a palindrome.
  // IsSeq lets any Repr, String included, be read as a Seq; BuildFrom builds a new Repr.
  def palindromize[Repr, A0](xs: Repr)(
      implicit seq: IsSeq[Repr] { type A = A0 }, eq: Eq[A0], bf: BuildFrom[Repr, A0, Repr]): Repr = {
    val ops = seq(xs)
    val start = palindromicSuffixStart(ops.toSeq)
    val b = bf.newBuilder(xs)
    b ++= ops
    b ++= ops.reverseIterator.drop(ops.length - start)
    b.result()
  }

  // Where the longest palindromic suffix starts; xs.drop(xs.length) is empty, hence a palindrome.
  private def palindromicSuffixStart[A](xs: Seq[A])(implicit eq: Eq[A]): Int =
    (0 to xs.length).find(i => isPalindrome(xs.drop(i))).get

  // Method syntax (xs.isPalindrome, "abc".palindromize) for anything IsSeq accepts, String included.
  class PalindromeOps[Repr, S <: IsSeq[Repr]](xs: Repr, seq: S) {
    def checkPalindrome(implicit eq: Eq[seq.A]): PalindromeResult = Palindrome.checkPalindrome(seq(xs).toSeq)
    def isPalindrome(implicit eq: Eq[seq.A]): Boolean = Palindrome.isPalindrome(seq(xs).toSeq)
    def palindromize(implicit eq: Eq[seq.A], bf: BuildFrom[Repr, seq.A, Repr]): Repr =
      Palindrome.palindromize[Repr, seq.A](xs)(seq: seq.type, eq, bf)
  }

  implicit def palindromeOps[Repr](xs: Repr)(implicit seq: IsSeq[Repr]): PalindromeOps[Repr, seq.type] =
    new PalindromeOps(xs, seq)
}
