import org.scalatest.funsuite.AnyFunSuite

class PalindromeSuite extends AnyFunSuite {
  test("isPalindrom checks empty and single character strings") {
    assert(isPalindrom(""))
    assert(isPalindrom("a"))
    assert(Palindrome.isPalindrom(""))
    assert(Palindrome.isPalindrom("a"))
  }

  test("isPalindrom checks valid palindrome strings") {
    assert(isPalindrom("racecar"))
    assert(isPalindrom("noon"))
    assert(isPalindrom("kayak"))
    assert(isPalindrom("madam"))
    assert(isPalindrom("12321"))
    assert(Palindrome.isPalindrom("racecar"))
  }

  test("isPalindrom checks non-palindrome strings") {
    assert(!isPalindrom("hello"))
    assert(!isPalindrom("world"))
    assert(!isPalindrom("scala"))
    assert(!isPalindrom("palindrome"))
    assert(!Palindrome.isPalindrom("hello"))
  }
}
