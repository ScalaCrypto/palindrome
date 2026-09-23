extension (s: String) {
  def isPalindrom(ignore: List[Char] = Nil): Boolean = {
    if (s == null) false
    else {
      val clean = s.filter(c => !ignore.contains(c))
      clean == clean.reverse
    }
  }

  def isPalindrome(ignore: List[Char] = Nil): Boolean = isPalindrom(ignore)
}

object Palindrome {
  def isPalindrom(s: String, ignore: List[Char] = Nil): Boolean = {
    if (s == null) false
    else s.isPalindrom(ignore)
  }

  def isPalindrome(s: String, ignore: List[Char] = Nil): Boolean = {
    if (s == null) false
    else s.isPalindrome(ignore)
  }
}
