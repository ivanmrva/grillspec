#!/usr/bin/env python3
# test_check_release_attestation.py - regression tests for check_release_attestation.py (the opt-in release gate).
# Covers verdict, --deep depth, and freshness (the attestation must still cover HEAD). Stdlib only; no network
# (uses local `git` only, which CI has). Run:  python3 tools/test_check_release_attestation.py
import subprocess, sys, tempfile, shutil, pathlib

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE / "check_release_attestation.py"

def git(d, *a):
    return subprocess.run(["git", "-C", str(d), "-c", "user.email=t@t", "-c", "user.name=t", *a],
                          capture_output=True, text=True)

def run(report_text=None, args=(), repo=False, tierb="release verdict: PASS\n"):
    d = pathlib.Path(tempfile.mkdtemp(prefix="attest_"))
    try:
        sha = "0" * 40
        if repo:
            subprocess.run(["git", "init", "-q", str(d)], capture_output=True, text=True)
            (d / "f.txt").write_text("x")
            git(d, "add", "-A"); git(d, "commit", "-q", "-m", "init")
            sha = git(d, "rev-parse", "HEAD").stdout.strip() or sha
        if tierb is not None:
            tr = d / "spec" / "10-delivery" / "verification" / "test-run.md"
            tr.parent.mkdir(parents=True, exist_ok=True)
            tr.write_text(tierb, encoding="utf-8")
        if report_text is not None:
            (d / "build-audit-report.md").write_text(report_text.replace("{SHA}", sha), encoding="utf-8")
        out = subprocess.run([sys.executable, str(TOOL), str(d), *args], capture_output=True, text=True)
        return out.returncode, out.stdout + out.stderr
    finally:
        shutil.rmtree(d, ignore_errors=True)

PASS = FAIL = 0
def expect(name, rc, output, want_rc, must=(), forbid=()):
    global PASS, FAIL
    probs = []
    if rc != want_rc: probs.append("rc %d != %d" % (rc, want_rc))
    probs += [("missing: " + s) for s in must if s not in output]
    probs += [("unexpected: " + s) for s in forbid if s in output]
    if probs:
        FAIL += 1; print("FAIL  " + name)
        for pr in probs: print("        " + pr)
        print("        --- output ---\n" + "\n".join("        " + l for l in output.splitlines()))
    else:
        PASS += 1; print("ok    " + name)

# clean: ATTESTED + depth: deep + a commit stamp that matches HEAD → passes with no warnings
rc, o = run("BUILD ATTESTATION: ATTESTED — 0 blocking · depth: deep\ncommit: {SHA}\n", repo=True)
expect("attested-deep-fresh-passes", rc, o, 0, must=["ATTESTED", "fresh"], forbid=["WARN", "ERROR"])

# a --deep report whose BODY says 'sample' still counts as deep (parse the marker, not the prose)
rc, o = run("BUILD ATTESTATION: ATTESTED · depth: deep\ncommit: {SHA}\nnotes: reviewed a sample of logs.\n", repo=True)
expect("deep-with-sample-word-passes", rc, o, 0, must=["depth: deep, fresh"], forbid=["WARN", "ERROR"])

# Tier-B release verdict: missing test-run.md → WARN (ERROR under --require-fresh); FAIL verdict → ERROR
rc, o = run("BUILD ATTESTATION: ATTESTED · depth: deep\ncommit: {SHA}\n", repo=True, tierb=None)
expect("tierb-missing-warns", rc, o, 0, must=["WARN", "no Tier-B release verdict"])
rc, o = run("BUILD ATTESTATION: ATTESTED · depth: deep\ncommit: {SHA}\n", repo=True, tierb=None, args=("--require-fresh",))
expect("tierb-missing-strict-errors", rc, o, 1, must=["ERROR", "no Tier-B release verdict"])
rc, o = run("BUILD ATTESTATION: ATTESTED · depth: deep\ncommit: {SHA}\n", repo=True, tierb="release verdict: FAIL\n")
expect("tierb-fail-errors", rc, o, 1, must=["ERROR", "release verdict is FAIL"])

# STALE: the stamped commit doesn't match HEAD (work landed since the audit) → ERROR
rc, o = run("BUILD ATTESTATION: ATTESTED · depth: deep\ncommit: deadbeefdeadbeefdeadbeef\n", repo=True)
expect("stale-attestation-fails", rc, o, 1, must=["ERROR", "STALE"])

# SAMPLED (attest) but fresh → only a depth WARN by default
rc, o = run("BUILD ATTESTATION: ATTESTED · depth: attest (sampled 6 of 34)\ncommit: {SHA}\n", repo=True)
expect("attested-sampled-warns", rc, o, 0, must=["WARN", "SAMPLED"], forbid=["ERROR"])

# ...and --require-deep makes that a hard ERROR
rc, o = run("BUILD ATTESTATION: ATTESTED · depth: attest (sampled 6 of 34)\ncommit: {SHA}\n",
            args=("--require-deep",), repo=True)
expect("require-deep-fails-on-sampled", rc, o, 1, must=["ERROR", "deep"])

# freshness UNVERIFIABLE: deep, but no commit stamp → WARN by default
rc, o = run("BUILD ATTESTATION: ATTESTED · depth: deep\n", repo=True)
expect("no-stamp-warns", rc, o, 0, must=["WARN", "UNVERIFIABLE"], forbid=["ERROR"])

# ...and --require-fresh makes the unverifiable case a hard ERROR
rc, o = run("BUILD ATTESTATION: ATTESTED · depth: deep\n", args=("--require-fresh",), repo=True)
expect("require-fresh-fails-unverifiable", rc, o, 1, must=["ERROR", "UNVERIFIABLE"])

# NOT-ATTESTED / NOT-ATTESTABLE / no-verdict / missing all fail before the depth+freshness checks
rc, o = run("BUILD ATTESTATION: NOT-ATTESTED — 3 blocking.\n")
expect("not-attested-fails", rc, o, 1, must=["NOT-ATTESTED", "not cleared"])
rc, o = run("BUILD ATTESTATION: NOT-ATTESTABLE (spec not clean)\n")
expect("not-attestable-fails", rc, o, 1, must=["NOT-ATTESTABLE"])
rc, o = run("# build-audit-report\nsome notes, no verdict.\n")
expect("no-verdict-fails", rc, o, 1, must=["no 'BUILD ATTESTATION"])
rc, o = run(None)
expect("missing-report-fails", rc, o, 1, must=["no build attestation", "before release"])

print("\n%d passed, %d failed" % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
