#!/usr/bin/env python3
# test_check_no_fakes.py - regression tests for check_no_fakes.py (the no-fakes-in-production tripwire).
#
# Each scenario writes a tiny project, runs the tool, asserts which findings fire (must=) and which do NOT
# (forbid=) - locking the precision so a later edit can't make it noisier or blind. Stdlib only; no network.
# Run:  python3 tools/test_check_no_fakes.py
import subprocess, sys, tempfile, shutil, pathlib

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE / "check_no_fakes.py"

def run(files, args=()):
    d = pathlib.Path(tempfile.mkdtemp(prefix="nofaketest_"))
    try:
        for rel, content in files.items():
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

CLEAN = "class PaymentService:\n    def charge(self, o):\n        return self.gw.charge(o.total)\n"

# real production code is clean
expect("clean-production", run({"src/a.py": CLEAN}), must=["0 error(s)"], forbid=["ERROR"])

# a Fake* class defined under src/ is an ERROR
expect("fake-class-in-src", run({"src/g.py": "class FakeGateway:\n    pass\n"}),
       must=["ERROR", "FakeGateway", "test double"])

# Stub_/mock_ function names too
expect("stub-func-in-src", run({"src/g.py": "def stub_charge():\n    return True\n"}),
       must=["ERROR", "stub_charge"])

# a mocking-library import in production is an ERROR
expect("mock-import-in-src", run({"src/w.py": "from unittest.mock import MagicMock\n"}),
       must=["ERROR", "mocking/test-double library"])

# the SAME double under tests/ is fine - never scanned
expect("double-under-tests-ok", run({"tests/g.py": "class FakeGateway:\n    pass\n", "src/a.py": CLEAN}),
       must=["0 error(s)"], forbid=["ERROR"])

# a *_test.py / .spec. file inside src is treated as a test, not production
expect("test-named-file-ignored", run({"src/g_test.py": "class FakeGateway:\n    pass\n", "src/a.py": CLEAN}),
       must=["0 error(s)"], forbid=["ERROR"])

# unconfigured -> fallback is a WARN (not a hard block by default)
expect("unconfigured-fallback-warn", run({"src/p.py": "def c():\n    if not configured():\n        return None\n"}),
       must=["WARN", "unconfigured"], forbid=["ERROR"])

# NotImplemented placeholder is a WARN
expect("notimpl-warn", run({"src/p.py": "def c():\n    raise NotImplementedError('todo')\n"}),
       must=["WARN", "placeholder"], forbid=["ERROR"])

# --strict promotes WARN to ERROR
expect("strict-promotes", run({"src/p.py": "def c():\n    if not configured():\n        return None\n"}, args=("--strict",)),
       must=["ERROR"])

# inline waiver suppresses a finding
expect("inline-waiver", run({"src/g.py": "class FakeGateway:  # no-fakes: allow legacy import shim\n    pass\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# allowlist file suppresses by path substring
expect("allowlist-file", run({"src/g.py": "class FakeGateway:\n    pass\n", ".claude/no-fakes-allow.txt": "src/g.py\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# no production source dir at all = clean no-op
expect("no-src-noop", run({"docs/readme.md": "hello\n"}),
       must=["nothing to scan"], forbid=["ERROR", "Traceback"])

# custom --src dirs
expect("custom-src", run({"app/g.py": "class MockRepo:\n    pass\n"}, args=("--src", "app")),
       must=["ERROR", "MockRepo"])

print("\n%d passed, %d failed" % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
