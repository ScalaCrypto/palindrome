import org.scalatest.FunSuite

class PalindromeSuite extends FunSuite {
  test("isPalindrome checks empty and single character strings with default ignore") {
    assert(Palindrome.isPalindrome(""))
    assert(Palindrome.isPalindrome("a"))
  }

  test("isPalindrome checks valid palindrome strings with default ignore") {
    assert(Palindrome.isPalindrome("racecar"))
    assert(Palindrome.isPalindrome("noon"))
    assert(Palindrome.isPalindrome("kayak"))
    assert(Palindrome.isPalindrome("madam"))
    assert(Palindrome.isPalindrome("12321"))
  }

  test("isPalindrome checks non-palindrome strings with default ignore") {
    assert(!Palindrome.isPalindrome("hello"))
    assert(!Palindrome.isPalindrome("world"))
    assert(!Palindrome.isPalindrome("scala"))
    assert(!Palindrome.isPalindrome("palindrome"))
  }

  test("isPalindrome does not ignore whitespace by default") {
    assert(!Palindrome.isPalindrome("never odd or even"))
    assert(!Palindrome.isPalindrome("race car"))
  }

  test("isPalindrome checks valid sentence palindromes ignoring whitespace") {
    val ignoreSpaces = List(' ')
    assert(Palindrome.isPalindrome("never odd or even", ignoreSpaces))
    assert(Palindrome.isPalindrome("race car", ignoreSpaces))
    assert(Palindrome.isPalindrome("nurses run", ignoreSpaces))
    assert(Palindrome.isPalindrome("was it a car or a cat i saw", ignoreSpaces))
    assert(Palindrome.isPalindrome("step on no pets", ignoreSpaces))
    assert(Palindrome.isPalindrome("live on time emit no evil", ignoreSpaces))
  }

  test("isPalindrome checks custom ignored characters") {
    assert(Palindrome.isPalindrome("race!car!", List('!')))
    assert(Palindrome.isPalindrome("madam, i'm adam", List(' ', ',', '\'')))
  }

  test("isPalindrome checks non-palindrome sentences with ignore parameter") {
    val ignoreSpaces = List(' ')
    assert(!Palindrome.isPalindrome("this is not a palindrome", ignoreSpaces))
    assert(!Palindrome.isPalindrome("hello world from scala", ignoreSpaces))
    assert(!Palindrome.isPalindrome("scala is great", ignoreSpaces))
  }
}
