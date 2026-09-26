import org.scalatest.funsuite.AnyFunSuite
import Palindrome._
import PalindromeResult.BreaksAt

class PalindromeSuite extends AnyFunSuite {
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

  test("isPalindrome and checkPalindrome are also methods on any Seq") {
    assert(Seq("a", "b", "a").isPalindrome)
    assert("racecar".toList.isPalindrome)
    assert(!Vector(1, 2).isPalindrome)
    assert(List(1, 2, 3).checkPalindrome == BreaksAt(0))
  }

  test("checkPalindrome reports where a non-palindrome breaks") {
    assert(checkPalindrome("racecar") == PalindromeResult.Palindrome)
    assert(checkPalindrome("hello") == BreaksAt(0))
    assert(checkPalindrome("abcxba") == BreaksAt(2))
    assert(checkPalindrome(Seq(1, 2, 3, 4, 2, 1)) == BreaksAt(2))
  }

  test("equality is case-sensitive by default") {
    assert(!isPalindrome("Racecar"))
    assert(checkPalindrome("Racecar") == BreaksAt(0))
  }

  test("another Eq can be passed explicitly") {
    assert(isPalindrome("Racecar")(Eq.caseInsensitive))
    assert("Racecar".toList.isPalindrome(Eq.caseInsensitive))
  }

  test("an implicit Eq in scope takes precedence over the default") {
    implicit val caseInsensitive: Eq[Char] = Eq.caseInsensitive
    assert(isPalindrome("Racecar"))
    assert(checkPalindrome("Racecar") == PalindromeResult.Palindrome)
  }
}
