#!/usr/bin/env python3
# test_check_e2e_target.py - regression tests for check_e2e_target.py (e2e-against-a-local-stack tripwire).
# Stdlib only; no network. Run:  python3 tools/test_check_e2e_target.py
import subprocess, sys, tempfile, shutil, pathlib

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE / "check_e2e_target.py"

CONTRACT = (
    "# levels\n\n## Tier contract\n"
    "| tier | real-deps | may-mock | mock-ceiling | target-env | coverage-bar | mutation-bar |\n"
    "|---|---|---|---|---|---|---|\n"
    "| unit | none | — | none | local | 80% | 70% |\n"
    "| integration | db | third-party-network | boundary-only | local | 70% | — |\n"
    "| e2e | all | — | none | preview | — | — |\n"
)
LEVELS = "spec/09-solution/test/levels.md"

def run(files):
    d = pathlib.Path(tempfile.mkdtemp(prefix="e2etarget_"))
    try:
        base = {LEVELS: CONTRACT}
        base.update(files)
        for rel, content in base.items():
            p = d / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding="utf-8")
        out = subprocess.run([sys.executable, str(TOOL), str(d)], capture_output=True, text=True)
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

# an e2e test that reads its target from env is clean
expect("e2e-uses-env-ok", run({"tests/e2e/a.js": "const url = process.env.E2E_BASE_URL;\nit('x', () => {});\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# an e2e test hardcoding localhost -> ERROR (integration mislabelled)
expect("e2e-localhost-error", run({"tests/e2e/a.js": "const url = 'http://localhost:3000';\nit('x', () => {});\n"}),
       must=["ERROR", "e2e", "local stack"])

# an e2e test spinning up testcontainers/docker-compose -> ERROR
expect("e2e-testcontainers-error", run({"tests/e2e/b.py": "from testcontainers.postgres import PostgresContainer\n"}),
       must=["ERROR", "local stack"])

# the SAME localhost in an INTEGRATION test (target-env local) is fine - not this tool's tier
expect("integration-localhost-ok", run({"tests/integration/a.js": "const url = 'http://localhost:5432';\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# inline waiver suppresses
expect("inline-waiver", run({"tests/e2e/a.js": "const url = 'http://localhost:3000'; // e2e-target: allow local pre-check\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# no real-env tier declared = no-op
CONTRACT_LOCAL = CONTRACT.replace("| preview |", "| local |")
d = pathlib.Path(tempfile.mkdtemp(prefix="e2etarget_"))
try:
    (d / "spec/09-solution/test").mkdir(parents=True); (d / LEVELS).write_text(CONTRACT_LOCAL)
    (d / "tests/e2e").mkdir(parents=True); (d / "tests/e2e/a.js").write_text("const u='http://localhost';\n")
    o = subprocess.run([sys.executable, str(TOOL), str(d)], capture_output=True, text=True)
    expect("no-realenv-tier-noop", o.stdout + o.stderr, must=["no real-deployed-env tier"], forbid=["ERROR"])
finally:
    shutil.rmtree(d, ignore_errors=True)

# co-located: an e2e/*.e2e.test.ts (classifies as e2e) hardcoding localhost is caught
expect("co-located-e2e-localhost", run({"e2e/checkout.e2e.test.ts": "const u = 'http://localhost:3000';\n"}),
       must=["ERROR", "local stack"])

# no contract = no-op
expect("no-contract-noop",
       (lambda: subprocess.run([sys.executable, str(TOOL), str(pathlib.Path(tempfile.mkdtemp(prefix="e2etarget_")))], capture_output=True, text=True))().stdout,
       must=["no tier contract"], forbid=["ERROR"])

print("\n%d passed, %d failed" % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
