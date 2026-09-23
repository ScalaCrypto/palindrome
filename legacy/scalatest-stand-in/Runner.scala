// Stand-in for ScalaTest's command-line Runner (see FunSuite.scala). Accepts the
// same "-s <suite class>" arguments legacy/test.sh passes to the real Runner,
// and like it exits with 1 when a test fails.
package org.scalatest.tools

import org.scalatest.FunSuite

object Runner {
  def main(args: Array[String]): Unit = {
    var suites: List[String] = Nil
    var i = 0
    while (i < args.length) {
      if (args(i) == "-s" && i + 1 < args.length) {
        suites = args(i + 1) :: suites
        i = i + 1
      }
      i = i + 1
    }
    var failed = 0
    for (name <- suites.reverse) {
      println(name + ":")
      failed = failed + Class.forName(name).newInstance().asInstanceOf[FunSuite].execute()
    }
    if (failed > 0) System.exit(1)
  }
}
