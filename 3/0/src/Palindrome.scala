def isPalindrom(s: String): Boolean = {
  if (s == null) false
  else {
    val clean = s.replaceAll("\\s", "")
    clean == clean.reverse
  }
}

object Palindrome {
  def isPalindrom(s: String): Boolean = {
    if (s == null) false
    else {
      val clean = s.replaceAll("\\s", "")
      clean == clean.reverse
    }
  }
}
