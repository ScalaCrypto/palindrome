# New given syntax and named context bounds

- **`given universal: [A] => Eq[A]`**: the 3.6 given syntax reads as "for every `A`, an `Eq[A]`", replacing
  `given universal[A]: Eq[A]`.
- **`[A: Eq as eq]`**: a context bound can now be named, so the `using eq: Eq[A]` clause folds into the type
  parameter. `eq` stays usable by name in the body.

3.5 rejects both.
