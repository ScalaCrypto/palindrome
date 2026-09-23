// Scala 3.0.2
extension (s: String)
  def isPalindrome: Boolean = isPalindrome(Set.empty[Char])
  def isPalindrome(ignore: Set[Char]): Boolean =
    if s == null then false
    else
      val clean = s.filter(c => !ignore.contains(c))
      clean == clean.reverse

object Palindrome:
  def isPalindrome(s: String): Boolean = if s == null then false else s.isPalindrome
  def isPalindrome(s: String, ignore: Set[Char]): Boolean = if s == null then false else s.isPalindrome(ignore)
