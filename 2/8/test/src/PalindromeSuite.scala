import org.scalatest.FunSuite

class PalindromeSuite extends FunSuite {
  test("isPalindrom checks empty and single character strings") {
    assert(Palindrome.isPalindrom(""))
    assert(Palindrome.isPalindrom("a"))
  }

  test("isPalindrom checks valid palindrome strings") {
    assert(Palindrome.isPalindrom("racecar"))
    assert(Palindrome.isPalindrom("noon"))
    assert(Palindrome.isPalindrom("kayak"))
    assert(Palindrome.isPalindrom("madam"))
    assert(Palindrome.isPalindrom("12321"))
  }

  test("isPalindrom checks non-palindrome strings") {
    assert(!Palindrome.isPalindrom("hello"))
    assert(!Palindrome.isPalindrom("world"))
    assert(!Palindrome.isPalindrom("scala"))
    assert(!Palindrome.isPalindrom("palindrome"))
  }
}
