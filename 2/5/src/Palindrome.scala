// Scala 2.5.1

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
    def eqv(x: Char, y: Char): Boolean = Character.toLowerCase(x) == Character.toLowerCase(y)
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
    // Tail-recursive, so scalac compiles it to a loop; @tailrec to check that arrives in 2.8.
    def loop(from: Int): PalindromeResult = {
      val to = xs.length - 1 - from
      if (from >= to) PalindromeResult.Palindrome
      else if (eq.eqv(xs(from), xs(to))) loop(from + 1)
      else PalindromeResult.BreaksAt(from)
    }
    loop(0)
  }

  def isPalindrome[A](xs: Seq[A])(implicit eq: Eq[A]): Boolean =
    checkPalindrome(xs) == PalindromeResult.Palindrome

  // The shortest palindrome starting with xs: mirror only what comes before its longest palindromic suffix
  // ("abcb" -> "abcba"). The Eq decides what counts as a palindrome.
  // Without a way to build "the same collection type", generic code can only promise a Seq.
  def palindromize[A](xs: Seq[A])(implicit eq: Eq[A]): Seq[A] = xs ++ xs.take(palindromicSuffixStart(xs)).reverse

  // Where the longest palindromic suffix starts; xs.drop(xs.length) is empty, hence a palindrome.
  private def palindromicSuffixStart[A](xs: Seq[A])(implicit eq: Eq[A]): Int =
    (0 to xs.length).find(i => isPalindrome(xs.drop(i))).get

  // Method syntax (xs.isPalindrome) through an implicit conversion to a wrapper.
  class PalindromeOps[A](xs: Seq[A]) {
    def checkPalindrome(implicit eq: Eq[A]): PalindromeResult = Palindrome.checkPalindrome(xs)
    def isPalindrome(implicit eq: Eq[A]): Boolean = Palindrome.isPalindrome(xs)
    def palindromize(implicit eq: Eq[A]): Seq[A] = Palindrome.palindromize(xs)
  }

  implicit def palindromeOps[A](xs: Seq[A]): PalindromeOps[A] = new PalindromeOps(xs)
}
