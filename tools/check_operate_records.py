#!/usr/bin/env python3
# check_operate_records.py - reconciles the append-only 12-operate ledger against the spec it enacted.
#
# 12-operate/ is a log of what actually happened to the running system (deploy/migration/incident/diagnosis
# records). It is never derived from the spec, so guard_derived.py doesn't protect it and check_freshness.py
# doesn't cover it - nothing checks that an operational record corresponds to the spec it claims to enact. This
# does the RECONCILIATION (never rewrites a record - it's a log of reality):
#   ERROR: a record references a known-type spec ID (T-/DATA-/NFR-/SEC-/SLO-/...) that resolves NOWHERE in the
#          rest of the spec - a dangling operate-record reference.
#   ERROR: a deploy-<env>-<version>.md whose <env> is not a declared environment (infra-ops topology/environments)
#          - deployed to an env off the ratified promotion path.
#   WARN:  a deploy record that names no T- (no trace to what shipped); a migration record that cites no DATA-.
#
# No-ops cleanly when there is no 12-operate ledger. Run from the project root:
#   python3 tools/check_operate_records.py [project_root] [--spec spec]
import sys, re, pathlib

args = [a for a in sys.argv[1:] if not a.startswith("--")]
ROOT = pathlib.Path(args[0] if args else ".")
def opt(flag, default):
    for i, a in enumerate(sys.argv):
        if a == flag and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default
SPEC = ROOT / opt("--spec", "spec")
OPERATE = SPEC / "12-operate"

# known ID prefixes (mirrors lint_spec's vocabulary; kept local so the tool is self-contained).
PREFIXES = ("T", "UC", "AC", "CMD", "EVT", "AGG", "INV", "DATA", "API", "NFR", "ASR", "SLO",
            "SEC", "OBL", "THR", "MOD", "JRN", "ML", "DS", "MET")
IDRE = re.compile(r"\b(" + "|".join(PREFIXES) + r")-([A-Za-z0-9_]+)\b")
DEPLOY_FILE = re.compile(r"^deploy-([A-Za-z0-9]+)-", re.I)

def ids_in(text):
    return {"%s-%s" % (m.group(1), m.group(2)) for m in IDRE.finditer(text)}

F = []
def add(sev, where, msg):
    F.append((sev, where, msg))

if not OPERATE.is_dir():
    print("check_operate_records: no 12-operate ledger under %s - nothing to reconcile." % SPEC)
    sys.exit(0)

# the universe of IDs defined/used ANYWHERE in the spec except the operate ledger itself.
known = set()
if SPEC.is_dir():
    for p in SPEC.rglob("*.md"):
        if OPERATE in p.parents or p.parent == OPERATE:
            continue
        known |= ids_in(p.read_text(encoding="utf-8", errors="replace"))

# declared environments, for the deploy-env reconciliation (skip the check if we can't find the source).
env_text = ""
for rel in ("09-solution/infra-ops/topology.md", "09-solution/infra-ops/environments.md"):
    f = SPEC / rel
    if f.exists():
        env_text += "\n" + f.read_text(encoding="utf-8", errors="replace").lower()

records = 0
for p in sorted(OPERATE.rglob("*.md")):
    if not p.is_file():
        continue
    records += 1
    rel = p.relative_to(ROOT).as_posix()
    text = p.read_text(encoding="utf-8", errors="replace")
    refs = ids_in(text)
    for rid in sorted(refs):
        if rid not in known:
            add("ERROR", rel, "references %s, which resolves nowhere in the spec - a dangling operate-record reference." % rid)
    name = p.name.lower()
    if name.startswith("deploy-"):
        if not any(r.startswith("T-") for r in refs):
            add("WARN", rel, "a deploy record that names no T- - no trace to which tasks/slice shipped.")
        m = DEPLOY_FILE.match(p.name)
        if m and env_text:
            env = m.group(1).lower()
            if not re.search(r"\b%s\b" % re.escape(env), env_text):
                add("ERROR", rel, "deployed to env '%s', which is not a declared environment (infra-ops topology/environments) - off the ratified promotion path." % env)
    if name.startswith("migration") and not any(r.startswith("DATA-") for r in refs):
        add("WARN", rel, "a migration record that cites no DATA- - no trace to the data change it enacted.")

order = {"ERROR": 0, "WARN": 1}
for sev, where, msg in sorted(F, key=lambda x: (order[x[0]], x[1])):
    print("%-5s %-44s %s" % (sev, where, msg))
e = sum(1 for x in F if x[0] == "ERROR")
w = len(F) - e
print("\n%d error(s), %d warning(s) over %d operate record(s)." % (e, w, records))
sys.exit(1 if e else 0)
