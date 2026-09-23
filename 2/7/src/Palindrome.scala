// Scala 2.7.7
object Palindrome {
  def isPalindrom(s: String): Boolean = isPalindrom(s, Nil)

  def isPalindrom(s: String, ignore: List[Char]): Boolean = {
    if (s == null) false
    else {
      val clean = s.filter(c => !ignore.contains(c))
      clean == clean.reverse
    }
  }

  def isPalindrome(s: String): Boolean = isPalindrom(s)
  def isPalindrome(s: String, ignore: List[Char]): Boolean = isPalindrom(s, ignore)
}
