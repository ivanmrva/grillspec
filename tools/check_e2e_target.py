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
# `.claude/e2e-target-allow.txt`. Contract parsing + test-file classification are shared via tier_contract.py.
#
# No-ops cleanly when there is no tier contract or no test tree. Run from the project root:
#   python3 tools/check_e2e_target.py [project_root] [--tests <roots>] [--levels <path>]
import sys, re, pathlib
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

LOCAL = re.compile(r"\b(?:localhost|127\.0\.0\.1|0\.0\.0\.0|docker-compose|docker_compose|testcontainers|"
                   r"GenericContainer|compose\.up|host\.docker\.internal)\b", re.I)

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

roots_exist = any((ROOT / d).is_dir() for d in TEST_DIRS)
if not contract:
    print("check_e2e_target: no tier contract in %s - nothing to enforce." % LEVELS)
    sys.exit(0)
if not realenv:
    print("check_e2e_target: the contract names no real-deployed-env tier - nothing to enforce.")
    sys.exit(0)
if not roots_exist:
    print("check_e2e_target: no test tree (%s) under %s - nothing to scan." % ("/".join(TEST_DIRS), ROOT))
    sys.exit(0)

scanned = 0
for posix, name, p in iter_test_files(ROOT, TEST_DIRS):
    tier = classify(posix, name)
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
