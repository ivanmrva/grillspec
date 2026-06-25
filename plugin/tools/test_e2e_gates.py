#!/usr/bin/env python3
# test_e2e_gates.py - end-to-end integration test for the accountability + ops gates as a CHAIN.
#
# The per-tool suites (test_check_task_record / test_check_no_fakes / test_check_config_drift /
# test_check_deploy_real / test_check_migration_real) lock each tool's behaviour in isolation. THIS proves they
# compose on one realistic mini-project: a properly-done task (real code, no fakes, declared config, a real
# deploy, a real migration, a backed Verification Record) passes ALL FIVE gates, and each distinct kind of cheat
# trips exactly the gate that owns it. Stdlib only; no network. Run: python3 tools/test_e2e_gates.py
import subprocess, sys, tempfile, shutil, pathlib

HERE = pathlib.Path(__file__).resolve().parent
REC  = HERE / "check_task_record.py"
FAKE = HERE / "check_no_fakes.py"
DRIFT = HERE / "check_config_drift.py"
DEPLOY = HERE / "check_deploy_real.py"
MIG  = HERE / "check_migration_real.py"

def project(d):
    """A clean, fully-backed mini-project: one done task, real code, declared config, @covers-tagged tests."""
    f = {
        # the task + its frozen obligations
        "spec/10-delivery/tasks/T-001.md":
            "T-001 | phase: MVP | Charge an order\n"
            "behavior:    UC-001 · AC-001a\n"
            "api:         API-Charge\n"
            "security:    SEC-1\n",
        # the env matrix (the declared config side)
        "spec/09-solution/infra-ops/environments.md":
            "<!-- scope: x | excludes: y | format: matrix -->\n"
            "| Key | Purpose | dev | prod |\n|---|---|---|---|\n"
            "| DATABASE_URL | store | local | distinct |\n| STRIPE_API_KEY | pay | test | live |\n",
        # the independent conformance verdict
        "spec/10-delivery/verification/review-report.md":
            "# review-report\nReviewed T-001 independently.\nVERDICT: PASS — T-001 conforms.\n",
        # the traceability matrix
        "spec/10-delivery/verification/traceability.md":
            "| spec ID | T- | code | test | pass |\n|---|---|---|---|---|\n"
            "| AC-001a | T-001 | src/charge.js | tests/e2e/charge.test.js | ✓ |\n"
            "| API-Charge | T-001 | src/charge.js | tests/contract/charge.json | ✓ |\n",
        # the backed Verification Record (status: done)
        "spec/10-delivery/verification/tasks/T-001.md":
            "status: done\ntask: T-001\nheld-out: AC-001a\n"
            "| Obligation | Source | Required | Evidence | Status |\n|---|---|---|---|---|\n"
            "| UC-001 | behavior | test | tests/e2e/charge.test.js | PASS |\n"
            "| AC-001a | behavior | test | tests/e2e/charge.test.js | PASS |\n"
            "| API-Charge | api | contract | tests/contract/charge.json | PASS |\n"
            "| SEC-1 | security | enforced | tests/e2e/charge.test.js | PASS |\n"
            "| tests-first | done-gate | trace | tests/e2e/charge.test.js | PASS |\n"
            "| tests:layers | test-strategy | levels | tests/e2e/charge.test.js · tests/contract/charge.json | PASS |\n"
            "| coverage | test-strategy | >= bar | 86% (bar 80%) | PASS |\n"
            "| mutation | test-strategy | >= bar | N/A — no domain-logic change | N/A |\n"
            "| fitness:no-fakes | done-gate | clean | check_no_fakes clean | PASS |\n"
            "| fitness:architecture | done-gate | green | fitness green | PASS |\n"
            "| spec-lint | done-gate | clean | lint clean | PASS |\n"
            "| deploy | infra-ops | real | .github/workflows/deploy.yml | PASS |\n"
            "| traceability | done-gate | updated | traceability.md | PASS |\n"
            "| conformance | review | verdict | review-report.md | PASS |\n",
        # real production code: reads only DECLARED config, no test doubles
        "src/charge.js":
            "const db = process.env.DATABASE_URL;\n"
            "const key = process.env.STRIPE_API_KEY;\n"
            "export function charge(order){ return db.save(order); }\n",
        # the test tree carries the @covers tag (AC id literally present)
        "tests/e2e/charge.test.js": "// @covers AC-001a\nit('charges', () => {});\n",
        "tests/contract/charge.json": "{}\n",
        # a REAL deploy workflow (invokes a recognized deploy command) - the deploy gate's clean side
        ".github/workflows/deploy.yml":
            "name: deploy\non: { push: { branches: [main] } }\n"
            "jobs:\n  deploy:\n    runs-on: ubuntu-latest\n"
            "    steps:\n      - run: helm upgrade --install app ./chart\n",
        # a REAL migration (has DDL) - the migration gate's clean side
        "migrations/001_orders.sql": "CREATE TABLE orders (id serial primary key, total numeric);\n",
    }
    for rel, content in f.items():
        p = d / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding="utf-8")

def run(tool, args):
    return subprocess.run([sys.executable, str(tool), *args], capture_output=True, text=True)

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1; print("ok    " + name)
    else: FAIL += 1; print("FAIL  " + name + ("\n        " + detail if detail else ""))

def fresh(mutate=None):
    d = pathlib.Path(tempfile.mkdtemp(prefix="e2e_"))
    project(d)
    if mutate: mutate(d)
    return d

# ── 1. the clean project passes ALL FOUR gates ─────────────────────────────
d = fresh()
try:
    r1 = run(REC,   [str(d / "spec"), "--task", "T-001"])
    r2 = run(FAKE,  [str(d)])
    r3 = run(DRIFT, [str(d)])
    r4 = run(DEPLOY, [str(d)])
    r5 = run(MIG,   [str(d)])
    check("clean: task-record passes",  r1.returncode == 0, r1.stdout + r1.stderr)
    check("clean: no-fakes passes",     r2.returncode == 0, r2.stdout + r2.stderr)
    check("clean: config-drift passes", r3.returncode == 0, r3.stdout + r3.stderr)
    check("clean: deploy-real passes",  r4.returncode == 0, r4.stdout + r4.stderr)
    check("clean: migration-real passes", r5.returncode == 0, r5.stdout + r5.stderr)
    rr = run(REC, [str(d / "spec"), "--report", "T-001"])
    check("clean: report says VERIFIED", "VERIFIED" in rr.stdout and rr.returncode == 0, rr.stdout)
finally:
    shutil.rmtree(d, ignore_errors=True)

# ── 2. a fake in production trips no-fakes ONLY ─────────────────────────────
def add_fake(d): (d / "src" / "fake_repo.js").write_text("export class FakeRepo { save(){ return true; } }\n")
d = fresh(add_fake)
try:
    check("fake: no-fakes catches it",        run(FAKE,  [str(d)]).returncode == 1)
    check("fake: config-drift unaffected",    run(DRIFT, [str(d)]).returncode == 0)
finally:
    shutil.rmtree(d, ignore_errors=True)

# ── 3. an undeclared env read trips config-drift ONLY ──────────────────────
def add_drift(d):
    p = d / "src" / "charge.js"
    p.write_text(p.read_text() + "const secret = process.env.UNDECLARED_SECRET;\n")
d = fresh(add_drift)
try:
    check("drift: config-drift catches it",   run(DRIFT, [str(d)]).returncode == 1)
    check("drift: no-fakes unaffected",       run(FAKE,  [str(d)]).returncode == 0)
finally:
    shutil.rmtree(d, ignore_errors=True)

# ── 4. an unbacked done-claim trips task-record ONLY ───────────────────────
def break_verdict(d):
    (d / "spec/10-delivery/verification/review-report.md").write_text("# review\nno verdict here\n")
d = fresh(break_verdict)
try:
    r = run(REC, [str(d / "spec"), "--task", "T-001"])
    check("unbacked: task-record catches it", r.returncode == 1 and "VERDICT" in (r.stdout + r.stderr))
    check("unbacked: no-fakes unaffected",    run(FAKE, [str(d)]).returncode == 0)
finally:
    shutil.rmtree(d, ignore_errors=True)

# ── 5. dropping a tagged test trips task-record's source-coverage check ─────
def drop_tag(d):
    (d / "tests/e2e/charge.test.js").write_text("it('charges', () => {});\n")   # @covers AC-001a removed
d = fresh(drop_tag)
try:
    r = run(REC, [str(d / "spec"), "--task", "T-001"])
    check("untagged: task-record catches missing @covers", r.returncode == 1 and "AC-001a" in (r.stdout + r.stderr))
finally:
    shutil.rmtree(d, ignore_errors=True)

# ── 6. a faked deploy artifact trips deploy-real ONLY ──────────────────────
def fake_deploy(d):
    (d / ".github/workflows/deploy.yml").write_text(
        "jobs:\n  deploy:\n    steps:\n      - run: echo TODO implement deploy && exit 0\n")
d = fresh(fake_deploy)
try:
    check("fakedeploy: deploy-real catches it",  run(DEPLOY, [str(d)]).returncode == 1)
    check("fakedeploy: no-fakes unaffected",     run(FAKE,   [str(d)]).returncode == 0)
    check("fakedeploy: config-drift unaffected", run(DRIFT,  [str(d)]).returncode == 0)
finally:
    shutil.rmtree(d, ignore_errors=True)

# ── 6b. a faked/empty migration trips migration-real ONLY ──────────────────
def fake_migration(d):
    (d / "migrations/001_orders.sql").write_text("-- TODO: write the real migration\n")
d = fresh(fake_migration)
try:
    check("fakemig: migration-real catches it", run(MIG,    [str(d)]).returncode == 1)
    check("fakemig: no-fakes unaffected",       run(FAKE,   [str(d)]).returncode == 0)
    check("fakemig: deploy-real unaffected",    run(DEPLOY, [str(d)]).returncode == 0)
finally:
    shutil.rmtree(d, ignore_errors=True)

# ── 7. a done-claim that OMITS the deploy row trips task-record ─────────────
def drop_deploy_row(d):
    p = d / "spec/10-delivery/verification/tasks/T-001.md"
    p.write_text("\n".join(l for l in p.read_text().splitlines() if "| deploy |" not in l) + "\n")
d = fresh(drop_deploy_row)
try:
    r = run(REC, [str(d / "spec"), "--task", "T-001"])
    check("nodeployrow: task-record catches omission", r.returncode == 1 and "deploy" in (r.stdout + r.stderr))
finally:
    shutil.rmtree(d, ignore_errors=True)

print("\n%d passed, %d failed" % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
