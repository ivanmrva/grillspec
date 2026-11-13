#!/usr/bin/env python3
# test_e2e_gates.py - end-to-end integration test for the tree-facing gates as a CHAIN.
#
# The per-tool suites (test_check_task / test_check_no_fakes / test_check_config_drift /
# test_check_deploy_real / test_check_migration_real / test_check_mock_budget / test_check_test_tiers /
# test_check_e2e_target / test_check_no_skips) lock each tool's behaviour in isolation. THIS proves they
# compose on one realistic mini-project: a properly-done task (real code, no fakes, declared config, a real
# deploy, a real migration, a done-claim the tree backs, a full tiered test tree) passes ALL gates, and each
# distinct kind of cheat trips exactly the gate that owns it. Stdlib only; no network.
# Run: python3 tools/test_e2e_gates.py
import subprocess, sys, tempfile, shutil, pathlib

HERE = pathlib.Path(__file__).resolve().parent
REC  = HERE / "check_task.py"
FAKE = HERE / "check_no_fakes.py"
DRIFT = HERE / "check_config_drift.py"
DEPLOY = HERE / "check_deploy_real.py"
MIG  = HERE / "check_migration_real.py"
MB   = HERE / "check_mock_budget.py"
TT   = HERE / "check_test_tiers.py"
ET   = HERE / "check_e2e_target.py"
NS   = HERE / "check_no_skips.py"

def project(d):
    """A clean, fully-backed mini-project: one done task, real code, declared config, @covers-tagged tests."""
    f = {
        # the task brief: one acceptance criterion, a done-claim
        "spec/10-delivery/tasks/T-001.md":
            "<!-- scope: x | excludes: y | format: z -->\n# T-001 — Charge an order\n\n"
            "| field | value |\n|---|---|\n| tier | feature |\n| phase | MVP · afk: eligible |\n"
            "| status | done |\n| behavior | UC-001<br>AC-001a — Given an open order, when charged, then it is saved |\n"
            "| touches | API-Charge |\n| rules | SEC-1 — only the owner may charge |\n",
        # the env matrix (the declared config side)
        "spec/09-solution/infra-ops/environments.md":
            "<!-- scope: x | excludes: y | format: matrix -->\n"
            "| Key | Purpose | dev | prod |\n|---|---|---|---|\n"
            "| DATABASE_URL | store | local | distinct |\n| STRIPE_API_KEY | pay | test | live |\n",
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
        # the machine-readable tier contract (the tier/mock/e2e gates read this)
        "spec/09-solution/test/levels.md":
            "# levels\n\n## Tier contract\n"
            "| tier | real-deps | may-mock | mock-ceiling | target-env | coverage-bar | mutation-bar |\n"
            "|---|---|---|---|---|---|---|\n"
            "| unit | none | — | none | local | 80% | 70% |\n"
            "| integration | db | third-party-network | boundary-only | local | 70% | — |\n"
            "| contract | provider,consumer | — | none | local | — | — |\n"
            "| e2e | all | — | none | preview | — | — |\n",
        # every declared tier has a suite; no mocks; the e2e reads its target from env
        "tests/unit/charge.unit.test.js": "it('adds', () => { expect(1 + 1).toBe(2); });\n",
        "tests/integration/charge.int.test.js": "it('persists', async () => { await db.save({}); });\n",
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

# ── 1. the clean project passes ALL gates ──────────────────────────────────
d = fresh()
try:
    r1 = run(REC,   [str(d / "spec"), "--task", "T-001"])
    r2 = run(FAKE,  [str(d)])
    r3 = run(DRIFT, [str(d)])
    r4 = run(DEPLOY, [str(d)])
    r5 = run(MIG,   [str(d)])
    r6 = run(MB,    [str(d)])
    r7 = run(TT,    [str(d)])
    r8 = run(ET,    [str(d)])
    r10 = run(NS,   [str(d)])
    check("clean: task done-claim passes",  r1.returncode == 0, r1.stdout + r1.stderr)
    check("clean: no-fakes passes",     r2.returncode == 0, r2.stdout + r2.stderr)
    check("clean: config-drift passes", r3.returncode == 0, r3.stdout + r3.stderr)
    check("clean: deploy-real passes",  r4.returncode == 0, r4.stdout + r4.stderr)
    check("clean: migration-real passes", r5.returncode == 0, r5.stdout + r5.stderr)
    check("clean: mock-budget passes",  r6.returncode == 0, r6.stdout + r6.stderr)
    check("clean: test-tiers passes",   r7.returncode == 0, r7.stdout + r7.stderr)
    check("clean: e2e-target passes",   r8.returncode == 0, r8.stdout + r8.stderr)
    check("clean: no-skips passes",     r10.returncode == 0, r10.stdout + r10.stderr)
    rr = run(REC, [str(d / "spec"), "--trace"])
    check("clean: trace names the covering test", "| AC-001a | T-001 | tests/e2e/charge.test.js |" in rr.stdout, rr.stdout)
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

# ── 4. a `critical` task without its review trips the task check ONLY ──────
def make_critical(d):
    p = d / "spec/10-delivery/tasks/T-001.md"
    p.write_text(p.read_text().replace("| tier | feature |", "| tier | critical — money path |\n| review | pending |"))
d = fresh(make_critical)
try:
    r = run(REC, [str(d / "spec"), "--task", "T-001"])
    check("unreviewed: task check catches it", r.returncode == 1 and "review" in (r.stdout + r.stderr))
    check("unreviewed: no-fakes unaffected",   run(FAKE, [str(d)]).returncode == 0)
finally:
    shutil.rmtree(d, ignore_errors=True)

# ── 5. dropping a tagged test trips the task check's source-coverage check ──
def drop_tag(d):
    (d / "tests/e2e/charge.test.js").write_text("it('charges', () => {});\n")   # @covers AC-001a removed
d = fresh(drop_tag)
try:
    r = run(REC, [str(d / "spec"), "--task", "T-001"])
    check("untagged: task check catches missing @covers", r.returncode == 1 and "AC-001a" in (r.stdout + r.stderr))
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

# ── 8. a mock at a 'none'-ceiling tier trips mock-budget ONLY ──────────────
def unit_mock(d):
    (d / "tests/unit/charge.unit.test.js").write_text("jest.mock('../../src/charge');\nit('x', () => {});\n")
d = fresh(unit_mock)
try:
    check("unitmock: mock-budget catches it", run(MB, [str(d)]).returncode == 1)
    check("unitmock: test-tiers unaffected",  run(TT, [str(d)]).returncode == 0)
    check("unitmock: no-fakes unaffected",    run(FAKE, [str(d)]).returncode == 0)
finally:
    shutil.rmtree(d, ignore_errors=True)

# ── 9. a declared tier with no suite trips test-tiers ONLY ─────────────────
def drop_integration(d):
    shutil.rmtree(d / "tests" / "integration", ignore_errors=True)
d = fresh(drop_integration)
try:
    # per-commit (default) is a WARN — mid-build a tier may not have landed; the release gate (--require-all-tiers) errors
    soft = run(TT, [str(d)])
    r = run(TT, [str(d), "--require-all-tiers"])
    check("notier: per-commit only WARNs",            soft.returncode == 0 and "not yet built" in (soft.stdout + soft.stderr))
    check("notier: --require-all-tiers catches it",   r.returncode == 1 and "integration" in (r.stdout + r.stderr))
    check("notier: mock-budget unaffected",           run(MB, [str(d)]).returncode == 0)
finally:
    shutil.rmtree(d, ignore_errors=True)

# ── 10. an "e2e" on a local stack trips e2e-target ONLY ────────────────────
def localhost_e2e(d):
    (d / "tests/e2e/charge.test.js").write_text("// @covers AC-001a\nconst base = 'http://localhost:3000';\nit('charges', () => {});\n")
d = fresh(localhost_e2e)
try:
    check("localhoste2e: e2e-target catches it", run(ET, [str(d)]).returncode == 1)
    check("localhoste2e: mock-budget unaffected", run(MB, [str(d)]).returncode == 0)
finally:
    shutil.rmtree(d, ignore_errors=True)

# ── 10b. a skipped test trips no-skips ONLY ────────────────────────────────
def skip_test(d):
    (d / "tests/e2e/charge.test.js").write_text("// @covers AC-001a\nit.skip('charges', () => {});\n")
d = fresh(skip_test)
try:
    check("skip: no-skips catches it",       run(NS, [str(d)]).returncode == 1)
    check("skip: mock-budget unaffected",    run(MB, [str(d)]).returncode == 0)
    check("skip: test-tiers unaffected",     run(TT, [str(d)]).returncode == 0)
finally:
    shutil.rmtree(d, ignore_errors=True)

print("\n%d passed, %d failed" % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
