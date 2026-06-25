#!/usr/bin/env python3
# test_check_task_record.py - regression tests for check_task_record.py (the per-task accountability backstop).
#
# Each scenario lays down a tiny project (spec/ task + verification records + evidence files), runs the tool,
# and asserts which findings fire (must=) and which do NOT (forbid=) - locking every check so a later edit
# can't silently regress one. Stdlib only; no network. Run:  python3 tools/test_check_task_record.py
import subprocess, sys, tempfile, shutil, pathlib

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE / "check_task_record.py"

TASK = (
    "T-014 | phase: MVP | Pay an order\n"
    "behavior:    UC-014 · AC-014a, AC-014b\n"
    "api:         API-Pay\n"
    "security:    SEC-03\n"
    "nfr:         ASR-002\n"
    "depends:     T-002\n"
)
TRACE_OK = (
    "| spec ID | T- | code | test | pass |\n|---|---|---|---|---|\n"
    "| AC-014a | T-014 | src/billing.js | t::AC-014a | ✓ |\n"
    "| AC-014b | T-014 | src/billing.js | t::AC-014b | ✓ |\n"
    "| API-Pay | T-014 | src/billing.js | t | ✓ |\n"
)
REVIEW_OK = "# review-report\nReviewed independently.\nVERDICT: PASS — T-014 conforms.\n"

def record(status="done", rows=None, drop=()):
    base = [
        ("UC-014", "tests/e2e/pay.js", "PASS"),
        ("AC-014a", "tests/e2e/pay.js::AC-014a", "PASS"),
        ("AC-014b", "tests/e2e/pay.js::AC-014b", "PASS"),
        ("API-Pay", "tests/contract/pay.json", "PASS"),
        ("SEC-03", "tests/e2e/pay.js", "PASS"),
        ("ASR-002", "—", "N/A — Tier-B"),
        ("tests-first", "—", "PASS"),
        ("tests:layers", "tests/e2e/pay.js · tests/contract/pay.json", "PASS"),
        ("coverage", "84% (bar 80%)", "PASS"),
        ("mutation", "—", "N/A — no domain-logic change"),
        ("fitness:no-fakes", "check_no_fakes clean", "PASS"),
        ("fitness:architecture", "—", "PASS"),
        ("spec-lint", "—", "PASS"),
        ("deploy", ".github/workflows/deploy.yml", "PASS"),
        ("traceability", "—", "PASS"),
        ("conformance", "review-report.md", "PASS"),
    ]
    over = dict(rows or {})
    lines = ["status: %s" % status, "task: T-014",
             "| Obligation | Source | Required | Evidence | Status |", "|---|---|---|---|---|"]
    for key, ev, st in base:
        if key in drop:
            continue
        if key in over:
            ev, st = over[key]
        lines.append("| %s | x | y | %s | %s |" % (key, ev, st))
    return "\n".join(lines) + "\n"

# test files carry the @covers tags (the AC ids literally appear in the test tree) so the source-coverage
# check passes by default; a scenario that wants the hole drops the tag via `covers=`.
def run(files, args=("--task", "T-014"),
        evidence=("tests/e2e/pay.js", "tests/contract/pay.json", "src/billing.js", ".github/workflows/deploy.yml"),
        covers="@covers AC-014a AC-014b API-Pay"):
    d = pathlib.Path(tempfile.mkdtemp(prefix="trectest_"))
    try:
        for ev in evidence:
            p = d / ev; p.parent.mkdir(parents=True, exist_ok=True); p.write_text("x")
        if covers is not None:
            (d / "tests" / "covers.txt").write_text(covers, encoding="utf-8")
        for rel, content in files.items():
            p = d / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding="utf-8")
        out = subprocess.run([sys.executable, str(TOOL), str(d / "spec"), *args], capture_output=True, text=True)
        return out.stdout + out.stderr
    finally:
        shutil.rmtree(d, ignore_errors=True)

V = "spec/10-delivery/verification/"
T = "spec/10-delivery/tasks/"
def proj(rec=None, trace=TRACE_OK, review=REVIEW_OK, task=TASK):
    f = {}
    if task is not None: f[T + "T-014.md"] = task
    if rec is not None: f[V + "tasks/T-014.md"] = rec
    if trace is not None: f[V + "traceability.md"] = trace
    if review is not None: f[V + "review-report.md"] = review
    return f

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

# ── happy path ─────────────────────────────────────────────────────────────
expect("clean-done-passes", run(proj(record())), must=["0 error(s)"],
       forbid=["ERROR"])

# ── in-progress is reported, never blocked ─────────────────────────────────
expect("in-progress-not-gated", run(proj(record(status="in-progress",
        rows={"AC-014a": ("", "PENDING"), "conformance": ("", "PENDING")}))),
       must=["in-progress", "0 error(s)"], forbid=["ERROR"])

# ── a bare done-claim (all PENDING) fails hard ─────────────────────────────
expect("done-with-pending-fails", run(proj(record(rows={k: ("", "PENDING") for k in
        ("AC-014a", "AC-014b", "conformance")}))),
       must=["ERROR", "claims done"], forbid=["0 error(s)"])

# ── the bar cannot be shrunk by dropping a referenced obligation ───────────
expect("dropped-obligation", run(proj(record(drop=("SEC-03",)))),
       must=["ERROR", "SEC-03", "cannot be shrunk"])

# ── conformance PASS in the record but no independent VERDICT on disk ───────
expect("conformance-without-verdict", run(proj(record(), review="# review\nno verdict\n")),
       must=["ERROR", "no independent 'VERDICT: PASS'"])

# ── an AC- with no passing row in the matrix = back-filled/missing test ─────
expect("untraced-ac", run(proj(record(),
        trace="| spec ID | T- | code | test | pass |\n|---|---|---|---|---|\n| AC-014a | T-014 | x | t | ✓ |\n| API-Pay | T-014 | x | t | ✓ |\n")),
       must=["ERROR", "AC-014b", "no passing row"])

# ── fabricated evidence path (file not on disk) ────────────────────────────
expect("fabricated-evidence", run(proj(record(rows={"AC-014a": ("tests/e2e/GHOST.js::AC-014a", "PASS")}))),
       must=["ERROR", "GHOST", "does not exist"])

# ── coverage below the stated bar ──────────────────────────────────────────
expect("coverage-below-bar", run(proj(record(rows={"coverage": ("61% (bar 80%)", "PASS")}))),
       must=["ERROR", "coverage 61 is below its bar 80"])

# ── a done-claim that OMITS the deploy row fails (silent scope reduction) ───
expect("missing-deploy-row", run(proj(record(drop=("deploy",)))),
       must=["ERROR", "deploy", "cannot be omitted"], forbid=["0 error(s)"])

# ── a done-claim that OMITS the tests:layers row fails ─────────────────────
expect("missing-tests-layers-row", run(proj(record(drop=("tests:layers",)))),
       must=["ERROR", "tests:layers", "cannot be omitted"], forbid=["0 error(s)"])

# ── omitting ANY standard gate row (here: traceability) fails the same way ──
expect("missing-traceability-row", run(proj(record(drop=("traceability",)))),
       must=["ERROR", "traceability", "cannot be omitted"], forbid=["0 error(s)"])

# ── a gate row may be N/A with a reason (here: mutation, no domain change) ──
expect("gate-row-na-ok", run(proj(record(rows={"mutation": ("—", "N/A — no domain-logic change")}))),
       must=["0 error(s)"], forbid=["ERROR"])

# ── deploy may be N/A with a reason (slice adds no deployable surface) ──────
expect("deploy-na-ok", run(proj(record(rows={"deploy": ("—", "N/A — no new deployable surface")}))),
       must=["0 error(s)"], forbid=["ERROR"])

# ── a deploy row citing a CI artifact that isn't on disk = fabricated ───────
expect("deploy-fabricated-artifact", run(proj(record(rows={"deploy": (".github/workflows/GHOST.yml", "PASS")}))),
       must=["ERROR", "GHOST", "does not exist"])

# ── matrix claims a test the SOURCE tree doesn't contain (the @covers hole) ──
expect("ac-claimed-not-in-source", run(proj(record()), covers="@covers AC-014a API-Pay"),
       must=["ERROR", "AC-014b", "no file under tests/"])

# ── claim done with no record at all ───────────────────────────────────────
expect("missing-record", run(proj(rec=None)),
       must=["ERROR", "no verification record"])

# ── --report renders a readable, tool-vouched completion report ────────────
expect("report-clean-verified", run(proj(record()), args=("--report", "T-014")),
       must=["VERIFIED", "AC-014a", "tests/e2e/pay.js", "0 error(s)"], forbid=["ISSUE"])
expect("report-flags-issue", run(proj(record(drop=("SEC-03",))), args=("--report", "T-014")),
       must=["ISSUE", "SEC-03"])

# ── --init generates a PENDING checklist from the task's frozen references ──
out = run(proj(rec=None), args=("--init", "T-014"))
expect("init-generates-checklist", out, must=["wrote pre-implementation checklist", "obligation rows"])

# ── no records dir at all = clean no-op (early project) ────────────────────
expect("no-records-noop", run({T + "T-014.md": TASK}, args=()),
       must=["no", "records"], forbid=["ERROR", "Traceback"])

print("\n%d passed, %d failed" % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
