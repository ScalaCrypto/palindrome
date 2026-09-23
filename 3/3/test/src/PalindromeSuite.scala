import org.scalatest.funsuite.AnyFunSuite

class PalindromeSuite extends AnyFunSuite {
  test("isPalindrom checks empty and single character strings with default ignore") {
    assert(isPalindrom(""))
    assert(isPalindrom("a"))
    assert(Palindrome.isPalindrom(""))
    assert(Palindrome.isPalindrom("a"))
  }

  test("isPalindrom checks valid palindrome strings with default ignore") {
    assert(isPalindrom("racecar"))
    assert(isPalindrom("noon"))
    assert(isPalindrom("kayak"))
    assert(isPalindrom("madam"))
    assert(isPalindrom("12321"))
    assert(Palindrome.isPalindrom("racecar"))
  }

  test("isPalindrom checks non-palindrome strings with default ignore") {
    assert(!isPalindrom("hello"))
    assert(!isPalindrom("world"))
    assert(!isPalindrom("scala"))
    assert(!isPalindrom("palindrome"))
    assert(!Palindrome.isPalindrom("hello"))
  }

  test("isPalindrom does not ignore whitespace by default") {
    assert(!isPalindrom("never odd or even"))
    assert(!isPalindrom("race car"))
    assert(!Palindrome.isPalindrom("never odd or even"))
    assert(!Palindrome.isPalindrom("race car"))
  }

  test("isPalindrom checks valid sentence palindromes ignoring whitespace") {
    val ignoreSpaces = List(' ')
    assert(isPalindrom("never odd or even", ignoreSpaces))
    assert(isPalindrom("race car", ignoreSpaces))
    assert(isPalindrom("nurses run", ignoreSpaces))
    assert(isPalindrom("was it a car or a cat i saw", ignoreSpaces))
    assert(isPalindrom("step on no pets", ignoreSpaces))
    assert(isPalindrom("live on time emit no evil", ignoreSpaces))
    assert(Palindrome.isPalindrom("never odd or even", ignoreSpaces))
    assert(Palindrome.isPalindrom("race car", ignoreSpaces))
  }

  test("isPalindrom checks custom ignored characters") {
    assert(isPalindrom("race!car!", List('!')))
    assert(isPalindrom("madam, i'm adam", List(' ', ',', '\'')))
    assert(Palindrome.isPalindrom("race!car!", List('!')))
    assert(Palindrome.isPalindrom("madam, i'm adam", List(' ', ',', '\'')))
  }

  test("isPalindrom checks non-palindrome sentences with ignore parameter") {
    val ignoreSpaces = List(' ')
    assert(!isPalindrom("this is not a palindrome", ignoreSpaces))
    assert(!isPalindrom("hello world from scala", ignoreSpaces))
    assert(!isPalindrom("scala is great", ignoreSpaces))
    assert(!Palindrome.isPalindrom("this is not a palindrome", ignoreSpaces))
  }
}
