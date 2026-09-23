// Scala 2.13.18
object Palindrome {
  def isPalindrome(s: String, ignore: Set[Char] = Set.empty): Boolean = {
    if (s == null) false
    else {
      val clean = s.filter(c => !ignore.contains(c))
      clean == clean.reverse
    }
  }
}
