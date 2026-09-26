# Type class instances as lambdas

- **SAM conversion**: `Eq` has a single abstract method, so from 2.12 a lambda can implement it. Two anonymous classes
  shrink to one line each. 2.11 rejects the lambdas with "missing parameter type".

2.13 is identical: its new collections and literal types don't touch this code.
