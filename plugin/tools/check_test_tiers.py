#!/usr/bin/env python3
# check_test_tiers.py - verifies the ACTUAL test tree matches the tier contract declared in the strategy.
#
# The tier contract (spec/09-solution/test/levels.md) declares which tiers the strategy requires. This confirms
# each declared tier actually EXISTS as a suite, and that no tests sit in a tier the contract never declared -
# a failure a per-task review can't see (it only sees one slice's tests, never the suite as a whole):
#   a declared tier with ZERO test files -> WARN by default (a build is incremental: contract/e2e/NFR-evidence
#     tiers legitimately don't exist until their tasks land, so a PER-COMMIT gate must not go red on a not-yet-due
#     tier); ERROR only under --require-all-tiers (audit-build / the release gate, where the build is complete and
#     every declared tier must exist).
#   WARN:  a test classified into a tier the contract never declares - misfiled, or an undeclared tier.
# It also prints the per-tier file counts (informational) so the distribution-shape judgment in audit-build has
# the numbers. Test-file classification + contract parsing are shared with the mock/e2e gates via tier_contract.py
# (co-located `foo.int.test.ts` and bare `foo.test.ts` = unit are handled; production/helper files are skipped).
#
# No-ops cleanly when there is no tier contract or no test tree. Run from the project root:
#   python3 tools/check_test_tiers.py [project_root] [--tests <roots>] [--levels <path>] [--require-all-tiers] [--strict]
import sys, pathlib
from tier_contract import load_contract, classify, iter_test_files, DEFAULT_ROOTS

args = [a for a in sys.argv[1:] if not a.startswith("--")]
ROOT = pathlib.Path(args[0] if args else ".")
def opt(flag, default):
    for i, a in enumerate(sys.argv):
        if a == flag and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default
TEST_DIRS = [s for s in opt("--tests", DEFAULT_ROOTS).split(",") if s]
LEVELS = pathlib.Path(opt("--levels", str(ROOT / "spec" / "09-solution" / "test" / "levels.md")))
STRICT = "--strict" in sys.argv
REQUIRE = "--require" in sys.argv                 # a test tree with NO tier contract becomes an ERROR (audit-build)
REQUIRE_ALL = "--require-all-tiers" in sys.argv   # every declared tier must have a suite (release completeness)

contract = load_contract(LEVELS)

F = []
def add(sev, where, msg):
    if sev == "WARN" and STRICT:
        sev = "ERROR"
    F.append((sev, where, msg))

roots_exist = any((ROOT / d).is_dir() for d in TEST_DIRS)
if not contract:
    if REQUIRE and roots_exist:
        print("%-5s %-24s %s" % ("ERROR", "tier-contract",
              "a test tree exists but the strategy declares NO tier contract in %s - the test strategy was never "
              "derived (or its levels.md carries no parseable tier-contract table)." % LEVELS))
        print("\n1 error(s), 0 warning(s).")
        sys.exit(1)
    print("check_test_tiers: no tier contract in %s - nothing to enforce." % LEVELS)
    sys.exit(0)
if not roots_exist:
    print("check_test_tiers: no test tree (%s) under %s - nothing to scan." % ("/".join(TEST_DIRS), ROOT))
    sys.exit(0)

counts = {}          # declared/mapped tier -> test-file count
undeclared = {}      # a recognized tier not in the contract -> a sample path
for posix, name, p in iter_test_files(ROOT, TEST_DIRS):
    tier = classify(posix, name)
    if tier in contract:
        counts[tier] = counts.get(tier, 0) + 1
    else:
        undeclared.setdefault(tier, p.relative_to(ROOT).as_posix())

for tier in sorted(contract):
    if counts.get(tier, 0) == 0:
        # a declared tier with no suite: WARN mid-build (tiers arrive as their tasks land - a per-commit gate must
        # not go red on a not-yet-due tier), ERROR only under --require-all-tiers (audit-build / release). Appended
        # directly so --strict doesn't promote it - its level is governed solely by --require-all-tiers.
        F.append(("ERROR" if REQUIRE_ALL else "WARN", "tier:" + tier,
                  "the tier contract declares '%s' but no %s suite exists - not yet built. Fine mid-build; "
                  "enforced at release (audit-build / the release gate run --require-all-tiers)." % (tier, tier)))
for tier, sample in sorted(undeclared.items()):
    add("WARN", sample, "tests classified as tier '%s' which the contract never declares - misfiled, or an "
                        "undeclared tier that dodged the strategy." % tier)

order = {"ERROR": 0, "WARN": 1}
for sev, where, msg in sorted(F, key=lambda x: (order[x[0]], x[1])):
    print("%-5s %-24s %s" % (sev, where, msg))
shape = " · ".join("%s=%d" % (t, counts.get(t, 0)) for t in sorted(contract))
e = sum(1 for x in F if x[0] == "ERROR")
w = len(F) - e
print("\n%d error(s), %d warning(s). tier distribution: %s." % (e, w, shape or "(empty)"))
sys.exit(1 if e else 0)
