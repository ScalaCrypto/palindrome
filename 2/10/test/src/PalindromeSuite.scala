import org.scalatest.FunSuite
import Palindrome._

class PalindromeSuite extends FunSuite {
  test("empty and single-element sequences are palindromes") {
    assert(isPalindrome(""))
    assert(isPalindrome("a"))
    assert(isPalindrome(Seq.empty[Int]))
    assert(isPalindrome(Seq(1)))
  }

  test("isPalindrome checks palindrome strings") {
    assert(isPalindrome("racecar"))
    assert(isPalindrome("noon"))
    assert(isPalindrome("kayak"))
    assert(isPalindrome("madam"))
    assert(isPalindrome("12321"))
  }

  test("isPalindrome checks non-palindrome strings") {
    assert(!isPalindrome("hello"))
    assert(!isPalindrome("world"))
    assert(!isPalindrome("scala"))
    assert(!isPalindrome("palindrome"))
    assert(!isPalindrome("race car"))
  }

  test("isPalindrome is generic over Seq[A]") {
    assert(isPalindrome(Seq(1, 2, 3, 2, 1)))
    assert(isPalindrome(List("a", "b", "a")))
    assert(isPalindrome(Vector('x', 'y', 'y', 'x')))
    assert(!isPalindrome(Seq(1, 2, 3)))
  }

  test("isPalindrome is also a method on any Seq") {
    assert(Seq("a", "b", "a").isPalindrome)
    assert("racecar".toList.isPalindrome)
    assert(!Vector(1, 2).isPalindrome)
  }

  test("isPalindrome finds a mismatch inside matching ends") {
    assert(!isPalindrome("abcxba"))
    assert(!isPalindrome(Seq(1, 2, 3, 4, 2, 1)))
  }

  test("equality is case-sensitive by default") {
    assert(!isPalindrome("Racecar"))
  }

  test("another Eq can be passed explicitly") {
    assert(isPalindrome("Racecar")(Eq.caseInsensitive))
    assert("Racecar".toList.isPalindrome(Eq.caseInsensitive))
  }

  test("an implicit Eq in scope takes precedence over the default") {
    implicit val caseInsensitive: Eq[Char] = Eq.caseInsensitive
    assert(isPalindrome("Racecar"))
  }

  test("palindromize builds the shortest palindrome starting with the input") {
    val s: String = palindromize("abcb")
    val l: List[Int] = List(1, 2, 3).palindromize
    val v: Vector[Char] = palindromize(Vector('x', 'y'))
    assert(s == "abcba")
    assert(l == List(1, 2, 3, 2, 1))
    assert(v == Vector('x', 'y', 'x'))
    assert(palindromize("abb") == "abba")
    assert(palindromize("racecar") == "racecar")
    assert(palindromize("") == "")
    assert(isPalindrome(palindromize("scala")))
    assert(Vector(1, 2).palindromize.isPalindrome)
  }

  test("palindromize uses the Eq in scope") {
    implicit val caseInsensitive: Eq[Char] = Eq.caseInsensitive
    assert(palindromize("abA") == "abA")
  }
}
