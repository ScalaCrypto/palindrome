// Scala 2.6.1

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

// Scala 2 has no top-level definitions, so the functions live in an object.
object Palindrome {
  def isPalindrome[A](xs: Seq[A])(implicit eq: Eq[A]): Boolean = {
    // Tail-recursive, so scalac compiles it to a loop; @tailrec to check that arrives in 2.8.
    def loop(from: Int): Boolean = {
      val to = xs.length - 1 - from
      from >= to || (eq.eqv(xs(from), xs(to)) && loop(from + 1))
    }
    loop(0)
  }

  // The shortest palindrome starting with xs: mirror only what comes before its longest palindromic suffix
  // ("abcb" -> "abcba"). The Eq decides what counts as a palindrome; the empty suffix always is one.
  // Without a way to build "the same collection type", generic code can only promise a Seq.
  def palindromize[A](xs: Seq[A])(implicit eq: Eq[A]): Seq[A] = {
    val start = (0 to xs.length).find(i => isPalindrome(xs.drop(i))).get
    xs ++ xs.take(start).reverse
  }

  // Method syntax (xs.isPalindrome) through an implicit conversion to a wrapper.
  class PalindromeOps[A](xs: Seq[A]) {
    def isPalindrome(implicit eq: Eq[A]): Boolean = Palindrome.isPalindrome(xs)
    def palindromize(implicit eq: Eq[A]): Seq[A] = Palindrome.palindromize(xs)
  }

  implicit def palindromeOps[A](xs: Seq[A]): PalindromeOps[A] = new PalindromeOps(xs)
}
