#!/usr/bin/env python3
# test_check_test_tiers.py - regression tests for check_test_tiers.py (declared-tier-vs-actual-suite).
# Stdlib only; no network. Run:  python3 tools/test_check_test_tiers.py
import subprocess, sys, tempfile, shutil, pathlib

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE / "check_test_tiers.py"

CONTRACT = (
    "# levels\n\n## Tier contract\n"
    "| tier | real-deps | may-mock | mock-ceiling | target-env | coverage-bar | mutation-bar |\n"
    "|---|---|---|---|---|---|---|\n"
    "| unit | none | — | none | local | 80% | 70% |\n"
    "| integration | db | third-party-network | boundary-only | local | 70% | — |\n"
    "| e2e | all | — | none | preview | — | — |\n"
)
LEVELS = "spec/09-solution/test/levels.md"

def run(files, args=(), contract=CONTRACT):
    d = pathlib.Path(tempfile.mkdtemp(prefix="testtiers_"))
    try:
        base = {} if contract is None else {LEVELS: contract}
        base.update(files)
        for rel, content in base.items():
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

FULL = {
    "tests/unit/a.py": "def test_a(): pass\n",
    "tests/integration/b.py": "def test_b(): pass\n",
    "tests/e2e/c.py": "def test_c(): pass\n",
}

# every declared tier has a suite -> clean
expect("all-tiers-present", run(FULL), must=["0 error(s)"], forbid=["ERROR"])

# a declared tier with no suite -> ERROR
expect("missing-tier", run({"tests/unit/a.py": "def test_a(): pass\n", "tests/e2e/c.py": "def test_c(): pass\n"}),
       must=["ERROR", "integration", "never built"])

# a dir whose segment isn't a recognized tier is simply not counted (no warn, no error)
d2 = dict(FULL); d2["tests/perf/z.py"] = "def test_z(): pass\n"
expect("unrecognized-dir-ignored", run(d2), must=["0 error(s)"], forbid=["ERROR"])
# a recognized tier segment not in the contract DOES warn: add 'contract' tier tests but contract omits it
d3 = dict(FULL); d3["tests/contract/z.py"] = "def test_z(): pass\n"
expect("recognized-undeclared-warn", run(d3), must=["WARN", "contract", "never declares"])

# distribution counts are printed
expect("prints-distribution", run(FULL), must=["tier distribution", "unit=1", "integration=1", "e2e=1"])

# no contract = no-op (default)
expect("no-contract-noop", run({"tests/unit/a.py": "def test(): pass\n"}, contract=None),
       must=["no tier contract"], forbid=["ERROR"])

# no contract but a test tree exists, under --require = ERROR (the strategy was never derived)
expect("require-missing-contract-error", run({"tests/unit/a.py": "def test(): pass\n"}, args=("--require",), contract=None),
       must=["ERROR", "NO tier contract", "never derived"])

# --require with NO test tree at all is still a no-op (nothing built yet)
expect("require-no-tests-noop", run({}, args=("--require",), contract=None),
       must=["no tier contract"], forbid=["ERROR"])

# tiers detected from the FILENAME (co-located / named-by-tier), not just the directory
expect("filename-tier-detection", run({
        "tests/charge.unit.test.js": "it('a', () => {});\n",
        "tests/charge.integration.test.js": "it('b', () => {});\n",
        "tests/charge.e2e.test.js": "it('c', () => {});\n",
    }), must=["0 error(s)"], forbid=["ERROR"])

# most files untier-able -> a blindness WARN (the gate can't see them)
expect("blindness-warn", run({
        "tests/e2e/c.py": "def test_c(): pass\n",
        "tests/integration/b.py": "def test_b(): pass\n",   # cover integration so the only ERROR is 'unit missing'...
        "tests/unit/a.py": "def test_a(): pass\n",
        "tests/helpers/x.py": "def h(): pass\n",
        "tests/helpers/y.py": "def h(): pass\n",
        "tests/helpers/z.py": "def h(): pass\n",
    }), must=["WARN", "blind"])

print("\n%d passed, %d failed" % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
