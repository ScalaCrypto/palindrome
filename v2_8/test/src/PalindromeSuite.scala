import org.scalatest.FunSuite
import org.scalatest.matchers.ShouldMatchers
import Palindrome._

class PalindromeSuite extends FunSuite with ShouldMatchers {
  test("empty and single-element sequences are palindromes") {
    isPalindrome("") should be (true)
    isPalindrome("a") should be (true)
    isPalindrome(Seq.empty[Int]) should be (true)
    isPalindrome(Seq(1)) should be (true)
  }

  test("two-element sequences with equal elements are palindromes") {
    isPalindrome("aa") should be (true)
    isPalindrome(Seq(1, 1)) should be (true)
  }

  test("two-element sequences with different elements are not palindromes") {
    isPalindrome("ab") should be (false)
    isPalindrome(Seq(1, 2)) should be (false)
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
    isPalindrome(Seq(1, 2, 3, 2, 1)) should be (true)
    isPalindrome(List("a", "b", "a")) should be (true)
    isPalindrome(Vector('x', 'y', 'y', 'x')) should be (true)
    isPalindrome(Seq(1, 2, 3)) should be (false)
  }

  test("isPalindrome is also a method on any Seq") {
    Seq("a", "b", "a").isPalindrome should be (true)
    "racecar".toList.isPalindrome should be (true)
    Vector(1, 2).isPalindrome should be (false)
  }

  test("isPalindrome finds a mismatch inside matching ends") {
    isPalindrome("abcxba") should be (false)
    isPalindrome(Seq(1, 2, 3, 4, 2, 1)) should be (false)
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
    val s: String = palindromize("abcb")
    val l: List[Int] = List(1, 2, 3).palindromize
    val v: Vector[Char] = palindromize(Vector('x', 'y'))
    s should be ("abcba")
    l should be (List(1, 2, 3, 2, 1))
    v should be (Vector('x', 'y', 'x'))
    palindromize("abb") should be ("abba")
    palindromize("racecar") should be ("racecar")
    palindromize("") should be ("")
    isPalindrome(palindromize("scala")) should be (true)
    Vector(1, 2).palindromize.isPalindrome should be (true)
  }

  test("palindromize uses the Eq in scope") {
    implicit val caseInsensitive: Eq[Char] = Eq.caseInsensitive
    palindromize("abA") should be ("abA")
  }
}
