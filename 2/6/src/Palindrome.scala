// Scala 2.6.1
object Palindrome {
  def isPalindrome(s: String): Boolean = isPalindrome(s, Set.empty[Char])

  def isPalindrome(s: String, ignore: Set[Char]): Boolean = {
    if (s == null) false
    else {
      val clean = s.filter(c => !ignore.contains(c))
      clean == clean.reverse
    }
  }
}
