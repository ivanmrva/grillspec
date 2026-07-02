#!/usr/bin/env python3
# check_test_tiers.py - verifies the ACTUAL test tree matches the tier contract declared in the strategy.
#
# The tier contract (spec/09-solution/test/levels.md) declares which tiers the strategy requires. This confirms
# each declared tier actually EXISTS as a suite, and that no tests live in a tier the contract never declared -
# the two failures a per-task review can't see (it only sees one slice's tests, never the suite as a whole):
#   ERROR: a declared tier with ZERO test files - the strategy names it but nothing was built.
#   WARN:  a test directory that maps to no declared tier - misfiled, or an undeclared tier that dodged the contract.
# It also prints the per-tier file counts (informational) so the distribution-shape judgment in audit-build has
# the numbers. It does NOT judge whether a given test sits at the RIGHT tier (that's semantic - audit-build) nor
# whether the distribution matches pyramid/integration-weighted (that's a judgment on these counts).
#
# No-ops cleanly when there is no tier contract or no test tree. Run from the project root:
#   python3 tools/check_test_tiers.py [project_root] [--tests tests,test] [--levels <path>] [--strict]
import sys, re, pathlib

args = [a for a in sys.argv[1:] if not a.startswith("--")]
ROOT = pathlib.Path(args[0] if args else ".")
def opt(flag, default):
    for i, a in enumerate(sys.argv):
        if a == flag and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default
TEST_DIRS = [s for s in opt("--tests", "tests,test").split(",") if s]
LEVELS = pathlib.Path(opt("--levels", str(ROOT / "spec" / "09-solution" / "test" / "levels.md")))
STRICT = "--strict" in sys.argv
REQUIRE = "--require" in sys.argv   # a test tree with NO tier contract becomes an ERROR (audit-build passes this)

CODE_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".java", ".kt", ".rb", ".cs", ".php", ".rs", ".scala", ".swift", ".json", ".feature", ".yaml", ".yml"}
TIER_SEG = re.compile(r"/(?:tests?|specs?|__tests__)/(?:.*/)?(unit|integration|contract|e2e|journey|smoke|system|acceptance|nfr)(?:/|_|-|\.|$)", re.I)
# also detect the tier from the FILENAME (co-located / named-by-tier layouts: foo.e2e.test.ts, bar_integration_test.py)
FNAME_TIER = re.compile(r"(?:^|[._-])(unit|integration|int|contract|e2e|journey|smoke|system|acceptance|nfr)[._-]", re.I)
SYNONYM = {"journey": "e2e", "smoke": "e2e", "system": "e2e", "acceptance": "e2e", "nfr": "e2e", "int": "integration"}

def load_contract(path):
    if not path.exists():
        return {}
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for i, ln in enumerate(lines):
        if "|" in ln and re.search(r"\btier\b", ln, re.I) and re.search(r"mock-?ceiling", ln, re.I):
            cols = [c.strip().lower().replace(" ", "-") for c in ln.strip().strip("|").split("|")]
            out = {}
            for dl in lines[i + 1:]:
                s = dl.strip()
                if not s.startswith("|"):
                    break
                if re.match(r"^\|?[\s:|-]+\|?$", s):
                    continue
                cells = [c.strip() for c in s.strip().strip("|").split("|")]
                if len(cells) < len(cols):
                    continue
                row = dict(zip(cols, cells))
                t = row.get("tier", "").lower()
                if t:
                    out[t] = row
            return out
    return {}

contract = load_contract(LEVELS)

F = []
def add(sev, where, msg):
    if sev == "WARN" and STRICT:
        sev = "ERROR"
    F.append((sev, where, msg))

def tier_of(posix, name):
    m = TIER_SEG.search(posix) or FNAME_TIER.search(name)
    if not m:
        return None
    t = m.group(1).lower()
    return SYNONYM.get(t, t)

roots = [ROOT / d for d in TEST_DIRS if (ROOT / d).is_dir()]
if not contract:
    if REQUIRE and roots:
        print("%-5s %-24s %s" % ("ERROR", "tier-contract",
              "a test tree exists (%s) but the strategy declares NO tier contract in %s - the test strategy "
              "was never derived (or its levels.md carries no tier-contract table)." % ("/".join(TEST_DIRS), LEVELS)))
        print("\n1 error(s), 0 warning(s).")
        sys.exit(1)
    print("check_test_tiers: no tier contract in %s - nothing to enforce." % LEVELS)
    sys.exit(0)
if not roots:
    print("check_test_tiers: no test tree (%s) under %s - nothing to scan." % ("/".join(TEST_DIRS), ROOT))
    sys.exit(0)

counts = {}          # declared/mapped tier -> file count
undeclared = {}      # raw tier segment not in contract -> a sample path
untierable = total = 0
for base in roots:
    for p in sorted(base.rglob("*")):
        if not p.is_file() or p.suffix not in CODE_EXT:
            continue
        total += 1
        posix = "/" + p.as_posix().strip("/")
        tier = tier_of(posix, p.name)
        if tier is None:
            untierable += 1
            continue
        rel = p.relative_to(ROOT).as_posix()
        if tier in contract:
            counts[tier] = counts.get(tier, 0) + 1
        else:
            undeclared.setdefault(tier, rel)

for tier in sorted(contract):
    if counts.get(tier, 0) == 0:
        add("ERROR", "tier:" + tier, "the tier contract declares '%s' but no %s suite exists under %s - "
                                     "a required test level was never built." % (tier, tier, "/".join(TEST_DIRS)))
for tier, sample in sorted(undeclared.items()):
    add("WARN", sample, "tests filed under tier '%s' which the contract never declares - misfiled, or an "
                        "undeclared tier that dodged the strategy." % tier)
# blindness: if most test files can't be assigned to a tier, this gate (and mock-budget/e2e-target) can't see them
if untierable and untierable >= (total - untierable):
    add("WARN", "tier:coverage", "%d of %d test file(s) couldn't be assigned to a tier (not foldered under a tier "
                                 "dir nor named .<tier>.) - this gate and the mock/e2e gates are blind to them; "
                                 "folder tests by tier or name them by tier." % (untierable, total))

order = {"ERROR": 0, "WARN": 1}
for sev, where, msg in sorted(F, key=lambda x: (order[x[0]], x[1])):
    print("%-5s %-24s %s" % (sev, where, msg))
shape = " · ".join("%s=%d" % (t, counts.get(t, 0)) for t in sorted(contract))
e = sum(1 for x in F if x[0] == "ERROR")
w = len(F) - e
print("\n%d error(s), %d warning(s). tier distribution: %s (%d untier-able of %d)." % (e, w, shape or "(empty)", untierable, total))
sys.exit(1 if e else 0)
