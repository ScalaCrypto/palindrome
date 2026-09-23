import mill._, scalalib._

trait CommonScalaModule extends ScalaModule {
  object test extends ScalaTests with TestModule.ScalaTest {
    def ivyDeps = T {
      val sv = scalaVersion()
      if (sv.startsWith("3.")) Agg(ivy"org.scalatest::scalatest:3.2.19")
      else if (sv.startsWith("2.13.") || sv.startsWith("2.12.")) Agg(ivy"org.scalatest::scalatest:3.2.19")
      else if (sv.startsWith("2.11.")) Agg(ivy"org.scalatest::scalatest:3.2.18")
      else if (sv.startsWith("2.10.")) Agg(ivy"org.scalatest::scalatest:3.0.9")
      else if (sv.startsWith("2.9.")) Agg(ivy"org.scalatest::scalatest:1.9.2")
      else if (sv.startsWith("2.8.")) Agg(ivy"org.scalatest::scalatest:1.8")
      else if (sv.startsWith("2.7.")) Agg(ivy"org.scalatest:scalatest:1.3")
      else Agg(ivy"org.scalatest:scalatest:0.9.5")
    }
  }
}

object `2` extends Module {
  object `5` extends CommonScalaModule { def scalaVersion = "2.5.1" }
  object `6` extends CommonScalaModule { def scalaVersion = "2.6.1" }
  object `7` extends CommonScalaModule { def scalaVersion = "2.7.7" }
  object `8` extends CommonScalaModule { def scalaVersion = "2.8.2" }
  object `9` extends CommonScalaModule { def scalaVersion = "2.9.3" }
  object `10` extends CommonScalaModule { def scalaVersion = "2.10.7" }
  object `11` extends CommonScalaModule { def scalaVersion = "2.11.12" }
  object `12` extends CommonScalaModule { def scalaVersion = "2.12.21" }
  object `13` extends CommonScalaModule { def scalaVersion = "2.13.18" }
}

object `3` extends Module {
  object `0` extends CommonScalaModule { def scalaVersion = "3.0.2" }
  object `1` extends CommonScalaModule { def scalaVersion = "3.1.3" }
  object `2` extends CommonScalaModule { def scalaVersion = "3.2.2" }
  object `3` extends CommonScalaModule { def scalaVersion = "3.3.8" }
  object `4` extends CommonScalaModule { def scalaVersion = "3.4.3" }
  object `5` extends CommonScalaModule { def scalaVersion = "3.5.2" }
  object `6` extends CommonScalaModule { def scalaVersion = "3.6.4" }
  object `7` extends CommonScalaModule { def scalaVersion = "3.7.4" }
  object `8` extends CommonScalaModule { def scalaVersion = "3.8.4" }
  object `9` extends CommonScalaModule { def scalaVersion = "3.9.0" }
}
