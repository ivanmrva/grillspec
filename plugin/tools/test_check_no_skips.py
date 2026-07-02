#!/usr/bin/env python3
# test_check_no_skips.py - regression tests for check_no_skips.py (the disabled/weakened-test tripwire).
#
# Each scenario writes a tiny project, runs the tool, asserts which findings fire (must=) and which do NOT
# (forbid=) - locking the precision so a later edit can't make it noisier or blind. Stdlib only; no network.
# Run:  python3 tools/test_check_no_skips.py
import subprocess, sys, tempfile, shutil, pathlib

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE / "check_no_skips.py"

def run(files, args=()):
    d = pathlib.Path(tempfile.mkdtemp(prefix="noskiptest_"))
    try:
        for rel, content in files.items():
            p = d / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding="utf-8")
        out = subprocess.run([sys.executable, str(TOOL), str(d), *args], capture_output=True, text=True)
        return out.stdout + out.stderr
    finally:
        shutil.rmtree(d, ignore_errors=True)

PASS = FAIL = 0
def expect(name, output, must=(), forbid=()):
    global PASS, FAIL
    probs = [("missing: " + s) for s in must if s not in output] + \
            [("unexpected: " + s) for s in forbid if s in output]
    if probs:
        FAIL += 1; print("FAIL  " + name)
        for pr in probs: print("        " + pr)
        print("        --- output ---\n" + "\n".join("        " + l for l in output.splitlines()))
    else:
        PASS += 1; print("ok    " + name)

CLEAN_JS = "describe('pay', () => {\n  it('charges the card', () => { expect(pay(1)).toBe(true) })\n})\n"

# a clean suite is clean
expect("clean-suite", run({"tests/pay.test.js": CLEAN_JS}), must=["0 error(s)"], forbid=["ERROR"])

# -- JS/TS skip + focus markers -------------------------------------------------------------------------
expect("it-skip", run({"tests/pay.test.js": "it.skip('charges', () => {})\n"}),
       must=["ERROR", "skipped/disabled test"])
expect("describe-skip", run({"tests/pay.test.ts": "describe.skip('pay', () => {})\n"}),
       must=["ERROR"])
expect("xit", run({"tests/pay.test.js": "xit('charges', () => {})\n"}),
       must=["ERROR"])
expect("mocha-this-skip", run({"tests/pay.test.js": "if (!env.ready) this.skip()\n"}),
       must=["ERROR"])
expect("only-shrinks-suite", run({"tests/pay.test.js": "it.only('charges', () => {})\n"}),
       must=["ERROR", "shrinks the suite"])
expect("fdescribe", run({"tests/pay.test.js": "fdescribe('pay', () => {})\n"}),
       must=["ERROR", "shrinks the suite"])
# a method CALL named .fit()/.xit() is NOT a focus/skip marker (curve-fitting, chess libs, ...)
expect("dot-fit-call-ok", run({"tests/model.test.py": "def test_m():\n    model.fit(X)\n    points.xit(3)\n"}),
       must=["0 error(s)"], forbid=["ERROR"])
expect("test-todo-warns", run({"tests/pay.test.js": "it.todo('handles refunds')\n"}),
       must=["WARN", "todo"], forbid=["ERROR"])

# -- Python markers -------------------------------------------------------------------------------------
expect("pytest-mark-skip", run({"tests/test_pay.py": "@pytest.mark.skip(reason='env not ready')\ndef test_pay(): ...\n"}),
       must=["ERROR", "launders"])
expect("pytest-skipif", run({"tests/test_pay.py": "@pytest.mark.skipif(no_db, reason='no db yet')\ndef test_pay(): ...\n"}),
       must=["ERROR"])
expect("pytest-xfail", run({"tests/test_pay.py": "@pytest.mark.xfail\ndef test_pay(): ...\n"}),
       must=["ERROR"])
expect("pytest-importorskip", run({"tests/test_pay.py": "stripe = pytest.importorskip('stripe')\n"}),
       must=["ERROR"])
expect("unittest-skiptest", run({"tests/test_pay.py": "def test_x(self):\n    self.skipTest('later')\n"}),
       must=["ERROR"])

# -- other languages ------------------------------------------------------------------------------------
expect("go-t-skip", run({"tests/pay_test.go": "func TestPay(t *testing.T) {\n  t.Skip(\"broker not ready\")\n}\n"}),
       must=["ERROR", "t.Skip"])
expect("go-short-warns", run({"tests/pay_test.go": "func TestPay(t *testing.T) {\n  if testing.Short() { return }\n}\n"}),
       must=["WARN"], forbid=["ERROR"])
expect("rust-ignore", run({"tests/pay_test.rs": "#[ignore]\nfn pays() {}\n"}),
       must=["ERROR", "#[ignore]"])
expect("junit-disabled", run({"tests/PayTest.java": "@Disabled(\"flaky\")\nvoid pays() {}\n"}),
       must=["ERROR"])
expect("xunit-skip-attr", run({"tests/PayTests.cs": "[Fact(Skip = \"env missing\")]\npublic void Pays() {}\n"}),
       must=["ERROR"])
expect("php-marktestskipped", run({"tests/PayTest.php": "$this->markTestSkipped('no gateway');\n"}),
       must=["ERROR"])
expect("ruby-skip-stmt", run({"tests/pay_spec.rb": "it 'pays' do\n  skip 'gateway not wired'\nend\n"}),
       must=["ERROR"])
expect("ruby-skip-assign-ok", run({"tests/pay_spec.rb": "it 'pays' do\n  skip = compute()\n  expect(skip).to eq 1\nend\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# -- co-located test files are scanned; production files are not -----------------------------------------
expect("colocated-test-scanned", run({"src/pay.test.ts": "it.skip('charges', () => {})\n"}),
       must=["ERROR"])
expect("production-not-scanned", run({"src/pay.ts": "export const skip = (job) => queue.skip(job)\n",
                                      "tests/pay.test.js": CLEAN_JS}),
       must=["0 error(s)"], forbid=["ERROR"])

# -- CI/build laundering ----------------------------------------------------------------------------------
expect("ci-test-or-true", run({".github/workflows/ci.yml": "      - run: npm test || true\n"}),
       must=["ERROR", "swallows its failure"])
expect("ci-pytest-exit0", run({".gitlab-ci.yml": "script:\n  - pytest || exit 0\n"}),
       must=["ERROR"])
expect("gradle-ignorefailures", run({"build.gradle": "test {\n    ignoreFailures = true\n}\n"}),
       must=["ERROR", "configured to be ignored"])
expect("ci-continue-on-error-warns", run({".github/workflows/ci.yml": "      continue-on-error: true\n"}),
       must=["WARN"], forbid=["ERROR"])
expect("passwithnotests-warns", run({"package.json": '{"scripts": {"test": "jest --passWithNoTests"}}\n'}),
       must=["WARN"], forbid=["ERROR"])
expect("ci-deploy-or-true-ok", run({".github/workflows/ci.yml": "      - run: notify-slack || true\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# -- waivers + strict -------------------------------------------------------------------------------------
expect("inline-waiver", run({"tests/pay.test.js": "it.skip('quarantined', () => {}) // no-skips: allow flake FLK-3\n"}),
       must=["0 error(s)"], forbid=["ERROR"])
expect("allowlist-file", run({"tests/pay.test.js": "it.skip('charges', () => {})\n",
                              ".claude/no-skips-allow.txt": "tests/pay.test.js\n"}),
       must=["0 error(s)"], forbid=["ERROR"])
expect("strict-promotes", run({"tests/pay.test.js": "it.todo('handles refunds')\n"}, args=("--strict",)),
       must=["ERROR"])

# -- empty project = clean no-op --------------------------------------------------------------------------
expect("no-tests-noop", run({"docs/readme.md": "hello\n"}),
       must=["nothing to scan"], forbid=["ERROR", "Traceback"])

print("\n%d passed, %d failed" % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
