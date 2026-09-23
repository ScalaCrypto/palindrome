import org.scalatest.funsuite.AnyFunSuite

class PalindromeSuite extends AnyFunSuite:
  test("extension method isPalindrome on String checks empty and single character strings") {
    assert("".isPalindrome)
    assert("a".isPalindrome)
    assert("".isPalindrom)
    assert("a".isPalindrom)
    assert(isPalindrome(""))
    assert(isPalindrome("a"))
    assert(isPalindrom(""))
    assert(isPalindrom("a"))
    assert(Palindrome.isPalindrome(""))
    assert(Palindrome.isPalindrome("a"))
    assert(Palindrome.isPalindrom(""))
    assert(Palindrome.isPalindrom("a"))
  }

  test("extension method isPalindrome on String checks valid palindrome strings") {
    assert("racecar".isPalindrome)
    assert("noon".isPalindrome)
    assert("kayak".isPalindrome)
    assert("madam".isPalindrome)
    assert("12321".isPalindrome)
    assert("racecar".isPalindrom)
    assert(isPalindrome("racecar"))
    assert(isPalindrom("racecar"))
    assert(Palindrome.isPalindrome("racecar"))
  }

  test("extension method isPalindrome on String checks non-palindrome strings") {
    assert(!"hello".isPalindrome)
    assert(!"world".isPalindrome)
    assert(!"scala".isPalindrome)
    assert(!"palindrome".isPalindrome)
    assert(!"hello".isPalindrom)
    assert(!isPalindrome("hello"))
    assert(!isPalindrom("hello"))
    assert(!Palindrome.isPalindrome("hello"))
  }

  test("extension method isPalindrome does not ignore whitespace by default") {
    assert(!"never odd or even".isPalindrome)
    assert(!"race car".isPalindrome)
    assert(!"never odd or even".isPalindrom)
    assert(!isPalindrome("never odd or even"))
    assert(!isPalindrom("never odd or even"))
    assert(!Palindrome.isPalindrome("never odd or even"))
  }

  test("extension method isPalindrome checks valid sentence palindromes ignoring whitespace") {
    val ignoreSpaces = List(' ')
    assert("never odd or even".isPalindrome(ignoreSpaces))
    assert("race car".isPalindrome(ignoreSpaces))
    assert("nurses run".isPalindrome(ignoreSpaces))
    assert("was it a car or a cat i saw".isPalindrome(ignoreSpaces))
    assert("step on no pets".isPalindrome(ignoreSpaces))
    assert("live on time emit no evil".isPalindrome(ignoreSpaces))
    assert("race car".isPalindrom(ignoreSpaces))

    assert(Palindrome.isPalindrome("never odd or even", ignoreSpaces))
    assert(Palindrome.isPalindrome("race car", ignoreSpaces))
    assert(Palindrome.isPalindrome("nurses run", ignoreSpaces))
    assert(Palindrome.isPalindrome("was it a car or a cat i saw", ignoreSpaces))
    assert(Palindrome.isPalindrome("step on no pets", ignoreSpaces))
    assert(Palindrome.isPalindrome("live on time emit no evil", ignoreSpaces))
    assert(Palindrome.isPalindrom("race car", ignoreSpaces))
  }

  test("extension method isPalindrome checks custom ignored characters") {
    assert("race!car!".isPalindrome(List('!')))
    assert("madam, i'm adam".isPalindrome(List(' ', ',', '\'')))
    assert("race!car!".isPalindrom(List('!')))

    assert(Palindrome.isPalindrome("race!car!", List('!')))
    assert(Palindrome.isPalindrome("madam, i'm adam", List(' ', ',', '\'')))
    assert(Palindrome.isPalindrom("race!car!", List('!')))
  }

  test("extension method isPalindrome checks non-palindrome sentences with ignore parameter") {
    val ignoreSpaces = List(' ')
    assert(!"this is not a palindrome".isPalindrome(ignoreSpaces))
    assert(!"hello world from scala".isPalindrome(ignoreSpaces))
    assert(!"scala is great".isPalindrome(ignoreSpaces))
    assert(!"this is not a palindrome".isPalindrom(ignoreSpaces))

    assert(!Palindrome.isPalindrome("this is not a palindrome", ignoreSpaces))
    assert(!Palindrome.isPalindrome("hello world from scala", ignoreSpaces))
    assert(!Palindrome.isPalindrome("scala is great", ignoreSpaces))
    assert(!Palindrome.isPalindrom("this is not a palindrome", ignoreSpaces))
  }
