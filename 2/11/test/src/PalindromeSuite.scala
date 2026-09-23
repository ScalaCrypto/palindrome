import org.scalatest.FunSuite

class PalindromeSuite extends FunSuite {
  test("isPalindrom checks empty and single character strings with default ignore") {
    assert(Palindrome.isPalindrom(""))
    assert(Palindrome.isPalindrom("a"))
  }

  test("isPalindrom checks valid palindrome strings with default ignore") {
    assert(Palindrome.isPalindrom("racecar"))
    assert(Palindrome.isPalindrom("noon"))
    assert(Palindrome.isPalindrom("kayak"))
    assert(Palindrome.isPalindrom("madam"))
    assert(Palindrome.isPalindrom("12321"))
  }

  test("isPalindrom checks non-palindrome strings with default ignore") {
    assert(!Palindrome.isPalindrom("hello"))
    assert(!Palindrome.isPalindrom("world"))
    assert(!Palindrome.isPalindrom("scala"))
    assert(!Palindrome.isPalindrom("palindrome"))
  }

  test("isPalindrom does not ignore whitespace by default") {
    assert(!Palindrome.isPalindrom("never odd or even"))
    assert(!Palindrome.isPalindrom("race car"))
  }

  test("isPalindrom checks valid sentence palindromes ignoring whitespace") {
    val ignoreSpaces = List(' ')
    assert(Palindrome.isPalindrom("never odd or even", ignoreSpaces))
    assert(Palindrome.isPalindrom("race car", ignoreSpaces))
    assert(Palindrome.isPalindrom("nurses run", ignoreSpaces))
    assert(Palindrome.isPalindrom("was it a car or a cat i saw", ignoreSpaces))
    assert(Palindrome.isPalindrom("step on no pets", ignoreSpaces))
    assert(Palindrome.isPalindrom("live on time emit no evil", ignoreSpaces))
  }

  test("isPalindrom checks custom ignored characters") {
    assert(Palindrome.isPalindrom("race!car!", List('!')))
    assert(Palindrome.isPalindrom("madam, i'm adam", List(' ', ',', '\'')))
  }

  test("isPalindrom checks non-palindrome sentences with ignore parameter") {
    val ignoreSpaces = List(' ')
    assert(!Palindrome.isPalindrom("this is not a palindrome", ignoreSpaces))
    assert(!Palindrome.isPalindrom("hello world from scala", ignoreSpaces))
    assert(!Palindrome.isPalindrom("scala is great", ignoreSpaces))
  }
}
