#!/usr/bin/env python3
# impact.py - downstream impact of changed spec IDs (efficient, ID-graph-driven propagation).
# Usage:  python3 tools/impact.py UC-014 CMD-Pay
#         python3 tools/impact.py --area 04-domain/ddd     (all IDs defined under a folder)
#         python3 tools/impact.py --since <gitref>      (self-detect: IDs on lines changed since <gitref>)
# Reads the spec/ reference graph + 10-delivery/verification/traceability.md (to reach code).
# Prints the MINIMAL set of downstream spec files / tasks / code that the change touches,
# ordered upstream -> downstream. This is the dependency tree made operational.
import os, re, sys, subprocess, pathlib
SPEC = pathlib.Path("spec")
if not SPEC.exists(): print("run from the project root (no spec/)"); sys.exit(2)
ID = r"(?:UC|AC|CMD|EVT|AGG|NFR|ASR|API|SEC|DATA|OBL|SLO|EXP|DS|T|ADR)-[A-Za-z0-9._-]*[A-Za-z0-9]"
DEF1 = re.compile(r"^\s*[-*#]*\s*\|?\s*\**(" + ID + r")\b")
DEF2 = re.compile(r"\bid:\s*(" + ID + r")\b", re.I)
REFMARK = re.compile(r"(?:implements?|depends(?:-on)?|refs?|references?|see|satisf(?:y|ies|ied-by)|covers?|covered-by|maps?-?to|reali[sz]es?|traces?-?to|verif(?:y|ies)|validates?|addresses|supersedes|->|\u2192)\s*:?\s*([^\n]*)", re.I)
IDTOK = re.compile(r"(?<![A-Za-z0-9])" + ID)   # left boundary: don't match T-/DS- inside words (CONTRACT-9, HOST-1)
def read(p):
    try: return p.read_text(encoding="utf-8")
    except Exception: return ""
def_of, defines, refs = {}, {}, {}
for p in SPEC.rglob("*.md"):
    r = p.relative_to(SPEC).as_posix(); defines.setdefault(r, set()); refs.setdefault(r, set())
    if p.name == "traceability.md": continue   # consulted separately for code mapping; its rows reference IDs, never define them
    for l in read(p).splitlines():
        m = DEF1.match(l)
        selfid = m.group(1) if m else None
        if selfid: def_of.setdefault(selfid, r); defines[r].add(selfid)
        for m2 in DEF2.finditer(l): def_of.setdefault(m2.group(1), r); defines[r].add(m2.group(1))
        for mk in REFMARK.finditer(l):
            for tok in IDTOK.findall(mk.group(1)):
                if tok != selfid: refs[r].add(tok)
refby = {}
for f, ids in refs.items():
    for i in ids: refby.setdefault(i, set()).add(f)
args = sys.argv[1:]
if args[:1] == ["--area"] and len(args) > 1:
    seeds = [i for f, ids in defines.items() if f.startswith(args[1]) for i in ids]
elif args[:1] == ["--since"] and len(args) > 1:
    # self-detection: ask git what changed under spec/ since <ref>, harvest IDs from changed lines
    try:
        diff = subprocess.run(["git", "diff", "--unified=0", args[1], "--", "spec/"],
                              capture_output=True, text=True).stdout
        untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard", "--", "spec/"],
                              capture_output=True, text=True).stdout.split()
    except Exception as ex:
        print("git diff failed:", ex); sys.exit(2)
    seeds = []
    for l in diff.splitlines():
        if l.startswith(("+", "-")) and not l.startswith(("+++", "---")):
            seeds += IDTOK.findall(l)
    for fn in untracked:                       # new files not yet staged: treat all their IDs as new
        seeds += IDTOK.findall(read(pathlib.Path(fn)))
    seeds = sorted(set(seeds))
    if not seeds: print("no spec IDs changed since", args[1], "(nothing to propagate)"); sys.exit(0)
else:
    seeds = args
if not seeds: print("usage: impact.py ID [ID ...]  |  --area <folder-prefix>  |  --since <gitref>"); sys.exit(2)
impacted_files, impacted_ids, frontier = set(), set(), list(seeds)
while frontier:
    i = frontier.pop()
    if i in impacted_ids: continue
    impacted_ids.add(i)
    if i in def_of: impacted_files.add(def_of[i])
    for f in refby.get(i, ()):
        impacted_files.add(f)
        for j in defines.get(f, ()):
            if j not in impacted_ids: frontier.append(j)
code = set()
tp = SPEC / "10-delivery" / "verification" / "traceability.md"
if tp.exists():
    for l in read(tp).splitlines():
        if not l.strip().startswith("|"): continue
        if set(IDTOK.findall(l)) & impacted_ids:
            for m in re.findall(r"[\w./-]+\.(?:py|ts|tsx|js|jsx|go|java|rb|rs|cs|kt|sql)", l): code.add(m)
def layer(r):
    if r.startswith("04-domain/ddd"): return 1
    if r.startswith("05-functional-spec") or r.startswith("06-requirements/"): return 2
    if r.startswith("11-commercial/"): return 2
    if r.startswith("09-solution/"): return 3
    if r.startswith("10-delivery/"): return 4
    if r.startswith("12-operate"): return 4
    return 0   # foundation (01-discovery, 02-product, 03-constraints/system-context) — upstream of ddd
tasks = sorted(i for i in impacted_ids if i.startswith("T-"))
print("CHANGED (seeds):", ", ".join(sorted(set(seeds))))
print("\nIMPACTED SPEC FILES (re-derive / re-review, upstream -> downstream):")
for r in sorted(impacted_files, key=lambda x: (layer(x), x)): print("  L%d  %s" % (layer(r), r))
print("\nIMPACTED TASKS (re-finalize / re-implement):", ", ".join(tasks) or "none")
print("IMPACTED CODE (re-implement + re-test):", ", ".join(sorted(code)) or "none (no traceability yet)")
print("\n%d spec file(s), %d task(s), %d code file(s) impacted." % (len(impacted_files), len(tasks), len(code)))
