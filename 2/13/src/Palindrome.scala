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
  // IsSeq lets any Repr, String included, be read as a Seq; BuildFrom builds a new Repr.
  def palindromize[Repr, A0](xs: Repr)(
      implicit seq: IsSeq[Repr] { type A = A0 }, eq: Eq[A0], bf: BuildFrom[Repr, A0, Repr]): Repr = {
    val ops = seq(xs)
    val start = (0 to ops.length).find(i => isPalindrome(ops.toSeq.drop(i))).get
    val b = bf.newBuilder(xs)
    b ++= ops
    b ++= ops.reverseIterator.drop(ops.length - start)
    b.result()
  }

  // Method syntax (xs.isPalindrome, "abc".palindromize) for anything IsSeq accepts, String included.
  class PalindromeOps[Repr, S <: IsSeq[Repr]](xs: Repr, seq: S) {
    def isPalindrome(implicit eq: Eq[seq.A]): Boolean = Palindrome.isPalindrome(seq(xs).toSeq)
    def palindromize(implicit eq: Eq[seq.A], bf: BuildFrom[Repr, seq.A, Repr]): Repr =
      Palindrome.palindromize[Repr, seq.A](xs)(seq: seq.type, eq, bf)
  }

  implicit def palindromeOps[Repr](xs: Repr)(implicit seq: IsSeq[Repr]): PalindromeOps[Repr, seq.type] =
    new PalindromeOps(xs, seq)
}
