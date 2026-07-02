#!/usr/bin/env python3
# check_e2e_target.py - a tripwire against "e2e" tests that actually run against a LOCAL stack.
#
# The tier contract (spec/09-solution/test/levels.md) names each tier's target-env. Tiers whose target-env is
# NOT `local` (e2e/journey/smoke/NFR-evidence) must run against a REAL deployed environment - an "e2e" against
# docker-compose/testcontainers/localhost is integration mislabelled: it never exercises the deploy, env-config,
# secrets, or networking that break in prod, so a green run proves nothing about the deployment. This catches
# the mechanically-detectable version of that: a non-local-tier test that hard-references a local stack.
#   ERROR: a test in a real-env tier that references localhost / 127.0.0.1 / docker-compose / testcontainers.
# The e2e target should come from config/env (the named deployed env), never a hardcoded local host. Suppress a
# legitimate case (a genuinely local pre-check) with an inline `e2e-target: allow <reason>` or an entry in
# `.claude/e2e-target-allow.txt`.
#
# No-ops cleanly when there is no tier contract or no test tree. Run from the project root:
#   python3 tools/check_e2e_target.py [project_root] [--tests tests,test] [--levels <path>]
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

CODE_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".java", ".kt", ".rb", ".cs", ".php", ".rs", ".scala", ".swift", ".feature", ".yaml", ".yml", ".json"}
TIER_SEG = re.compile(r"/(?:tests?|specs?|__tests__)/(?:.*/)?(unit|integration|contract|e2e|journey|smoke|system|acceptance|nfr)(?:/|_|-|\.|$)", re.I)
FNAME_TIER = re.compile(r"(?:^|[._-])(unit|integration|int|contract|e2e|journey|smoke|system|acceptance|nfr)[._-]", re.I)
SYNONYM = {"journey": "e2e", "smoke": "e2e", "system": "e2e", "acceptance": "e2e", "nfr": "e2e", "int": "integration"}
LOCAL = re.compile(r"\b(?:localhost|127\.0\.0\.1|0\.0\.0\.0|docker-compose|docker_compose|testcontainers|"
                   r"GenericContainer|compose\.up|host\.docker\.internal)\b", re.I)

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
# tiers that must hit a real deployed env: target-env present and not 'local'.
realenv = {t for t, row in contract.items()
           if (row.get("target-env", "") or "").strip().lower() not in ("", "local", "-", "—", "n-a", "n/a")}

allow = []
allowf = ROOT / ".claude" / "e2e-target-allow.txt"
if allowf.exists():
    for ln in allowf.read_text(encoding="utf-8", errors="replace").splitlines():
        ln = ln.split("#", 1)[0].strip()
        if ln:
            allow.append(ln)

F = []
def add(sev, where, msg):
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
    print("check_e2e_target: no tier contract in %s - nothing to enforce." % LEVELS)
    sys.exit(0)
if not realenv:
    print("check_e2e_target: the contract names no real-deployed-env tier - nothing to enforce.")
    sys.exit(0)
if not roots:
    print("check_e2e_target: no test tree (%s) under %s - nothing to scan." % ("/".join(TEST_DIRS), ROOT))
    sys.exit(0)

scanned = 0
for base in roots:
    for p in sorted(base.rglob("*")):
        if not p.is_file() or p.suffix not in CODE_EXT:
            continue
        posix = "/" + p.as_posix().strip("/")
        tier = tier_of(posix, p.name)
        if tier not in realenv:
            continue
        scanned += 1
        rel = p.relative_to(ROOT).as_posix()
        env = contract[tier].get("target-env", "?")
        for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if "e2e-target: allow" in line:
                continue
            if LOCAL.search(line):
                add("ERROR", "%s:%d" % (rel, n),
                    "tier '%s' must run against the deployed env '%s' but this points at a local stack - "
                    "integration mislabelled as e2e; take the target from config/env, not a hardcoded host." % (tier, env))

for sev, where, msg in sorted(F, key=lambda x: x[1]):
    print("%-5s %-40s %s" % (sev, where, msg))
e = sum(1 for x in F if x[0] == "ERROR")
print("\n%d error(s) over %d real-env-tier test file(s); real-env tiers: %s."
      % (e, scanned, ", ".join(sorted(realenv))))
sys.exit(1 if e else 0)
