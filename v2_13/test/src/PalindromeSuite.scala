import org.scalatest.funsuite.AnyFunSuite
import org.scalatest.matchers.should.Matchers
import Palindrome._

class PalindromeSuite extends AnyFunSuite with Matchers {
  test("empty and single-element sequences are palindromes") {
    isPalindrome("") shouldBe true
    isPalindrome("a") shouldBe true
    isPalindrome(Seq.empty[Int]) shouldBe true
    isPalindrome(Seq(1)) shouldBe true
  }

  test("two-element sequences with equal elements are palindromes") {
    isPalindrome("aa") shouldBe true
    isPalindrome(Seq(1, 1)) shouldBe true
  }

  test("two-element sequences with different elements are not palindromes") {
    isPalindrome("ab") shouldBe false
    isPalindrome(Seq(1, 2)) shouldBe false
  }

  test("isPalindrome accepts palindrome strings") {
    isPalindrome("racecar") shouldBe true
    isPalindrome("noon") shouldBe true
    isPalindrome("kayak") shouldBe true
    isPalindrome("madam") shouldBe true
    isPalindrome("12321") shouldBe true
  }

  test("isPalindrome rejects non-palindrome strings") {
    isPalindrome("hello") shouldBe false
    isPalindrome("world") shouldBe false
    isPalindrome("scala") shouldBe false
    isPalindrome("palindrome") shouldBe false
    isPalindrome("race car") shouldBe false
  }

  test("isPalindrome is generic over Seq[A]") {
    isPalindrome(Seq(1, 2, 3, 2, 1)) shouldBe true
    isPalindrome(List("a", "b", "a")) shouldBe true
    isPalindrome(Vector('x', 'y', 'y', 'x')) shouldBe true
    isPalindrome(Seq(1, 2, 3)) shouldBe false
  }

  test("isPalindrome is also a method on any Seq") {
    Seq("a", "b", "a").isPalindrome shouldBe true
    "racecar".isPalindrome shouldBe true
    Vector(1, 2).isPalindrome shouldBe false
  }

  test("isPalindrome finds a mismatch inside matching ends") {
    isPalindrome("abcxba") shouldBe false
    isPalindrome(Seq(1, 2, 3, 4, 2, 1)) shouldBe false
  }

  test("equality is case-sensitive by default") {
    isPalindrome("Racecar") shouldBe false
  }

  test("another Eq can be passed explicitly") {
    isPalindrome("Racecar")(Eq.caseInsensitive) shouldBe true
    "Racecar".isPalindrome(Eq.caseInsensitive) shouldBe true
  }

  test("an implicit Eq in scope takes precedence over the default") {
    implicit val caseInsensitive: Eq[Char] = Eq.caseInsensitive
    isPalindrome("Racecar") shouldBe true
  }

  test("palindromize builds the shortest palindrome starting with the input") {
    val s: String = "abcb".palindromize
    val l: List[Int] = List(1, 2, 3).palindromize
    val v: Vector[Char] = palindromize(Vector('x', 'y'))
    s shouldBe "abcba"
    l shouldBe List(1, 2, 3, 2, 1)
    v shouldBe Vector('x', 'y', 'x')
    palindromize("abb") shouldBe "abba"
    palindromize("racecar") shouldBe "racecar"
    palindromize("") shouldBe ""
    "scala".palindromize.isPalindrome shouldBe true
    Vector(1, 2).palindromize.isPalindrome shouldBe true
  }

  test("palindromize uses the Eq in scope") {
    implicit val caseInsensitive: Eq[Char] = Eq.caseInsensitive
    "abA".palindromize shouldBe "abA"
  }
}
