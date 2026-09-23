// Scala 2.5.1
object Palindrome {
  def isPalindrome(s: String): Boolean = isPalindrome(s, Nil)

  def isPalindrome(s: String, ignore: List[Char]): Boolean = {
    if (s == null) false
    else {
      val clean = s.filter(c => !ignore.contains(c))
      clean == clean.reverse
    }
  }
}
