# New given syntax and named context bounds

- **`given universal: [A] => Eq[A]`**: the 3.6 given syntax reads as "for every `A`, an `Eq[A]`", replacing
  `given universal[A]: Eq[A]`.
- **`[Repr: IsSeq as isSeq]`**: a context bound can now be named, so `palindromize`'s `using isSeq: IsSeq[Repr]`
  clause folds into the type parameter, and `isSeq.A` still works in the `BuildFrom`. `isPalindrome` needs no name
  for its `Eq`, since `===` comes from the given itself, so it keeps 3.0's `[A: Eq]`.

3.5 rejects both. 3.7 to 3.9 are identical.
