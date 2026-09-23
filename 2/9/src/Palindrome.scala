// Scala 2.9.3
object Palindrome {
  def isPalindrome(s: String, ignore: Set[Char] = Set.empty): Boolean = {
    if (s == null) false
    else {
      val clean = s.filter(c => !ignore.contains(c))
      clean == clean.reverse
    }
  }
}
