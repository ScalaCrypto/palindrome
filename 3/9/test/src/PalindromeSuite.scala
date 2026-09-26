import org.scalatest.funsuite.AnyFunSuite
import PalindromeResult.*

class PalindromeSuite extends AnyFunSuite:
  test("empty and single-element sequences are palindromes") {
    assert("".isPalindrome)
    assert("a".isPalindrome)
    assert(Seq.empty[Int].isPalindrome)
    assert(Seq(1).isPalindrome)
  }

  test("isPalindrome checks palindrome strings") {
    assert("racecar".isPalindrome)
    assert("noon".isPalindrome)
    assert("kayak".isPalindrome)
    assert("madam".isPalindrome)
    assert("12321".isPalindrome)
  }

  test("isPalindrome checks non-palindrome strings") {
    assert(!"hello".isPalindrome)
    assert(!"world".isPalindrome)
    assert(!"scala".isPalindrome)
    assert(!"palindrome".isPalindrome)
    assert(!"race car".isPalindrome)
  }

  test("isPalindrome is generic over Seq[A]") {
    assert(Seq(1, 2, 3, 2, 1).isPalindrome)
    assert(List("a", "b", "a").isPalindrome)
    assert(Vector('x', 'y', 'y', 'x').isPalindrome)
    assert(!Seq(1, 2, 3).isPalindrome)
  }

  test("isPalindrome and checkPalindrome can also be called as functions") {
    assert(isPalindrome("racecar"))
    assert(isPalindrome(Seq(1, 2, 1)))
    assert(!isPalindrome("hello"))
    assert(checkPalindrome(List(1, 2, 3)) == BreaksAt(0))
  }

  test("checkPalindrome reports where a non-palindrome breaks") {
    assert("racecar".checkPalindrome == Palindrome)
    assert("hello".checkPalindrome == BreaksAt(0))
    assert("abcxba".checkPalindrome == BreaksAt(2))
    assert(Seq(1, 2, 3, 4, 2, 1).checkPalindrome == BreaksAt(2))
  }

  test("equality is case-sensitive by default") {
    assert(!"Racecar".isPalindrome)
    assert("Racecar".checkPalindrome == BreaksAt(0))
  }

  test("another Eq can be passed explicitly") {
    assert("Racecar".isPalindrome(using Eq.caseInsensitive))
    assert(isPalindrome("Racecar")(using Eq.caseInsensitive))
  }

  test("a given Eq in scope takes precedence over the default") {
    given Eq[Char] = Eq.caseInsensitive
    assert("Racecar".isPalindrome)
    assert("Racecar".checkPalindrome == Palindrome)
  }

  test("a BreaksAt can be matched by field name") {
    val index = "abcxba".checkPalindrome match
      case BreaksAt(index = i) => i
      case Palindrome          => -1
    assert(index == 2)
  }
