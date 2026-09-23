// A minimal stand-in for ScalaTest's FunSuite, for Scala 2.5 and 2.6: no
// ScalaTest release with FunSuite can be read by those compilers. It covers
// only what the PalindromeSuite tests use (test and assert). Compiled
// together with each version's sources by legacy/test.sh; not the real ScalaTest.
package org.scalatest

class TestFailedException(message: String) extends RuntimeException(message)

trait FunSuite {
  private var tests: List[(String, () => Unit)] = Nil

  protected def test(name: String)(body: => Unit): Unit = tests = (name, () => body) :: tests

  protected def assert(condition: Boolean): Unit =
    if (!condition) throw new TestFailedException("assertion failed")

  // Runs the tests in declaration order, prints a ScalaTest-style summary and
  // returns the number of failed tests.
  def execute(): Int = {
    var failed = 0
    for ((name, body) <- tests.reverse) {
      try {
        body()
        println("- " + name)
      } catch {
        case e: Throwable =>
          failed = failed + 1
          println("- " + name + " *** FAILED *** " + e)
      }
    }
    println("Tests: succeeded " + (tests.length - failed) + ", failed " + failed)
    failed
  }
}
