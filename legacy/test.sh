#!/usr/bin/env bash
# Builds and tests the Scala versions Mill can't build (2.5-2.9) by calling each
# version's own scalac directly. See "Pre-2.10 Versions" in STATE.md for why.
#
# Usage: legacy/test.sh [version ...]    e.g. legacy/test.sh 2.7 2.9
#        With no arguments, tests all of 2.5-2.9.
#
# Needs coursier's `cs` on the PATH (https://get-coursier.io), curl and tar.
# Downloads (JDK 8, a JDK 7 rt.jar, compilers, ScalaTest) are cached; build
# output goes to out/legacy/.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cache="$root/out/legacy"

# version | Scala release | ScalaTest dependency, or "stand-in" | scalac option for the Java boot classpath
#
# ScalaTest must be a release built with the same Scala version (older compilers
# can't read newer Scala signatures); none with FunSuite exists for 2.5 or 2.6,
# so those use legacy/scalatest-stand-in. Before 2.10, Scala artifacts carry the
# full Scala version (scalatest_2.8.2) or none (scalatest). 2.5-2.7 name the boot
# classpath option -bootclasspath; 2.8+ -javabootclasspath.
versions="
2.5 2.5.1 stand-in                            -bootclasspath
2.6 2.6.1 stand-in                            -bootclasspath
2.7 2.7.7 org.scalatest:scalatest:1.0         -bootclasspath
2.8 2.8.2 org.scalatest:scalatest_2.8.2:1.8   -javabootclasspath
2.9 2.9.3 org.scalatest:scalatest_2.9.3:1.9.2 -javabootclasspath
"

command -v cs >/dev/null || { echo "legacy/test.sh needs coursier's cs: https://get-coursier.io" >&2; exit 1; }

# These compilers can't read JDK 8+ class files, so they run on JDK 8 but read
# the Java standard library from a JDK 7 rt.jar. The rt.jar is only read, never
# run, so the x86_64 build works on any architecture.
jdk7_rt_jar() {
  local name sha256
  case "$(uname -s)" in
    Darwin) name=zulu7.56.0.11-ca-jdk7.0.352-macosx_x64
            sha256=31909aa6233289f8f1d015586825587e95658ef59b632665e1e49fc33a2cdf06 ;;
    Linux)  name=zulu7.56.0.11-ca-jdk7.0.352-linux_x64
            sha256=8a7387c1ed151474301b6553c6046f865dc6c1e1890bcf106acc2780c55727c8 ;;
    *)      echo "legacy/test.sh: unsupported OS $(uname -s)" >&2; return 1 ;;
  esac
  if [ ! -d "$cache/$name" ]; then
    echo "Downloading JDK 7 ($name) for its rt.jar ..." >&2
    mkdir -p "$cache"
    curl -fsSL -o "$cache/$name.tar.gz" "https://cdn.azul.com/zulu/bin/$name.tar.gz"
    echo "$sha256  $cache/$name.tar.gz" | shasum -a 256 -c - >/dev/null \
      || { echo "legacy/test.sh: checksum mismatch for $name.tar.gz" >&2; rm -f "$cache/$name.tar.gz"; return 1; }
    tar -xzf "$cache/$name.tar.gz" -C "$cache"
    rm "$cache/$name.tar.gz"
  fi
  find "$cache/$name" -path '*/jre/lib/rt.jar' | head -1
}

test_version() {
  local version=$1 scala=$2 scalatest=$3 boot_option=$4
  local dir="$root/2/${version#2.}" out="$cache/classes/$version"
  echo
  echo "=== Scala $scala ($scalatest)"

  local header
  header="$(head -1 "$dir/src/Palindrome.scala")"
  if [ "$header" != "// Scala $scala" ]; then
    echo "$dir/src/Palindrome.scala starts with '$header', expected '// Scala $scala'" >&2
    return 1
  fi

  local library compiler test_classpath=""
  local sources=("$dir/src/Palindrome.scala" "$dir/test/src/PalindromeSuite.scala")
  library="$(cs fetch --classpath --intransitive "org.scala-lang:scala-library:$scala")" || return 1
  # The compiler goes with its library on the classpath: 2.5.1's POM doesn't declare it.
  compiler="$(cs fetch --classpath "org.scala-lang:scala-compiler:$scala")" || return 1
  if [ "$scalatest" = stand-in ]; then
    sources+=("$root"/legacy/scalatest-stand-in/*.scala)
  else
    # Intransitive: old ScalaTest POMs may pull in a scala-library of another version.
    test_classpath=":$(cs fetch --classpath --intransitive "$scalatest")" || return 1
  fi

  rm -rf "$out" && mkdir -p "$out"
  "$java" -cp "$compiler:$library" scala.tools.nsc.Main "$boot_option" "$rt_jar" \
    -classpath "$library$test_classpath" -d "$out" "${sources[@]}" || return 1
  "$java" -cp "$library$test_classpath:$out" org.scalatest.tools.Runner -o -s PalindromeSuite
}

java="$(cs java-home --jvm zulu:8)/bin/java"
rt_jar="$(jdk7_rt_jar)"

selected=("$@")
[ ${#selected[@]} -gt 0 ] || selected=(2.5 2.6 2.7 2.8 2.9)

passed=() failed=()
for version in "${selected[@]}"; do
  row="$(echo "$versions" | awk -v v="$version" '$1 == v')"
  if [ -z "$row" ]; then
    echo "legacy/test.sh: unknown version $version (known: 2.5 2.6 2.7 2.8 2.9)" >&2
    failed+=("$version")
    continue
  fi
  # shellcheck disable=SC2086 # split the table row into arguments
  if test_version $row; then passed+=("$version"); else failed+=("$version"); fi
done

echo
echo "Passed: ${passed[*]:-none}"
echo "Failed: ${failed[*]:-none}"
[ ${#failed[@]} -eq 0 ]
