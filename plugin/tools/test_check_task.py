#!/usr/bin/env python3
# test_check_task.py - regression tests for check_task.py (status + done-claim computed from the tree).
#
# Each scenario writes a tiny project to a tempdir, runs the tool, and asserts what the output must and must
# not contain plus the exit code. Stdlib only. Run:  python3 tools/test_check_task.py   (exit 0 = all pass).
import os, subprocess, sys, tempfile, shutil, pathlib, json

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE / "check_task.py"
HDR = "<!-- scope: x | excludes: y | format: z -->"

def run(files, *args, env=None):
    d = pathlib.Path(tempfile.mkdtemp(prefix="tasktest_"))
    try:
        for rel, content in files.items():
            p = d / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        e = {k: v for k, v in os.environ.items() if k != "GRILLSPEC_TEST_ROOTS"}
        e.update(env or {})
        out = subprocess.run([sys.executable, str(TOOL), str(d / "spec"), *args], capture_output=True, text=True, cwd=d, env=e)
        return out.returncode, out.stdout + out.stderr
    finally:
        shutil.rmtree(d, ignore_errors=True)

PASS = FAIL = 0
def expect(name, result, code=None, must=(), forbid=()):
    global PASS, FAIL
    rc, output = result
    probs = [("missing: " + s) for s in must if s not in output] + \
            [("unexpected: " + s) for s in forbid if s in output]
    if code is not None and rc != code:
        probs.append("exit code %d, wanted %d" % (rc, code))
    if probs:
        FAIL += 1; print("FAIL  " + name)
        for pr in probs: print("        " + pr)
        print("        --- output ---\n        " + output.replace("\n", "\n        "))
    else:
        PASS += 1; print("ok    " + name)

def brief(status="done", tier="feature", behavior="UC-1<br>AC-1a — Given an open invoice, when paid, then it is marked paid", extra=""):
    return (HDR + "\n# T-002\n\n| field | value |\n|---|---|\n| tier | %s |\n| phase | MVP · afk: eligible |\n"
            "| status | %s |\n| behavior | %s |\n%s" % (tier, status, behavior, extra))

T = "spec/10-delivery/tasks/T-002.md"
COVERED = {"tests/pay.test.js": "// @covers AC-1a\nit('marks the invoice paid', () => {})\n"}

expect("no-tasks-is-clean", run({"spec/04-domain/ddd/a.md": HDR}), code=0, must=["nothing to check"])
expect("done-and-covered-passes", run(dict(COVERED, **{T: brief()})), code=0, must=["| T-002 | feature | MVP | done | 1/1 |"], forbid=["ERROR"])
expect("done-without-covers-fails", run({T: brief()}), code=1, must=["claims done but: no `@covers` test for AC-1a"])
expect("in-progress-is-reported-not-gated", run({T: brief(status="in-progress")}), code=0, must=["| in-progress | 0/1 |"], forbid=["ERROR"])
expect("task-flag-gates-an-in-progress-task", run({T: brief(status="in-progress")}, "--task", "T-002"), code=1, must=["is checked as done but: no `@covers` test for AC-1a"])
expect("covers-in-a-readme-is-not-coverage", run({T: brief(), "docs/README.md": "@covers AC-1a\n"}), code=1, must=["no `@covers` test for AC-1a"])
expect("covers-in-a-helper-without-a-test-is-not-coverage", run({T: brief(), "tests/helpers.js": "// @covers AC-1a\nexport const x = 1\n"}), code=1)
expect("covers-id-must-match-whole-token", run({T: brief(), "tests/pay.test.js": "// @covers AC-1ab\nit('x', () => {})\n"}), code=1)
expect("colocated-test-counts", run({T: brief(), "src/billing/pay.test.ts": "// @covers AC-1a\ntest('x', () => {})\n"}), code=0)
expect("nested-source-root-counts", run({T: brief(), "code/apps/pay/src/pay.test.ts": "// @covers AC-1a\ntest('x', () => {})\n"}), code=0)
expect("unresolved-gap-fails", run(dict(COVERED, **{T: brief(extra="| rules | GAP retention period — data — UNRESOLVED |\n")})), code=1, must=["1 unresolved GAP(s)"])
expect("open-dependency-fails", run(dict(COVERED, **{T: brief(extra="| depends | T-001 |\n"),
       "spec/10-delivery/tasks/T-001.md": HDR + "\n| field | value |\n|---|---|\n| tier | critical |\n| status | in-progress |\n"})),
       code=1, must=["depends on T-001 (not done)"])
expect("done-dependency-passes", run(dict(COVERED, **{T: brief(extra="| depends | T-001 |\n"),
       "spec/10-delivery/tasks/T-001.md": HDR + "\n| field | value |\n|---|---|\n| tier | feature |\n| status | done |\n"})), code=0)
expect("critical-needs-review-pass", run(dict(COVERED, **{T: brief(tier="critical — money path", extra="| review | pending |\n")})),
       code=1, must=["`critical` task without `review | PASS`"])
expect("critical-with-review-pass", run(dict(COVERED, **{T: brief(tier="critical — money path", extra="| review | PASS |\n")})), code=0, must=["| pass |"])
expect("design-first-needs-its-note", run(dict(COVERED, **{T: brief(extra="| design | design-first — 10-delivery/impl-design/T-002-pay.md |\n")})),
       code=1, must=["design note is missing"])
expect("design-first-with-note", run(dict(COVERED, **{T: brief(extra="| design | design-first — 10-delivery/impl-design/T-002-pay.md |\n"),
       "spec/10-delivery/impl-design/T-002-pay.md": HDR + "\nnote\n"})), code=0)
UX = "| ux | JRN-7 · SCR-3 · states: empty · loading · error → prototypes/pay.html |\n"
expect("ui-states-need-state-tags", run(dict(COVERED, **{T: brief(extra=UX)})), code=1, must=["no `@state:` test for empty, loading, error"])
expect("ui-states-covered", run({T: brief(extra=UX), "tests/pay.test.js":
       "// @covers AC-1a\n// @state:empty @state:loading @state:error\nit('x', () => {})\n"}), code=0, must=["| 3/3 |"])
expect("ux-na-needs-no-states", run(dict(COVERED, **{T: brief(extra="| ux | N/A — headless |\n")})), code=0)
rc, out = run(dict(COVERED, **{T: brief()}), "--json")
try:
    data = json.loads(out); ok = rc == 0 and data[0]["task"] == "T-002" and data[0]["acs_covered"] == 1
except Exception:
    ok = False
expect("json-status", (0 if ok else 1, out), code=0)
expect("trace-lists-covering-tests", run(dict(COVERED, **{T: brief()}), "--trace"), code=0, must=["| AC-1a | T-002 | tests/pay.test.js |"])
expect("missing-status-row-is-todo", run({T: HDR + "\n| field | value |\n|---|---|\n| tier | feature |\n| behavior | UC-1<br>AC-1a — x |\n"}), code=0, must=["| todo |"])
expect("unknown-task-id", run({T: brief()}, "--task", "T-999"), code=2, must=["no task brief"])

print("\n%d passed, %d failed" % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
