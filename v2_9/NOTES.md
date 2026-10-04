# `tails` finds the palindromic suffix

- **`seq.tails.indexWhere(isPalindrome(_))`**: the 2.9 library adds `tails` to sequences, an iterator over `seq`,
  `seq.drop(1)`, and so on down to the empty sequence. `indexWhere` gives the position of the first suffix that's a
  palindrome, which is where the mirrored part starts. It's the same search as 2.8's
  `(0 to seq.length).find(i => isPalindrome(seq.drop(i))).get`, in the same order and at the same cost, without
  the index arithmetic or the `.get`: the empty suffix always matches. 2.8 rejects it ("value tails is not a member
  of Seq[A]"). This is a library change, not a language one.

2.10 to 3.9 keep it.
