#!/usr/bin/env python3
# spec_status.py - mechanical readiness rollup (stdlib only).
# Usage:  python3 tools/spec_status.py [spec_dir]
# An OBJECTIVE completeness signal to complement lint_spec.py (pass/fail). It counts and checks
# structure; it does NOT judge whether the content is correct - that stays the conductor's job.
import sys, re, pathlib
SPEC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "spec")
# TYPES mirrors lint_spec.py's vocabulary (selfcheck guards them in sync).
TYPES = "UC|AC|CMD|EVT|AGG|VO|HOT|POL|RM|ENTL|ENT|NFR|ASR|API|SEC|THR|DATA|OBL|SLO|EXP|DS|ML|FAC|REPO|SVC|IF|MOD|CA|ADR|T"
PREFIXES = TYPES.split("|")
ID = "(?:" + TYPES + r")-[A-Za-z0-9._-]*[A-Za-z0-9]"   # tail matches lint_spec's IDCORE (allows '.'/'_', e.g. DATA-Customer.id)
DEF1 = re.compile(r"^\s*[-*#]*\s*\|?\s*\**(" + ID + r")\b")
DEF2 = re.compile(r"^\s*id:\s*(" + ID + r")\b", re.I)
IDTOK = re.compile(r"(?<![A-Za-z0-9-])" + ID)   # left boundary (matches lint_spec): a preceding alnum OR '-' blocks the match, so a namespaced SUR-AGG-250 yields no phantom id
def read(p):
    try: return p.read_text(encoding="utf-8", errors="replace")
    except Exception: return ""
files = sorted(SPEC.rglob("*.md")) if SPEC.exists() else []
defined = {}
for p in files:
    for l in read(p).splitlines():
        m = DEF1.match(l) or DEF2.match(l)
        if m and m.group(1) not in defined: defined[m.group(1)] = p
def of(pre): return sorted(d for d in defined if d.split("-")[0].upper() == pre)
ALL = "\n".join(read(p) for p in files)
uc, ac, nfr, asr, tasks = of("UC"), of("AC"), of("NFR"), of("ASR"), of("T")
ac_nums = set(m.group(1) for a in ac for m in [re.match(r"^AC-(\d+)[a-z]+$", a)] if m)
uc_with_ac = [u for u in uc for m in [re.match(r"^UC-(\d+)$", u)] if m and m.group(1) in ac_nums]
afk_elig = len(re.findall(r"afk:\s*eligible", ALL, re.I))
afk_block = len(re.findall(r"afk:\s*blocked", ALL, re.I))
gaps = sum(1 for l in ALL.splitlines() if re.search(r"\bGAP\b", l) and re.search(r"\bUNRESOLVED\b", l, re.I))
def count_entries(name):
    hits = list(SPEC.glob("**/" + name))
    if not hits: return None
    return sum(1 for l in read(hits[0]).splitlines() if re.match(r"^\s*([-*]|\d+\.)\s+\S", l))
tps = list(SPEC.glob("**/traceability.md"))
trace = set()
if tps:
    for l in read(tps[0]).splitlines(): trace |= set(IDTOK.findall(l))
adrs = of("ADR") or sorted(set(re.findall(r"ADR-[A-Za-z][A-Za-z0-9]*-\d+", " ".join(p.name for p in files))))
def pct(a, b): return ("%d%%" % round(100.0 * a / b)) if b else "n/a"
def shown(x): return "-" if x is None else str(x)
print("SPEC STATUS  (" + str(SPEC) + ")")
print("=" * 54)
if not files:
    print("no spec/*.md found - nothing to report."); sys.exit(0)
print("elements defined:")
for pre in PREFIXES:
    c = len(of(pre))
    if c: print("  %-5s %d" % (pre, c))
print("-" * 54)
print("use-cases:           %d  (with an acceptance criterion: %d / %s)" % (len(uc), len(uc_with_ac), pct(len(uc_with_ac), len(uc))))
print("acceptance criteria: %d" % len(ac))
print("NFRs / ASRs:         %d / %d" % (len(nfr), len(asr)))
print("tasks:               %d  (afk eligible: %d, blocked: %d)" % (len(tasks), afk_elig, afk_block))
print("ADRs:                %d" % len(adrs))
print("traceability matrix: %s%s" % ("present" if tps else "ABSENT", ("  (%d ids referenced)" % len(trace)) if tps else ""))
print("-" * 54)
blockers = []
if gaps: blockers.append("%d unresolved GAP(s) in tasks" % gaps)
ucm = len(uc) - len(uc_with_ac)
if ucm: blockers.append("%d use-case(s) with no acceptance criteria" % ucm)
if afk_block: blockers.append("%d task(s) afk:blocked (need a human)" % afk_block)
if blockers:
    print("NOT mechanically clear to build:")
    for b in blockers: print("  - " + b)
else:
    print("no mechanical blockers (gaps / ACs / afk all clear).")
print("NOTE: mechanical only - it does not judge whether the content is RIGHT.")
