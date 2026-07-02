#!/usr/bin/env python3
# check_mock_budget.py - a coarse, high-precision tripwire against tests that mock beyond their tier's ceiling.
#
# The test strategy's tier contract (spec/09-solution/test/levels.md) declares, per tier, a `mock-ceiling`:
#   none         -> no test doubles at all (unit/contract/e2e): a mock here means the test is doing another
#                   tier's work, or an e2e that mocks isn't e2e. ANY mock usage is an ERROR.
#   boundary-only -> integration: real DB/broker/filesystem, mock ONLY third-party network at the boundary.
#                   A mock that names a real-dep keyword (the tier's declared real deps, or db/broker/repo/...)
#                   is an ERROR - "use the real dependency, not a double".
#   n-a / absent  -> not enforced.
# This is the mechanical detector for over-mocking that check_no_fakes.py deliberately does NOT do (that tool
# never scans tests/). Like it, this is deliberately conservative and escapable, because a noisy gate gets
# `--no-verify`d: suppress with an inline `mock-budget: allow <reason>` comment, or a path/substring entry in
# `.claude/mock-budget-allow.txt`.
#
# No-ops cleanly when there is no tier contract or no test tree. Run from the project root:
#   python3 tools/check_mock_budget.py [project_root] [--tests tests,test] [--levels <path>] [--strict]
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

CODE_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".java", ".kt", ".rb", ".cs", ".php", ".rs", ".scala", ".swift"}
# a test file's tier, from its path (the directory segment) or a filename hint.
TIER_SEG = re.compile(r"/(?:tests?|specs?|__tests__)/(?:.*/)?(unit|integration|contract|e2e|journey|smoke|system|acceptance|nfr)(?:/|_|-|\.|$)", re.I)
FNAME_TIER = re.compile(r"(?:^|[._-])(unit|integration|int|contract|e2e|journey|smoke|system|acceptance|nfr)[._-]", re.I)
SYNONYM = {"journey": "e2e", "smoke": "e2e", "system": "e2e", "acceptance": "e2e", "nfr": "e2e", "int": "integration"}
# no leading \b: some alternatives start with '@' (a non-word char), before which \b can never match; each
# token instead carries its own trailing \b / punctuation to stay precise.
MOCK = re.compile(
    r"(?:unittest\.mock|mock\.(?:patch|Mock|MagicMock|AsyncMock)|@patch\b|\bMagicMock\b|\bAsyncMock\b|"
    r"\bsinon\b|\btestdouble\b|td\.replace|jest\.(?:mock|fn|spyOn)|vi\.(?:mock|fn|spyOn)|\bnock\b|"
    r"org\.mockito|\bmockito\b|@Mock\b|\beasymock\b|\bmoq\b|\bnsubstitute\b|\bfakeiteasy\b|\bgomock\b|golang/mock|testify/mock|\bmockk\b)",
    re.I)
IMPORT_MOCK = re.compile(r"\b(?:from\s+mock\b|import\s+mock\b|require\(['\"][^'\"]*mock)", re.I)
DEFAULT_REALDEP = ("db", "database", "datastore", "repository", "repo", "sql", "postgres", "mysql", "sqlite",
                   "mongo", "redis", "broker", "kafka", "rabbit", "queue", "sqs", "pubsub", "filesystem", "fs")

def load_contract(path):
    """{tier: {col: value}} parsed from the levels.md tier-contract table (header has 'tier' + 'mock-ceiling')."""
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

def realdeps(row):
    raw = (row.get("real-deps", "") or "").lower()
    toks = [t.strip() for t in re.split(r"[,/;·]", raw) if t.strip() and t.strip() not in ("none", "-", "—", "all", "n-a", "n/a")]
    return tuple(set(toks) | set(DEFAULT_REALDEP))

contract = load_contract(LEVELS)

allow = []
allowf = ROOT / ".claude" / "mock-budget-allow.txt"
if allowf.exists():
    for ln in allowf.read_text(encoding="utf-8", errors="replace").splitlines():
        ln = ln.split("#", 1)[0].strip()
        if ln:
            allow.append(ln)

F = []
def add(sev, where, msg):
    if sev == "WARN" and STRICT:
        sev = "ERROR"
    if not any(a in where or a in msg for a in allow):
        F.append((sev, where, msg))

def tier_of(posix, name):
    m = TIER_SEG.search(posix) or FNAME_TIER.search(name)
    if not m:
        return None
    t = m.group(1).lower()
    return SYNONYM.get(t, t)

roots = [ROOT / d for d in TEST_DIRS if (ROOT / d).is_dir()]
if not contract:
    print("check_mock_budget: no tier contract in %s - nothing to enforce." % LEVELS)
    sys.exit(0)
if not roots:
    print("check_mock_budget: no test tree (%s) under %s - nothing to scan." % ("/".join(TEST_DIRS), ROOT))
    sys.exit(0)

scanned = 0
for base in roots:
    for p in sorted(base.rglob("*")):
        if not p.is_file() or p.suffix not in CODE_EXT:
            continue
        posix = "/" + p.as_posix().strip("/")
        tier = tier_of(posix, p.name)
        if tier is None or tier not in contract:
            continue  # untier-able / undeclared tier -> check_test_tiers' concern, not this one
        ceiling = (contract[tier].get("mock-ceiling", "") or "").lower()
        if ceiling in ("", "n-a", "n/a", "-", "—"):
            continue
        deps = realdeps(contract[tier])
        scanned += 1
        rel = p.relative_to(ROOT).as_posix()
        for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if "mock-budget: allow" in line:
                continue
            if not (MOCK.search(line) or IMPORT_MOCK.search(line)):
                continue
            where = "%s:%d" % (rel, n)
            if ceiling == "none":
                add("ERROR", where, "tier '%s' has mock-ceiling 'none' but this test mocks - push the double out, "
                                    "or move the test to the tier its real dependencies belong to." % tier)
            elif ceiling in ("boundary-only", "boundary"):
                low = line.lower()
                hit = next((d for d in deps if re.search(r"\b%s\b" % re.escape(d), low)), None)
                if hit:
                    add("ERROR", where, "tier '%s' is boundary-only but this mocks a real dependency ('%s') - "
                                        "integration tests use the real %s (testcontainers), not a double." % (tier, hit, hit))

order = {"ERROR": 0, "WARN": 1}
for sev, where, msg in sorted(F, key=lambda x: (order[x[0]], x[1])):
    print("%-5s %-40s %s" % (sev, where, msg))
e = sum(1 for x in F if x[0] == "ERROR")
w = len(F) - e
print("\n%d error(s), %d warning(s) over %d tiered test file(s); contract tiers: %s."
      % (e, w, scanned, ", ".join(sorted(contract))))
sys.exit(1 if e else 0)
