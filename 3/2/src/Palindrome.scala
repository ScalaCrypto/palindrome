// Scala 3.2.2
import scala.annotation.targetName

extension (s: String)
  def isPalindrome: Boolean = isPalindrome(Set.empty[Char])
  def isPalindrome(ignore: Set[Char]): Boolean =
    if s == null then false
    else
      val clean = s.filter(c => !ignore.contains(c))
      clean == clean.reverse

// Same JVM signature as the extension's isPalindrome(s)(ignore), hence the @targetName.
@targetName("isPalindromeOf")
def isPalindrome(s: String, ignore: Set[Char] = Set.empty): Boolean = s.isPalindrome(ignore)
