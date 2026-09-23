import org.scalatest.funsuite.AnyFunSuite

class PalindromeSuite extends AnyFunSuite {
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

  test("isPalindrom checks valid sentence palindromes ignoring whitespace") {
    assert(Palindrome.isPalindrom("never odd or even"))
    assert(Palindrome.isPalindrom("race car"))
    assert(Palindrome.isPalindrom("nurses run"))
    assert(Palindrome.isPalindrom("was it a car or a cat i saw"))
    assert(Palindrome.isPalindrom("step on no pets"))
    assert(Palindrome.isPalindrom("live on time emit no evil"))
  }

  test("isPalindrom checks non-palindrome sentences") {
    assert(!Palindrome.isPalindrom("this is not a palindrome"))
    assert(!Palindrome.isPalindrom("hello world from scala"))
    assert(!Palindrome.isPalindrom("scala is great"))
  }
}
