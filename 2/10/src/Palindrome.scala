// Scala 2.10.7
object Palindrome {
  def isPalindrome(s: String, ignore: List[Char] = Nil): Boolean = {
    if (s == null) false
    else {
      val clean = s.filter(c => !ignore.contains(c))
      clean == clean.reverse
    }
  }
}
