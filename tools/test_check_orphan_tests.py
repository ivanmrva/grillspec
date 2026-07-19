#!/usr/bin/env python3
# test_check_orphan_tests.py - regression tests for check_orphan_tests.py (the reverse-traceability /
# drift tripwire: every behavioral test traces to a live spec driver).
#
# Each scenario writes a tiny project, runs the tool, asserts which findings fire (must=) and which do NOT
# (forbid=) - locking the precision so a later edit can't make it noisier or blind. Stdlib only; no network.
# Run:  python3 tools/test_check_orphan_tests.py
import subprocess, sys, os, tempfile, shutil, pathlib

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE / "check_orphan_tests.py"

def run(files, args=(), env_extra=None):
    d = pathlib.Path(tempfile.mkdtemp(prefix="orphantest_"))
    try:
        for rel, content in files.items():
            p = d / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding="utf-8")
        env = dict(os.environ, **env_extra) if env_extra else None
        out = subprocess.run([sys.executable, str(TOOL), str(d), *args],
                             capture_output=True, text=True, env=env)
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

SPEC = {"spec/06-requirements/acceptance.md": "## Criteria\n- AC-001 charges the card\n- AC-002 refunds\n"}
TAGGED_JS = "// @covers AC-001\nit('charges the card', () => { expect(pay(1)).toBe(true) })\n"
UNTAGGED_JS = "it('charges the card', () => { expect(pay(1)).toBe(true) })\n"

# no spec/ tree -> nothing to reconcile against, clean no-op
expect("no-spec-noop", run({"tests/pay.test.js": UNTAGGED_JS}),
       must=["nothing to reconcile"], forbid=["ERROR"])

# no test files -> clean no-op
expect("no-tests-noop", run(dict(SPEC)), must=["nothing to scan"], forbid=["ERROR"])

# a tagged suite is clean
expect("tagged-clean", run({**SPEC, "tests/pay.test.js": TAGGED_JS}),
       must=["0 error(s)"], forbid=["ERROR"])

# an untagged failing-capable test source is an ORPHAN
expect("orphan-fires", run({**SPEC, "tests/pay.test.js": UNTAGGED_JS}),
       must=["ERROR", "no spec driver", "DRIFT"])

# a @covers naming an ID the spec doesn't know is DANGLING
expect("dangling-fires", run({**SPEC, "tests/pay.test.js":
                              "// @covers AC-999\nit('x', () => {})\n"}),
       must=["ERROR", "dangling driver", "AC-999"])

# multiple IDs on one line: only the unknown one fires
expect("mixed-ids", run({**SPEC, "tests/pay.test.js":
                         "// @covers AC-001, AC-777\nit('x', () => {})\n"}),
       must=["ERROR", "AC-777"], forbid=["AC-001 names"])

# prose after the tag never reads as a driver ID (lowercase tokens are not IDs)
expect("prose-not-id", run({**SPEC, "tests/pay.test.js":
                            "// @covers AC-001 when user-123 pays\nit('x', () => {})\n"}),
       must=["0 error(s)"], forbid=["ERROR", "user-123"])

# a @state tag counts as a driver (the ux-cell sibling of @covers)
expect("state-tag-drives", run({**SPEC, "tests/checkout.test.tsx":
                                "// @state:empty\nit('renders empty state', () => {})\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# a test-named file with NO runnable test declaration (helper-shaped) is never flagged
expect("helper-not-flagged", run({**SPEC, "tests/util.test.js":
                                  "export const mkUser = () => ({id: 1})\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# python: the tag lives in a comment, read on raw text
expect("python-tagged", run({**SPEC, "tests/test_pay.py":
                             "# @covers AC-002\ndef test_refund():\n    assert refund(1)\n"}),
       must=["0 error(s)"], forbid=["ERROR"])
expect("python-orphan", run({**SPEC, "tests/test_pay.py":
                             "def test_refund():\n    assert refund(1)\n"}),
       must=["ERROR", "no spec driver"])

# inline waiver: a legitimately driver-free suite (fitness functions, generated harness)
expect("inline-waiver", run({**SPEC, "tests/arch.test.js":
                             "// no-orphans: allow architecture fitness function, no spec driver by design\n"
                             "it('no domain import from adapters', () => {})\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# allow-file waiver by path substring
expect("allowfile-waiver", run({**SPEC,
                                ".grillspec/no-orphans-allow.txt": "tests/generated/  # scaffolded harness\n",
                                "tests/generated/smoke.test.js": UNTAGGED_JS}),
       must=["0 error(s)"], forbid=["ERROR"])

# the spec ID may live in a contract yaml, not only markdown
expect("yaml-id-counts", run({"spec/07-solution/contracts/openapi.yaml": "x-spec-id: API-010\n",
                              "tests/api.test.js": "// @covers API-010\nit('x', () => {})\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# -- the off-grammar sweep: test-shaped content under a test tree, invisible to the classifier ----------
# a file in tests/ that declares tests but matches no recognized naming pattern is an ERROR
expect("offgrammar-fires", run({**SPEC, "tests/pay_checks.py":
                                "# @covers AC-001\ndef test_charge():\n    assert pay(1)\n"}),
       must=["ERROR", "unrecognized test naming"])

# ...even when EVERY test in the project is off-grammar (the early no-tests exit must not swallow it)
expect("offgrammar-only-project", run({**SPEC, "tests/verify_payment.js":
                                       "it('charges', () => { expect(pay(1)).toBe(true) })\n"}),
       must=["ERROR", "unrecognized test naming"])

# a helper in tests/ with no test declarations is never flagged by the sweep
expect("offgrammar-helper-ok", run({**SPEC, "tests/factories.py":
                                    "def make_user():\n    return {'id': 1}\n"}),
       forbid=["ERROR", "unrecognized"])

# Gherkin .feature files are recognized by extension - exempt from the naming grammar
expect("feature-exempt", run({**SPEC, "tests/checkout.feature":
                              "Feature: checkout\n  Scenario: pays\n    When I pay\n"}),
       forbid=["ERROR", "unrecognized"])

# the inline waiver covers a deliberate off-grammar exception
expect("offgrammar-waiver", run({**SPEC, "tests/harness_driver.py":
                                 "# no-orphans: allow generated harness driver, runner-invoked directly\n"
                                 "def test_all():\n    run_generated()\n"}),
       forbid=["ERROR", "unrecognized"])

# co-located src is NEVER swept for naming - a production helper named test_* -shaped is not a test tree
expect("src-not-swept", run({**SPEC, "src/util/probe.py":
                             "def test_connection():\n    return ping()\n"}),
       forbid=["ERROR", "unrecognized"])

# -- shared GRILLSPEC_TEST_ROOTS lever: a monorepo rooted under code/ is invisible to the tier_contract walk
# -- (root/<d> is top-level only) until the env names 'code' - the same lever check_task_record honors ------
CODE_ORPHAN = {**SPEC, "code/apps/pay/src/pay.test.js": "it('charges', () => { expect(pay(1)).toBe(true) })\n"}
# without the env, root/code is never entered -> the orphan under it is invisible (false clean is the bug)
expect("code-rooted-invisible-without-env", run(CODE_ORPHAN),
       must=["nothing to scan"], forbid=["ERROR"])
# with the env, the tree is walked and the untagged test is caught as the orphan it is
expect("code-rooted-seen-with-env", run(CODE_ORPHAN, env_extra={"GRILLSPEC_TEST_ROOTS": "code"}),
       must=["ERROR", "no spec driver"])

print("\n%d ok, %d failed" % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
