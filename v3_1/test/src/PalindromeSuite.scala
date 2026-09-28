import org.scalatest.funsuite.AnyFunSuite
import org.scalatest.matchers.should.Matchers

class PalindromeSuite extends AnyFunSuite with Matchers:
  test("empty and single-element sequences are palindromes") {
    "".isPalindrome shouldBe true
    "a".isPalindrome shouldBe true
    Seq.empty[Int].isPalindrome shouldBe true
    Seq(1).isPalindrome shouldBe true
  }

  test("two-element sequences with equal elements are palindromes") {
    "aa".isPalindrome shouldBe true
    Seq(1, 1).isPalindrome shouldBe true
  }

  test("two-element sequences with different elements are not palindromes") {
    "ab".isPalindrome shouldBe false
    Seq(1, 2).isPalindrome shouldBe false
  }

  test("isPalindrome accepts palindrome strings") {
    "racecar".isPalindrome shouldBe true
    "noon".isPalindrome shouldBe true
    "kayak".isPalindrome shouldBe true
    "madam".isPalindrome shouldBe true
    "12321".isPalindrome shouldBe true
  }

  test("isPalindrome rejects non-palindrome strings") {
    "hello".isPalindrome shouldBe false
    "world".isPalindrome shouldBe false
    "scala".isPalindrome shouldBe false
    "palindrome".isPalindrome shouldBe false
    "race car".isPalindrome shouldBe false
  }

  test("isPalindrome is generic over Seq[A]") {
    Seq(1, 2, 3, 2, 1).isPalindrome shouldBe true
    List("a", "b", "a").isPalindrome shouldBe true
    Vector('x', 'y', 'y', 'x').isPalindrome shouldBe true
    Seq(1, 2, 3).isPalindrome shouldBe false
  }

  test("isPalindrome can also be called as a function") {
    isPalindrome("racecar") shouldBe true
    isPalindrome(Seq(1, 2, 1)) shouldBe true
    isPalindrome("hello") shouldBe false
  }

  test("isPalindrome finds a mismatch inside matching ends") {
    "abcxba".isPalindrome shouldBe false
    Seq(1, 2, 3, 4, 2, 1).isPalindrome shouldBe false
  }

  test("equality is case-sensitive by default") {
    "Racecar".isPalindrome shouldBe false
  }

  test("another Eq can be passed explicitly") {
    "Racecar".isPalindrome(using Eq.caseInsensitive) shouldBe true
    isPalindrome("Racecar")(using Eq.caseInsensitive) shouldBe true
  }

  test("a given Eq in scope takes precedence over the default") {
    given Eq[Char] = Eq.caseInsensitive
    "Racecar".isPalindrome shouldBe true
  }

  test("palindromize builds the shortest palindrome starting with the input") {
    val s: String = "abcb".palindromize
    val l: List[Int] = List(1, 2, 3).palindromize
    val v: Vector[Char] = Vector('x', 'y').palindromize
    s shouldBe "abcba"
    l shouldBe List(1, 2, 3, 2, 1)
    v shouldBe Vector('x', 'y', 'x')
    palindromize("abb") shouldBe "abba"
    "racecar".palindromize shouldBe "racecar"
    "".palindromize shouldBe ""
    "scala".palindromize.isPalindrome shouldBe true
  }

  test("palindromize uses the Eq in scope") {
    given Eq[Char] = Eq.caseInsensitive
    "abA".palindromize shouldBe "abA"
  }
