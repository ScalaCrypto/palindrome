def isPalindrom(s: String, ignore: List[Char] = Nil): Boolean = {
  if (s == null) false
  else {
    val clean = s.filter(c => !ignore.contains(c))
    clean == clean.reverse
  }
}

object Palindrome {
  def isPalindrom(s: String, ignore: List[Char] = Nil): Boolean = {
    if (s == null) false
    else {
      val clean = s.filter(c => !ignore.contains(c))
      clean == clean.reverse
    }
  }
}
