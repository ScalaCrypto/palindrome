import org.scalatest.funsuite.AnyFunSuite

class PalindromeSuite extends AnyFunSuite:
  test("extension method isPalindrome on String checks empty and single character strings") {
    assert("".isPalindrome)
    assert("a".isPalindrome)
    assert(isPalindrome(""))
    assert(isPalindrome("a"))
  }

  test("extension method isPalindrome on String checks valid palindrome strings") {
    assert("racecar".isPalindrome)
    assert("noon".isPalindrome)
    assert("kayak".isPalindrome)
    assert("madam".isPalindrome)
    assert("12321".isPalindrome)
    assert(isPalindrome("racecar"))
  }

  test("extension method isPalindrome on String checks non-palindrome strings") {
    assert(!"hello".isPalindrome)
    assert(!"world".isPalindrome)
    assert(!"scala".isPalindrome)
    assert(!"palindrome".isPalindrome)
    assert(!isPalindrome("hello"))
  }

  test("extension method isPalindrome does not ignore whitespace by default") {
    assert(!"never odd or even".isPalindrome)
    assert(!"race car".isPalindrome)
    assert(!isPalindrome("never odd or even"))
  }

  test("extension method isPalindrome checks valid sentence palindromes ignoring whitespace") {
    val ignoreSpaces = Set(' ')
    assert("never odd or even".isPalindrome(ignoreSpaces))
    assert("race car".isPalindrome(ignoreSpaces))
    assert("nurses run".isPalindrome(ignoreSpaces))
    assert("was it a car or a cat i saw".isPalindrome(ignoreSpaces))
    assert("step on no pets".isPalindrome(ignoreSpaces))
    assert("live on time emit no evil".isPalindrome(ignoreSpaces))

    assert(isPalindrome("never odd or even", ignoreSpaces))
    assert(isPalindrome("race car", ignoreSpaces))
    assert(isPalindrome("nurses run", ignoreSpaces))
    assert(isPalindrome("was it a car or a cat i saw", ignoreSpaces))
    assert(isPalindrome("step on no pets", ignoreSpaces))
    assert(isPalindrome("live on time emit no evil", ignoreSpaces))
  }

  test("extension method isPalindrome checks custom ignored characters") {
    assert("race!car!".isPalindrome(Set('!')))
    assert("madam, i'm adam".isPalindrome(Set(' ', ',', '\'')))

    assert(isPalindrome("race!car!", Set('!')))
    assert(isPalindrome("madam, i'm adam", Set(' ', ',', '\'')))
  }

  test("extension method isPalindrome checks non-palindrome sentences with ignore parameter") {
    val ignoreSpaces = Set(' ')
    assert(!"this is not a palindrome".isPalindrome(ignoreSpaces))
    assert(!"hello world from scala".isPalindrome(ignoreSpaces))
    assert(!"scala is great".isPalindrome(ignoreSpaces))

    assert(!isPalindrome("this is not a palindrome", ignoreSpaces))
    assert(!isPalindrome("hello world from scala", ignoreSpaces))
    assert(!isPalindrome("scala is great", ignoreSpaces))
  }
