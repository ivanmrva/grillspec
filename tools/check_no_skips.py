#!/usr/bin/env python3
# check_no_skips.py - a coarse, high-precision tripwire against DISABLED or WEAKENED tests.
#
# Why it exists (the test-side sibling of check_no_fakes.py): the anti-cheat rule "never add skip/xfail/
# ignore, never shrink the suite" lived only in prose - nothing mechanical caught it. A skipped test reads
# GREEN while asserting nothing; an `xfail` launders a red into an expected pass; a `.only`/`fit` silently
# shrinks the whole suite to one case; a CI test step with `|| true` or `ignoreFailures` swallows every
# failure. All of these are the same cheat as a fake in src/: the gate stays green while the system is not
# proven. In this system an unready dependency is meant to keep the test RED - red is the truthful signal,
# never a reason to skip the test.
#
# ERROR (a test disabled, laundered, or the suite shrunk - almost always the cheat):
#   - a skip/disable marker: it.skip/test.skip/describe.skip/xit/xdescribe/this.skip() (JS/TS),
#     @pytest.mark.skip/skipif/xfail, pytest.skip/xfail/importorskip, @unittest.skip, skipTest (Python),
#     t.Skip/Skipf/SkipNow (Go), #[ignore] (Rust), @Disabled/@Ignore (JVM), [Ignore]/Skip="" (C#),
#     markTestSkipped (PHP), leading skip/pending (Ruby);
#   - a focus marker that shrinks the suite: .only( / fit( / fdescribe(;
#   - a swallowed test command in a CI/build file: `npm test || true`, `pytest || exit 0`,
#     gradle `ignoreFailures = true`, maven `testFailureIgnore`.
# WARN (a declared deferral or a possibly-legit escape hatch - review, don't necessarily block):
#   - it.todo/test.todo, markTestIncomplete, a testing.Short() guard (Go);
#   - `continue-on-error: true` / `allow_failure: true` on a CI step (line-based scan can't prove it wraps
#     a test step); `--passWithNoTests` (legit in per-file hooks, laundering in a full-suite run).
# Suppress a finding with an inline `no-skips: allow <reason>` comment on the line, or a path/substring
# entry in `.grillspec/no-skips-allow.txt`. `--strict` promotes WARN -> ERROR.
#
# Test files are found via the shared tier_contract classifier (tests/ trees AND co-located *.test.* files);
# CI/build files are the same deploy-intent set check_deploy_real.py watches, plus Makefile/package.json/
# gradle/pom. LIMITATION (by design): config-level suite exclusions (jest testPathIgnorePatterns, vitest
# exclude) are not scanned - defaults there are legitimate and noisy; the conformance review owns that case.
#
# No-ops cleanly when there is no test tree yet. Run from the project root:
#   python3 tools/check_no_skips.py [project_root] [--tests <roots>] [--strict]
import sys, re, pathlib
from tier_contract import iter_test_files, PRUNE, DEFAULT_ROOTS

args = [a for a in sys.argv[1:] if not a.startswith("--")]
ROOT = pathlib.Path(args[0] if args else ".")
STRICT = "--strict" in sys.argv
def opt(flag, default):
    for i, a in enumerate(sys.argv):
        if a == flag and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default
TEST_DIRS = [s for s in opt("--tests", DEFAULT_ROOTS).split(",") if s]

# -- test-file markers. The x/f function forms use (?<![.\w]) so a method CALL never matches: model.fit(X)
# -- and points.xit( are library calls, not Jasmine focus/skip markers.
SKIP_MEMBER = re.compile(r"\b(?:it|test|describe|context|suite)\s*\.\s*(?:skip|fixme|failing)\s*\(")
X_FUNC = re.compile(r"(?<![.\w])x(?:it|test|describe|context|specify)\s*\(")
ONLY = re.compile(r"\b(?:it|test|describe|context|suite)\s*\.\s*only\s*\(|(?<![.\w])f(?:it|describe|context)\s*\(")
THIS_SKIP = re.compile(r"\bthis\.skip\s*\(")
PY_SKIP = re.compile(r"pytest\.mark\.(?:skip|skipif|xfail)|\bpytest\.(?:skip|xfail|importorskip)\s*\(|"
                     r"@unittest\.skip|@skip(?:If|Unless)?\s*\(|\bskipTest\s*\(")
GO_SKIP = re.compile(r"\b[tb]\.Skip(?:f|Now)?\s*\(")
RUST_IGNORE = re.compile(r"#\[\s*ignore")
JVM_DISABLED = re.compile(r"@(?:Disabled|Ignore)\b")
CS_SKIP = re.compile(r"\[\s*Ignore\s*[\]\(]|\bSkip\s*=\s*\"")
PHP_SKIP = re.compile(r"->markTestSkipped\s*\(")
RB_SKIP = re.compile(r"^\s*(?:skip|pending)\b(?!\s*[:=(]?\s*=)")   # .rb only: a bare skip/pending statement
TODO_MEMBER = re.compile(r"\b(?:it|test)\s*\.\s*todo\s*\(")
PHP_INCOMPLETE = re.compile(r"->markTestIncomplete\s*\(")
GO_SHORT = re.compile(r"\btesting\.Short\s*\(")

# -- CI/build laundering. ERROR only when the swallow is on the SAME line as a recognized test command -
# -- that single-line pairing is the high-precision signal; a bare `|| true` elsewhere may be legitimate.
TEST_CMD = re.compile(r"\b(?:npm\s+(?:run\s+)?test|yarn\s+(?:run\s+)?test|pnpm\s+(?:run\s+)?test|pytest|"
                      r"python3?\s+-m\s+pytest|go\s+test|cargo\s+test|mvn\b[^|]*\btest|gradlew?\b[^|]*\btest|"
                      r"jest|vitest|mocha|jasmine|rspec|phpunit|dotnet\s+test|ctest|tox|nox)\b", re.I)
SWALLOW = re.compile(r"\|\|\s*(?:true|exit\s+0|:)(?:\s|$|\")")
BUILD_IGNORE = re.compile(r"\bignoreFailures\s*=?\s*true|testFailureIgnore\W*true|maven\.test\.failure\.ignore\W*true", re.I)
CI_SOFT = re.compile(r"\bcontinue-on-error:\s*true|\ballow_failure:\s*true", re.I)
PASS_EMPTY = re.compile(r"--pass-?[Ww]ith-?[Nn]o-?[Tt]ests")
CI_FILE = re.compile(
    r"(?:^|/)(?:\.github/workflows/[^/]+\.ya?ml|\.gitlab-ci\.yml|\.circleci/config\.yml|"
    r"azure-pipelines\.ya?ml|bitbucket-pipelines\.yml|\.drone\.yml|cloudbuild\.ya?ml|Jenkinsfile[^/]*|"
    r"[Mm]akefile|package\.json|[^/]+\.gradle(?:\.kts)?|pom\.xml)$")

allow = []
allowf = ROOT / ".grillspec" / "no-skips-allow.txt"
if allowf.exists():
    for ln in allowf.read_text(encoding="utf-8", errors="replace").splitlines():
        ln = ln.split("#", 1)[0].strip()
        if ln:
            allow.append(ln)

def allowed(where, msg):
    return any(a in where or a in msg for a in allow)

F = []
def add(sev, where, msg):
    if sev == "WARN" and STRICT:
        sev = "ERROR"
    if not allowed(where, msg):
        F.append((sev, where, msg))

UNSKIP = "un-skip it; an unready dependency must FAIL the test - red is the truthful signal, never a skip."

tested = 0
for posix, name, p in iter_test_files(ROOT, TEST_DIRS):
    tested += 1
    rel = p.relative_to(ROOT).as_posix()
    for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if "no-skips: allow" in line:
            continue
        where = "%s:%d" % (rel, n)
        if SKIP_MEMBER.search(line) or X_FUNC.search(line) or THIS_SKIP.search(line):
            add("ERROR", where, "a skipped/disabled test reads green while asserting nothing - " + UNSKIP)
        elif PY_SKIP.search(line):
            add("ERROR", where, "a skip/skipif/xfail marker launders a red into a pass - " + UNSKIP)
        elif p.suffix == ".go" and GO_SKIP.search(line):
            add("ERROR", where, "t.Skip disables this test at run time - " + UNSKIP)
        elif p.suffix == ".rs" and RUST_IGNORE.search(line):
            add("ERROR", where, "#[ignore] disables this test - " + UNSKIP)
        elif p.suffix in (".java", ".kt", ".scala") and JVM_DISABLED.search(line):
            add("ERROR", where, "@Disabled/@Ignore disables this test - " + UNSKIP)
        elif p.suffix == ".cs" and CS_SKIP.search(line):
            add("ERROR", where, "an Ignore/Skip attribute disables this test - " + UNSKIP)
        elif p.suffix == ".php" and PHP_SKIP.search(line):
            add("ERROR", where, "markTestSkipped disables this test - " + UNSKIP)
        elif p.suffix == ".rb" and RB_SKIP.search(line):
            add("ERROR", where, "a skip/pending statement disables this test - " + UNSKIP)
        if ONLY.search(line):
            add("ERROR", where, "a .only/fit/fdescribe focus marker silently shrinks the suite to this case - remove it before committing.")
        if TODO_MEMBER.search(line):
            add("WARN", where, "a declared-but-unwritten test (todo) defers the red - write the failing test instead.")
        if p.suffix == ".php" and PHP_INCOMPLETE.search(line):
            add("WARN", where, "markTestIncomplete defers the red - write the failing test instead.")
        if p.suffix == ".go" and GO_SHORT.search(line):
            add("WARN", where, "a testing.Short() guard conditionally skips - make sure CI runs the full (non-short) suite.")

ci = 0
for p in sorted(ROOT.rglob("*")):
    if not p.is_file():
        continue
    posix = "/" + p.as_posix().strip("/")
    if PRUNE.search(posix) or not CI_FILE.search(posix):
        continue
    ci += 1
    rel = p.relative_to(ROOT).as_posix()
    for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if "no-skips: allow" in line:
            continue
        where = "%s:%d" % (rel, n)
        if TEST_CMD.search(line) and SWALLOW.search(line):
            add("ERROR", where, "the test command swallows its failure (|| true / exit 0) - a red suite must fail this step.")
        if BUILD_IGNORE.search(line):
            add("ERROR", where, "test failures are configured to be ignored - a red suite must fail the build.")
        if CI_SOFT.search(line):
            add("WARN", where, "continue-on-error/allow_failure on a CI step - if it wraps a test/gate step, a red run is being swallowed.")
        if PASS_EMPTY.search(line):
            add("WARN", where, "--passWithNoTests turns 'no tests ran' into a pass - fine in a per-file hook, laundering in a full-suite run.")

if tested == 0 and ci == 0:
    print("check_no_skips: no test files or CI/build files under %s - nothing to scan." % ROOT)
    sys.exit(0)

order = {"ERROR": 0, "WARN": 1}
for sev, where, msg in sorted(F, key=lambda x: (order[x[0]], x[1])):
    print("%-5s %-32s %s" % (sev, where, msg))
e = sum(1 for x in F if x[0] == "ERROR")
w = len(F) - e
print("\n%d error(s), %d warning(s) over %d test file(s) + %d ci/build file(s)." % (e, w, tested, ci))
sys.exit(1 if e else 0)
