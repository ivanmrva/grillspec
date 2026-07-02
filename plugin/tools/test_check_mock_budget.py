#!/usr/bin/env python3
# test_check_mock_budget.py - regression tests for check_mock_budget.py (the over-mocking tripwire).
#
# Each scenario writes a tiny project (a tier contract + a test tree), runs the tool, and asserts which findings
# fire (must=) and which do NOT (forbid=) - locking the precision so a later edit can't make it noisier or blind.
# Stdlib only; no network. Run:  python3 tools/test_check_mock_budget.py
import subprocess, sys, tempfile, shutil, pathlib

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE / "check_mock_budget.py"

CONTRACT = (
    "# levels\n\n## Tier contract\n"
    "| tier | real-deps | may-mock | mock-ceiling | target-env | coverage-bar | mutation-bar |\n"
    "|---|---|---|---|---|---|---|\n"
    "| unit | none | — | none | local | 80% | 70% |\n"
    "| integration | db,broker | third-party-network | boundary-only | local | 70% | — |\n"
    "| contract | provider,consumer | — | none | local | — | — |\n"
    "| e2e | all | — | none | preview | — | — |\n"
)
LEVELS = "spec/09-solution/test/levels.md"

def run(files, args=()):
    d = pathlib.Path(tempfile.mkdtemp(prefix="mockbudget_"))
    try:
        base = {LEVELS: CONTRACT}
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

# a unit test with no mocks is clean
expect("unit-clean", run({"tests/unit/a.py": "def test_add():\n    assert 1 + 1 == 2\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# CONV-047: a hand-built double injected through the production constructor is ALLOWED at a 'none' tier
expect("unit-injected-double-ok", run({"tests/unit/checkout.test.ts":
        "const billing = { create: vi.fn() };\nconst svc = makeCreateCheckoutSession(billing);\n"}),
       must=["0 error(s)"], forbid=["ERROR"])
expect("unit-magicmock-inject-ok", run({"tests/unit/svc_test.py":
        "from unittest.mock import MagicMock\ndef test_x():\n    svc = Service(MagicMock())\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# ...but MODULE-level mocking (swaps a real import behind the code's back) is still an ERROR at 'none'
expect("unit-module-mock-error", run({"tests/unit/a.ts": "vi.mock('../billing');\nit('x', () => {});\n"}),
       must=["ERROR", "MODULE-level"])
expect("unit-patch-error", run({"tests/unit/a.py": "from unittest.mock import patch\n@patch('app.clock')\ndef test_x():\n    pass\n"}),
       must=["ERROR", "MODULE-level"])

# an e2e test that module-mocks is the same ERROR (an e2e that swaps imports isn't e2e)
expect("e2e-module-mock-error", run({"tests/e2e/a.js": "jest.mock('../db');\nit('x', () => {});\n"}),
       must=["ERROR", "e2e"])

# integration MAY mock a third-party boundary
expect("integration-boundary-ok", run({"tests/integration/a.js": "jest.mock('stripe');\nit('x', () => {});\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# ...but integration must NOT mock a real dependency (the DB) -> ERROR (module-level OR a hand-built db fake)
expect("integration-mocks-db-error", run({"tests/integration/a.py": "from unittest.mock import patch\n@patch('app.db')\ndef test_x():\n    pass\n"}),
       must=["ERROR", "boundary-only", "real dependency"])
expect("integration-vifn-db-error", run({"tests/integration/a.ts": "const db = { save: vi.fn() };\nuse(db);\n"}),
       must=["ERROR", "real dependency"])

# inline waiver suppresses a module-mock
expect("inline-waiver", run({"tests/unit/a.ts": "vi.mock('../x'); // mock-budget: allow legacy shim\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# allowlist file suppresses by path
expect("allowlist-file", run({"tests/unit/a.ts": "vi.mock('../x');\n", ".claude/mock-budget-allow.txt": "tests/unit/a.ts\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# no contract at all = clean no-op
d = pathlib.Path(tempfile.mkdtemp(prefix="mockbudget_"))
try:
    (d / "tests/unit").mkdir(parents=True)
    (d / "tests/unit/a.py").write_text("from unittest.mock import Mock\n")
    o = subprocess.run([sys.executable, str(TOOL), str(d)], capture_output=True, text=True)
    out = o.stdout + o.stderr
    expect("no-contract-noop", out, must=["no tier contract"], forbid=["ERROR", "Traceback"])
finally:
    shutil.rmtree(d, ignore_errors=True)

# no test tree = clean no-op
expect("no-tests-noop", run({"docs/x.md": "hi\n"}),
       must=["nothing to scan"], forbid=["ERROR", "Traceback"])

print("\n%d passed, %d failed" % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
