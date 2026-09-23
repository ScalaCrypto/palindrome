// Scala 3.4.3
extension (s: String) {
  def isPalindrom: Boolean = isPalindrom(Nil)
  def isPalindrom(ignore: List[Char]): Boolean = {
    if (s == null) false
    else {
      val clean = s.filter(c => !ignore.contains(c))
      clean == clean.reverse
    }
  }

  def isPalindrome: Boolean = isPalindrom
  def isPalindrome(ignore: List[Char]): Boolean = isPalindrom(ignore)
}

object Palindrome {
  def isPalindrom(s: String): Boolean = if (s == null) false else s.isPalindrom
  def isPalindrom(s: String, ignore: List[Char]): Boolean = if (s == null) false else s.isPalindrom(ignore)

  def isPalindrome(s: String): Boolean = if (s == null) false else s.isPalindrome
  def isPalindrome(s: String, ignore: List[Char]): Boolean = if (s == null) false else s.isPalindrome(ignore)
}
