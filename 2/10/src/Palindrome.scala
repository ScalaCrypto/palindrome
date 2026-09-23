object Palindrome {
  def isPalindrom(s: String): Boolean = {
    if (s == null) false
    else s == s.reverse
  }
}
