// Stand-in for ScalaTest's ShouldMatchers (see FunSuite.scala). Covers only
// `left should be (right)`, which checks that left == right.
package org.scalatest.matchers

import org.scalatest.TestFailedException

trait ShouldMatchers {
  class Be(val right: Any)

  def be(right: Any): Be = new Be(right)

  class AnyShouldWrapper(left: Any) {
    def should(be: Be): Unit =
      if (left != be.right) throw new TestFailedException(left + " was not " + be.right)
  }

  implicit def convertToAnyShouldWrapper(left: Any): AnyShouldWrapper = new AnyShouldWrapper(left)
}
