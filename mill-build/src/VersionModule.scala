package millbuild

import mill.*, scalalib.*

// Shared setup for the version modules (2/<minor>, 3/<minor>). Each version's
// package.mill.yaml sets its scalaVersion, plus scalaTestDep and jvmId where
// that version needs something other than the defaults.
trait VersionModule extends ScalaModule {
  def scalaTestDep: T[String] = "org.scalatest::scalatest:3.2.19"

  object test extends ScalaTests with TestModule.ScalaTest {
    def mvnDeps = Seq(Dep.parse(VersionModule.this.scalaTestDep()))
  }
}
