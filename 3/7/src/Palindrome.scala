// Scala 3.7.4
extension (s: String)
  def isPalindrome: Boolean = isPalindrome(Nil)
  def isPalindrome(ignore: List[Char]): Boolean =
    if s == null then false
    else
      val clean = s.filter(c => !ignore.contains(c))
      clean == clean.reverse

object Palindrome:
  def isPalindrome(s: String): Boolean = if s == null then false else s.isPalindrome
  def isPalindrome(s: String, ignore: List[Char]): Boolean = if s == null then false else s.isPalindrome(ignore)
