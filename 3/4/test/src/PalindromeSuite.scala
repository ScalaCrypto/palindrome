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

  test("isPalindrom checks valid sentence palindromes ignoring whitespace") {
    assert(isPalindrom("never odd or even"))
    assert(isPalindrom("race car"))
    assert(isPalindrom("nurses run"))
    assert(isPalindrom("was it a car or a cat i saw"))
    assert(isPalindrom("step on no pets"))
    assert(isPalindrom("live on time emit no evil"))
    assert(Palindrome.isPalindrom("never odd or even"))
    assert(Palindrome.isPalindrom("race car"))
  }

  test("isPalindrom checks non-palindrome sentences") {
    assert(!isPalindrom("this is not a palindrome"))
    assert(!isPalindrom("hello world from scala"))
    assert(!isPalindrom("scala is great"))
    assert(!Palindrome.isPalindrom("this is not a palindrome"))
  }
}
