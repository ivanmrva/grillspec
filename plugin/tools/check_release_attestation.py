#!/usr/bin/env python3
# check_release_attestation.py - the (opt-in) release gate: a fresh whole-build attestation must exist and pass.
#
# The per-task gates prove each TASK was done right; the whole-build audit proves the BUILD as a whole was (its
# verdict lands in build-audit-report.md at the project root). Nothing consumes that verdict - so a release can
# ship with a stale or missing attestation. This closes that, symmetric to how check_task_record.py makes the
# per-task conformance verdict a hard gate row. It is DELIBERATELY opt-in: run it at release / in a release
# workflow, and make it a REQUIRED branch-protection check if your team wants release gating enforced (the
# system's stance is that the per-task checks aren't optional but the release decision stays the team's - so this
# ships available, not wired-on).
#   ERROR: no build-audit-report.md; or its verdict is NOT-ATTESTED / NOT-ATTESTABLE; or it carries no verdict line.
#   WARN (ERROR under --require-deep): the report is ATTESTED but was a SAMPLED (`attest`) run, not a full
#     `--deep` re-judgment - the release bar should require the full independent pass (a sampled second-pass can
#     miss the one task that overfit its visible tests). Make it `--require-deep` to enforce.
#   ERROR: the attestation is STALE - it stamps `commit: <sha>` but HEAD has moved since (work landed after the
#     audit, so the ATTESTED verdict no longer covers the current tree). Re-run the whole-build audit at HEAD.
#   WARN (ERROR under --require-fresh): freshness UNVERIFIABLE - no `commit:` stamp in the report, or not a git
#     repo. A strict release gate should require a verifiably-fresh attestation.
#
# Run at release time from the project root:
#   python3 tools/check_release_attestation.py [project_root] [--report <path>] [--require-deep] [--require-fresh]
import sys, re, pathlib, subprocess

args = [a for a in sys.argv[1:] if not a.startswith("--")]
ROOT = pathlib.Path(args[0] if args else ".")
def opt(flag, default):
    for i, a in enumerate(sys.argv):
        if a == flag and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default
REPORT = pathlib.Path(opt("--report", str(ROOT / "build-audit-report.md")))
REQUIRE_DEEP = "--require-deep" in sys.argv
REQUIRE_FRESH = "--require-fresh" in sys.argv

def git_head(root):
    try:
        r = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None
    except Exception:
        return None

# the verdict line the whole-build audit writes: "BUILD ATTESTATION: ATTESTED | NOT-ATTESTED | NOT-ATTESTABLE ..."
VERDICT = re.compile(r"BUILD ATTESTATION:\s*(ATTESTED|NOT-ATTESTED|NOT-ATTESTABLE)", re.I)

if not REPORT.exists():
    print("ERROR  no build attestation at %s - run the whole-build audit before release." % REPORT)
    print("\n1 error(s).")
    sys.exit(1)

text = REPORT.read_text(encoding="utf-8", errors="replace")
m = VERDICT.search(text)
if not m:
    print("ERROR  %s carries no 'BUILD ATTESTATION: <verdict>' line - not a valid attestation." % REPORT)
    print("\n1 error(s).")
    sys.exit(1)

verdict = m.group(1).upper()
if verdict != "ATTESTED":
    print("ERROR  %s: BUILD ATTESTATION: %s - the build is not cleared for release." % (REPORT, verdict))
    print("\n1 error(s).")
    sys.exit(1)

# ATTESTED - now evaluate depth and freshness; collect all issues so one run reports everything.
issues = []  # (level, message)

# depth: was it the full --deep re-judgment, or a sampled `attest` run? Parse the marker VALUE (not a
# whole-text scan for "sampl", which a deep report's prose could trip on).
dm = re.search(r"depth:\s*([a-z]+)", text, re.I)
if not (dm and dm.group(1).lower() in ("deep", "full")):
    issues.append(("ERROR" if REQUIRE_DEEP else "WARN",
                   "SAMPLED (`attest`) run, not a full `--deep` re-judgment - a release bar should require the "
                   "full independent pass. Re-run `audit-build --deep`."))

# freshness: does the attestation still cover the current tree? It stamps `commit: <sha>`; compare to HEAD.
sha_m = re.search(r"commit:\s*([0-9a-f]{7,40})", text, re.I)
head = git_head(ROOT)
if sha_m and head:
    attested = sha_m.group(1).lower()
    if not (head.startswith(attested) or attested.startswith(head)):
        issues.append(("ERROR", "STALE - attestation covers commit %s but HEAD is %s; work landed since the "
                                "audit. Re-run `audit-build --deep` at HEAD." % (attested[:12], head[:12])))
else:
    why = "the report carries no `commit:` stamp" if not sha_m else "not a git repo / git unavailable"
    issues.append(("ERROR" if REQUIRE_FRESH else "WARN",
                   "freshness UNVERIFIABLE (%s) - can't confirm the attestation covers the current tree." % why))

errs = [msg for lvl, msg in issues if lvl == "ERROR"]
warns = [msg for lvl, msg in issues if lvl == "WARN"]
for msg in errs:
    print("ERROR  %s: %s" % (REPORT, msg))
for msg in warns:
    print("WARN   %s: %s" % (REPORT, msg))
if not issues:
    print("ok     %s: BUILD ATTESTATION: ATTESTED (depth: deep, fresh)." % REPORT)
print("\n%d error(s), %d warning(s)." % (len(errs), len(warns)))
sys.exit(1 if errs else 0)
