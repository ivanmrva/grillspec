#!/usr/bin/env python3
# test_check_operate_records.py - regression tests for check_operate_records.py (12-operate reconciliation).
# Stdlib only; no network. Run:  python3 tools/test_check_operate_records.py
import subprocess, sys, tempfile, shutil, pathlib

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE / "check_operate_records.py"

# a minimal spec: one task, one DATA-, an infra-ops environments file declaring dev+prod.
SPEC = {
    "spec/10-delivery/tasks/T-001.md": "T-001 | Charge an order\n",
    "spec/04-domain/ddd/data.md": "DATA-Order — the order aggregate.\n",
    "spec/09-solution/infra-ops/environments.md":
        "| Key | dev | prod |\n|---|---|---|\n| DATABASE_URL | local | live |\n",
}

def run(files):
    d = pathlib.Path(tempfile.mkdtemp(prefix="operate_"))
    try:
        base = dict(SPEC); base.update(files)
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

# a deploy record naming a real T- to a declared env is clean
expect("deploy-clean", run({"spec/12-operate/deploy-dev-1.0.0.md": "Deployed T-001 to dev.\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# a deploy record referencing a T- that doesn't exist -> ERROR (dangling)
expect("deploy-dangling-task", run({"spec/12-operate/deploy-dev-1.0.0.md": "Deployed T-999 to dev.\n"}),
       must=["ERROR", "T-999", "resolves nowhere"])

# a deploy to an env not declared in infra-ops -> ERROR (off the promotion path)
expect("deploy-unknown-env", run({"spec/12-operate/deploy-qa-1.0.0.md": "Deployed T-001 to qa.\n"}),
       must=["ERROR", "qa", "not a declared environment"])

# a deploy record naming no T- -> WARN (no trace)
expect("deploy-no-task-warn", run({"spec/12-operate/deploy-dev-1.0.0.md": "Deployed something to dev.\n"}),
       must=["WARN", "names no T-"])

# a migration record citing a real DATA- is clean
expect("migration-clean", run({"spec/12-operate/migration-001-orders.md": "Enacted DATA-Order change.\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# a migration citing no DATA- -> WARN
expect("migration-no-data-warn", run({"spec/12-operate/migration-001-orders.md": "Ran a migration.\n"}),
       must=["WARN", "cites no DATA-"])

# an incident referencing a dangling NFR- -> ERROR
expect("incident-dangling-nfr", run({"spec/12-operate/incident-42.md": "Breached NFR-Latency.\n"}),
       must=["ERROR", "NFR-Latency", "resolves nowhere"])

# an incident/diagnosis record with no learnings/propagation line -> WARN (unclosed postmortem loop)
expect("incident-no-learnings-warn", run({
    "spec/06-requirements/quality/q.md": "| ID | attr |\n|---|---|\n| NFR-Lat | latency |\n",
    "spec/12-operate/incident-42.md": "Breached NFR-Lat. Mitigated by restart.\n"}),
       must=["WARN", "no learnings/propagation line"])
# ...and one that routes a learning is clean
expect("incident-learnings-ok", run({
    "spec/06-requirements/quality/q.md": "| ID | attr |\n|---|---|\n| NFR-Lat | latency |\n",
    "spec/12-operate/incident-42.md": "Breached NFR-Lat.\nlearning: retry storm on cold cache — gap raised to quality (assumption added).\n"}),
       forbid=["no learnings/propagation line"])
# a deploy record is NOT held to the learnings line (it's an incident/diagnosis obligation)
expect("deploy-not-held-to-learnings", run({
    "spec/06-requirements/quality/q.md": "| id | x |\n|---|---|\n| T-001 | t |\n",
    "spec/09-solution/infra-ops/environments.md": "dev environment\n",
    "spec/12-operate/deploy-dev-1.0.0.md": "Shipped T-001 to dev.\n"}),
       forbid=["no learnings/propagation line"])

# no 12-operate ledger = clean no-op
expect("no-ledger-noop", run({}), must=["nothing to reconcile"], forbid=["ERROR", "Traceback"])

print("\n%d passed, %d failed" % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
