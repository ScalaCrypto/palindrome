import org.scalatest.FunSuite
import org.scalatest.matchers.ShouldMatchers
import Palindrome._

class PalindromeSuite extends FunSuite with ShouldMatchers {
  test("empty and single-element sequences are palindromes") {
    isPalindrome("") should be (true)
    isPalindrome("a") should be (true)
    isPalindrome(List[Int]()) should be (true)
    isPalindrome(List(1)) should be (true)
  }

  test("two-element sequences with equal elements are palindromes") {
    isPalindrome("aa") should be (true)
    isPalindrome(List(1, 1)) should be (true)
  }

  test("two-element sequences with different elements are not palindromes") {
    isPalindrome("ab") should be (false)
    isPalindrome(List(1, 2)) should be (false)
  }

  test("isPalindrome accepts palindrome strings") {
    isPalindrome("racecar") should be (true)
    isPalindrome("noon") should be (true)
    isPalindrome("kayak") should be (true)
    isPalindrome("madam") should be (true)
    isPalindrome("12321") should be (true)
  }

  test("isPalindrome rejects non-palindrome strings") {
    isPalindrome("hello") should be (false)
    isPalindrome("world") should be (false)
    isPalindrome("scala") should be (false)
    isPalindrome("palindrome") should be (false)
    isPalindrome("race car") should be (false)
  }

  test("isPalindrome is generic over Seq[A]") {
    isPalindrome(List(1, 2, 3, 2, 1)) should be (true)
    isPalindrome(List("a", "b", "a")) should be (true)
    isPalindrome(List('x', 'y', 'y', 'x')) should be (true)
    isPalindrome(List(1, 2, 3)) should be (false)
  }

  test("isPalindrome is also a method on any Seq") {
    List("a", "b", "a").isPalindrome should be (true)
    "racecar".toList.isPalindrome should be (true)
    List(1, 2).isPalindrome should be (false)
  }

  test("isPalindrome finds a mismatch inside matching ends") {
    isPalindrome("abcxba") should be (false)
    isPalindrome(List(1, 2, 3, 4, 2, 1)) should be (false)
  }

  test("equality is case-sensitive by default") {
    isPalindrome("Racecar") should be (false)
  }

  test("another Eq can be passed explicitly") {
    isPalindrome("Racecar")(Eq.caseInsensitive) should be (true)
    "Racecar".toList.isPalindrome(Eq.caseInsensitive) should be (true)
  }

  test("an implicit Eq in scope takes precedence over the default") {
    implicit val caseInsensitive: Eq[Char] = Eq.caseInsensitive
    isPalindrome("Racecar") should be (true)
  }

  test("palindromize builds the shortest palindrome starting with the input") {
    val s: Seq[Char] = palindromize("abcb")
    s.mkString("") should be ("abcba")
    palindromize(List(1, 2, 3)).toList should be (List(1, 2, 3, 2, 1))
    List(1, 2).palindromize.toList should be (List(1, 2, 1))
    palindromize("abb").mkString("") should be ("abba")
    palindromize("racecar").mkString("") should be ("racecar")
    palindromize("").length should be (0)
    isPalindrome(palindromize("scala")) should be (true)
  }

  test("palindromize uses the Eq in scope") {
    implicit val caseInsensitive: Eq[Char] = Eq.caseInsensitive
    palindromize("abA").mkString("") should be ("abA")
  }
}
