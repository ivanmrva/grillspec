#!/usr/bin/env python3
# test_check_task_record.py - regression tests for check_task_record.py (the per-task accountability backstop).
#
# Each scenario lays down a tiny project (spec/ task + verification records + evidence files), runs the tool,
# and asserts which findings fire (must=) and which do NOT (forbid=) - locking every check so a later edit
# can't silently regress one. Stdlib only; no network. Run:  python3 tools/test_check_task_record.py
import subprocess, sys, os, tempfile, shutil, pathlib

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
TASK_TABLE = (
    "# T-014 — Pay an order\n\n"
    "| field | value |\n"
    "|---|---|\n"
    "| behavior | UC-014 pay an order<br>AC-014a accepts a valid payment |\n"
    "| tests | AC-014a — unit — accepts a valid payment<br>AC-014b — integration — rejects an invalid payment |\n"
    "| api | API-Pay |\n"
    "| security | SEC-03 |\n"
    "| nfr | ASR-002 |\n"
    "| depends | T-002 |\n"
)
TRACE_OK = (
    "| spec ID | T- | code | test | pass |\n|---|---|---|---|---|\n"
    "| AC-014a | T-014 | src/billing.js | t::AC-014a | ✓ |\n"
    "| AC-014b | T-014 | src/billing.js | t::AC-014b | ✓ |\n"
    "| API-Pay | T-014 | src/billing.js | t | ✓ |\n"
)
REVIEW_OK = "# review-report\nReviewed independently.\nVERDICT: PASS — T-014 conforms.\n"

def record(status="done", rows=None, drop=(), extra=()):
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
        ("ux:states", "—", "N/A — headless"),
        ("a11y", "—", "N/A — headless"),
        ("ux:rendered", "—", "N/A — headless"),
        ("prototype-review", "—", "N/A — headless"),
        ("obs", "—", "N/A — no observable surface"),
        ("traceability", "—", "PASS"),
        ("conformance", "review-report.md", "PASS"),
    ] + list(extra)
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

# A real test source carries the @covers tags and a runnable test declaration by default; scenarios that want
# a hole replace that source via `covers=`. A text file or a bare AC mention must never discharge this gate.
def run(files, args=("--task", "T-014"),
        evidence=("tests/e2e/pay.js", "tests/contract/pay.json", "src/billing.js", ".github/workflows/deploy.yml"),
        covers="// @covers AC-014a AC-014b API-Pay\nit('pays an order', () => { throw new Error('assertion sentinel'); });\n",
        env_extra=None):
    d = pathlib.Path(tempfile.mkdtemp(prefix="trectest_"))
    try:
        for ev in evidence:
            p = d / ev; p.parent.mkdir(parents=True, exist_ok=True); p.write_text("x")
        if covers is not None:
            (d / "tests" / "e2e" / "pay.js").write_text(covers, encoding="utf-8")
        for rel, content in files.items():
            p = d / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding="utf-8")
        env = dict(os.environ, **env_extra) if env_extra else None
        out = subprocess.run([sys.executable, str(TOOL), str(d / "spec"), *args],
                             capture_output=True, text=True, env=env)
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

# ── the bar may be worded 'threshold'/'target'/'>=', not just 'bar' ─────────
expect("coverage-threshold-word-ok", run(proj(record(rows={"coverage": ("84% (threshold 80%)", "PASS")}))),
       must=["0 error(s)"], forbid=["ERROR"])
expect("coverage-threshold-below-fails", run(proj(record(rows={"coverage": ("61% (threshold 80%)", "PASS")}))),
       must=["ERROR", "below its bar"])

# ── the ratified tier-contract bar is the floor: an evidence cell claiming a LOWER bar is a shrunk
#    threshold (ERROR), and the measured value must clear the ratified bar, not the claimed one ──
LEVELS = ("<!-- scope: tiers | excludes: x | format: table -->\n"
          "| tier | real-deps | may-mock | mock-ceiling | target-env | coverage-bar | mutation-bar |\n"
          "|---|---|---|---|---|---|---|\n"
          "| unit | none | none | none | local | 80% | 70% |\n")
def _with_levels(f):
    f["spec/09-solution/test/levels.md"] = LEVELS
    return f
expect("coverage-shrunk-bar-fails", run(_with_levels(proj(record(rows={"coverage": ("61% (bar 50%)", "PASS")})))),
       must=["ERROR", "claims bar 50", "ratified", "coverage 61 is below its bar 80"])
expect("coverage-ratified-bar-met-ok", run(_with_levels(proj(record(rows={"coverage": ("84% (bar 80%)", "PASS")})))),
       forbid=["claims bar", "below its bar"])

# ── a free-form coverage/mutation cell (no measured+bar, not N/A) is unverifiable ──
expect("coverage-freeform-fails", run(proj(record(rows={"coverage": ("looks good", "PASS")}))),
       must=["ERROR", "must cite a measured value AND its bar"])

# ── a BARE N/A on the mutation gate (no reason) is a silent skip -> ERROR ──
expect("mutation-bare-na-fails", run(proj(record(rows={"mutation": ("—", "N/A")}))),
       must=["ERROR", "states no reason"])

# ── the measured value is the HEADLINE %, not the first digit anywhere: a task-id / per-file subscores
#    before the headline metric must NOT false-fail a passing row (regression for the 4.11.0 nums[0] bug) ──
expect("mutation-headline-not-taskid", run(proj(record(rows={"mutation":
        ("test:mutation (Stryker), T-002 pure logic — 82.04% overall (account-state.ts 78.57% · stripe-mappers.ts 83.05%) ≥ 70% break", "PASS")}))),
       must=["0 error(s)"], forbid=["ERROR", "below its bar"])
# and it still CATCHES a real miss when the headline is below the bar, even with an id in the prose
expect("mutation-headline-below-bar-caught", run(proj(record(rows={"mutation":
        ("T-002 mutation — 61.5% overall ≥ 70% bar", "PASS")}))),
       must=["ERROR", "61.5 is below its bar 70"])
# a bar keyword must be a whole word — 'min' inside 'deterMINistic' must NOT be read as the bar
# (it grabbed the next number as the threshold and false-failed a passing row)
expect("bar-keyword-not-substring", run(proj(record(rows={"coverage":
        ("deterministic stage at 100% lines · 93.8% overall (bar 80%)", "PASS")}))),
       must=["0 error(s)"], forbid=["ERROR", "below its bar"])
# ...while a real below-bar row with such a word present is still caught
expect("bar-keyword-not-substring-below-caught", run(proj(record(rows={"coverage":
        ("deterministic run — 61% overall (bar 80%)", "PASS")}))),
       must=["ERROR", "61 is below its bar 80"])
# a hyphenated module-name segment is not a bar keyword: `promotion-floor.ts 90.91%` must leave the actual
# `threshold 70` as the bar, rather than treating 90.91 as the bar and 70 as the measured score.
expect("bar-keyword-not-hyphenated-module", run(proj(record(rows={"mutation":
        ("test:mutation (Stryker) — promotion-floor.ts 90.91% killed · break threshold 70", "PASS")}))),
       must=["0 error(s)"], forbid=["ERROR", "below its bar"])
# the standalone word `floor` remains a supported bar spelling.
expect("bar-floor-still-enforced", run(proj(record(rows={"coverage":
        ("61% overall (floor 80%)", "PASS")}))),
       must=["ERROR", "61 is below its bar 80"])

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
expect("ac-claimed-not-in-source", run(proj(record()),
        covers="// @covers AC-014a API-Pay\nit('pays', () => {});\n"),
       must=["ERROR", "AC-014b", "no failing-capable test source"])

# A bare AC mention in a real test source is documentation, not the required @covers tag. This is the exact
# hole that previously let a source comment satisfy the check because it searched only for the raw AC token.
expect("ac-source-comment-is-not-covers-tag", run(proj(record()),
        covers="// AC-014a and AC-014b are exercised here\nit('pays', () => {});\n"),
       must=["ERROR", "AC-014a", "@covers AC-014a", "AC-014b", "@covers AC-014b"])

# A tag in a source-shaped file with no runnable test declaration is not failing-capable evidence.
expect("ac-tag-without-test-is-not-capable", run(proj(record()),
        covers="// @covers AC-014a AC-014b\nexport const fixture = {};\n"),
       must=["ERROR", "AC-014a", "no failing-capable test source"])

# Current derive-tasks output is a two-column field table. An AC declared only in its `tests` cell must still
# become an obligation and require its own source tag; legacy `field: value` parsing cannot silently skip it.
expect("table-tests-cell-ac-requires-source-tag", run(proj(record(), task=TASK_TABLE),
        covers="// @covers AC-014a API-Pay\n// AC-014b integration intent\nit('pays', () => {});\n"),
       must=["ERROR", "AC-014b", "@covers AC-014b"])
expect("table-task-with-tags-passes", run(proj(record(), task=TASK_TABLE)),
       must=["done — 6 obligations", "0 error(s)"], forbid=["ERROR"])

# ── the rendered-surface + obs gate rows are required-presence like deploy ──
expect("missing-ux-states-row", run(proj(record(drop=("ux:states",)))),
       must=["ERROR", "ux:states", "cannot be omitted"], forbid=["0 error(s)"])
expect("missing-obs-row", run(proj(record(drop=("obs",)))),
       must=["ERROR", "obs", "cannot be omitted"], forbid=["0 error(s)"])

# ── a UI task's ux/obs cells mint obligations (JRN-/SLO-/EXP- only) the record must carry ──
TASK_UI = TASK_TABLE + (
    "| ux | JRN-7 (pay) — states: empty · error → prototype: prototypes/ui/pay.html |\n"
    "| a11y | keyboard: tab order · SC 2.4.7 |\n"
    "| obs | SLO-1 payment-latency metric · EXP-2 checkout_completed event |\n"
)
UI_ROWS = {"ux:states": ("tests/e2e/pay.js", "PASS"), "a11y": ("tests/e2e/pay.js", "PASS"),
           "ux:rendered": ("tests/e2e/pay.js", "PASS"), "obs": ("tests/e2e/pay.js", "PASS"),
           "prototype-review": ("frozen — reviewed at finalization", "PASS")}
UI_EXTRA = (("JRN-7", "tests/e2e/pay.js", "PASS"), ("SLO-1", "tests/e2e/pay.js", "PASS"),
            ("EXP-2", "tests/e2e/pay.js", "PASS"))
UI_COVERS = ("// @covers AC-014a AC-014b API-Pay\n// @state:empty @state:error\n"
             "it('pays an order', () => { throw new Error('assertion sentinel'); });\n")
expect("ui-task-ux-obs-obligations-missing", run(proj(record(rows=UI_ROWS), task=TASK_UI), covers=UI_COVERS),
       must=["ERROR", "JRN-7", "SLO-1", "EXP-2", "cannot be shrunk"])
expect("ui-task-ux-obs-obligations-carried", run(proj(record(rows=UI_ROWS, extra=UI_EXTRA), task=TASK_UI), covers=UI_COVERS),
       must=["0 error(s)"], forbid=["ERROR"])

# ── a false 'N/A — headless' on the rendered-surface rows contradicts the task's own non-N/A ux cell ──
expect("ui-task-false-headless-na", run(proj(record(extra=UI_EXTRA), task=TASK_UI), covers=UI_COVERS),
       must=["ERROR", "cannot discharge its rendered-surface gate", "every named signal"])

# ── a PASS with no on-disk evidence path on a rendered-surface/obs row is an assertion, not evidence ──
expect("ui-task-pathless-pass-fails", run(proj(record(rows=dict(UI_ROWS, **{"ux:states": ("done, looks good", "PASS")}),
        extra=UI_EXTRA), task=TASK_UI), covers=UI_COVERS),
       must=["ERROR", "pathless PASS"])

# ── every ux-cell state needs a literal @state:<name> tag in a failing-capable test source ──
expect("ui-task-missing-state-tag-fails", run(proj(record(rows=UI_ROWS, extra=UI_EXTRA), task=TASK_UI),
        covers="// @covers AC-014a AC-014b API-Pay\n// @state:empty\nit('pays', () => { throw new Error('x'); });\n"),
       must=["ERROR", "@state:error"])

# ── a UI slice's prototype-review row must positively read frozen/reviewed/waived ──
expect("ui-task-unreviewed-prototype-fails", run(proj(record(rows=dict(UI_ROWS,
        **{"prototype-review": ("pending — JIT at execution", "PASS")}), extra=UI_EXTRA), task=TASK_UI), covers=UI_COVERS),
       must=["ERROR", "unreviewed screen cannot ride a done-claim"])

# ── an 'N/A — reuses DS-…' ux cell mints NO obligation (DS- is not a ux obligation type) ──
expect("ux-na-reuse-mints-nothing", run(proj(record(),
        task=TASK_TABLE + "| ux | N/A — reuses DS-001 on the existing screen |\n")),
       must=["0 error(s)"], forbid=["ERROR", "DS-001"])

# ── an N/A ux cell whose explanation cross-refs a JRN- mints nothing either (the cell is N/A) ──
expect("ux-na-crossref-mints-nothing", run(proj(record(),
        task=TASK_TABLE + "| ux | N/A — headless (JRN-9 handled by T-020) |\n")),
       must=["0 error(s)"], forbid=["ERROR", "JRN-9"])

# ── a PASS'd NFR obligation row must cite a measurement against a bar, not an assertion ──
expect("nfr-row-unmeasured-fails", run(proj(record(rows={"ASR-002": ("load test looks good", "PASS")}))),
       must=["ERROR", "cites no measurement against a bar"])
expect("nfr-row-measured-ok", run(proj(record(rows={"ASR-002": ("p95 212ms vs target 300ms (k6 run tests/e2e/pay.js)", "PASS")}))),
       must=["0 error(s)"], forbid=["ERROR"])
# the N/A — Tier-B escape stays legal (the default fixture uses it — re-asserted here explicitly)
expect("nfr-row-na-ok", run(proj(record(rows={"ASR-002": ("—", "N/A — evidenced by the Tier-B load run")}))),
       must=["0 error(s)"], forbid=["ERROR"])

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

# ── colocated @covers evidence is found when a source root is NESTED (code/apps/*/src/…) ──
# A monorepo rooted under code/ keeps its tests colocated at code/apps/billing/src/pay.test.js — the source
# root 'src' is present but NOT at parts[0], so the old parts[0] check blinded the scan and reported the AC
# as untested. The any-part membership finds it. (Isolate the @covers evidence there via covers=None so the
# only place the tags live is the nested colocated file.)
CODE_ROOTED = "// @covers AC-014a AC-014b API-Pay\nit('pays', () => { throw new Error('sentinel'); });\n"
_f = proj(record()); _f["code/apps/billing/src/pay.test.js"] = CODE_ROOTED
expect("nested-colocated-source-root-found", run(_f, covers=None),
       forbid=["has no failing-capable test source carrying an `@covers"])

# ── a leaf dir NOT in the recognized root set is not auto-discovered (selectivity preserved) ──
_g = proj(record()); _g["code/billing/pay.test.js"] = CODE_ROOTED
expect("unrecognized-leaf-not-auto-found", run(_g, covers=None),
       must=["has no failing-capable test source carrying an `@covers"])

# ── GRILLSPEC_TEST_ROOTS extends the recognized set for a non-standard leaf name ──
expect("env-root-extends-discovery", run(_g, covers=None, env_extra={"GRILLSPEC_TEST_ROOTS": "billing"}),
       forbid=["has no failing-capable test source carrying an `@covers"])

# ── no records dir at all = clean no-op (early project) ────────────────────
expect("no-records-noop", run({T + "T-014.md": TASK}, args=()),
       must=["no", "records"], forbid=["ERROR", "Traceback"])

# ── omitted [spec_dir] with --task defaults to ./spec — the flag's value must not be eaten as the path ──
# `check_task_record.py --task T-014` used to double-count "T-014" as the spec_dir positional, resolving the
# record at the bogus T-014/10-delivery/… path. Correct parse reads ./spec under the cwd.
_h = pathlib.Path(tempfile.mkdtemp(prefix="trectest_"))
try:
    for rel, content in proj(record()).items():
        p = _h / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding="utf-8")
    _o = subprocess.run([sys.executable, str(TOOL), "--task", "T-014"],
                        capture_output=True, text=True, cwd=_h)
    expect("no-positional-defaults-to-spec", _o.stdout + _o.stderr,
           forbid=["T-014/10-delivery"])
finally:
    shutil.rmtree(_h, ignore_errors=True)

print("\n%d passed, %d failed" % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
