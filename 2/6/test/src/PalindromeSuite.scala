import org.scalatest.FunSuite
import Palindrome._

class PalindromeSuite extends FunSuite {
  test("empty and single-element sequences are palindromes") {
    assert(isPalindrome(""))
    assert(isPalindrome("a"))
    assert(isPalindrome(List[Int]()))
    assert(isPalindrome(List(1)))
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
    assert(isPalindrome(List(1, 2, 3, 2, 1)))
    assert(isPalindrome(List("a", "b", "a")))
    assert(isPalindrome(List('x', 'y', 'y', 'x')))
    assert(!isPalindrome(List(1, 2, 3)))
  }

  test("isPalindrome is also a method on any Seq") {
    assert(List("a", "b", "a").isPalindrome)
    assert("racecar".toList.isPalindrome)
    assert(!List(1, 2).isPalindrome)
  }

  test("isPalindrome finds a mismatch inside matching ends") {
    assert(!isPalindrome("abcxba"))
    assert(!isPalindrome(List(1, 2, 3, 4, 2, 1)))
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
    val s: Seq[Char] = palindromize("abcb")
    assert(s.mkString("") == "abcba")
    assert(palindromize(List(1, 2, 3)).toList == List(1, 2, 3, 2, 1))
    assert(List(1, 2).palindromize.toList == List(1, 2, 1))
    assert(palindromize("abb").mkString("") == "abba")
    assert(palindromize("racecar").mkString("") == "racecar")
    assert(palindromize("").length == 0)
    assert(isPalindrome(palindromize("scala")))
  }

  test("palindromize uses the Eq in scope") {
    implicit val caseInsensitive: Eq[Char] = Eq.caseInsensitive
    assert(palindromize("abA").mkString("") == "abA")
  }
}
