#!/usr/bin/env python3
# spec-lint - deterministic consistency checks over spec/. Stdlib only.
# ERROR = hard violation (exit 1). WARN = heuristic candidate. INFO = delegated to the conductor.
# Run from the project root:  python3 tools/lint_spec.py [spec_dir]
import os, re, sys, pathlib

SPEC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "spec")
if not SPEC.exists():
    print("no spec/ dir at", SPEC); sys.exit(2)

# Mirrors repo-layout.md (machine copy): folders that may directly hold content, at any depth.
LEAF_DIRS = ["01-discovery","02-product/vision","02-product/customers","02-product/market","02-product/goals","03-constraints","03-system-context",
    "04-domain/ddd","05-requirements/functional","05-requirements/quality","05-requirements/data",
    "05-requirements/integration","05-requirements/security","05-requirements/ux","05-requirements/design-system","05-requirements/compliance","05-requirements/ml",
    "06-commercial","07-gtm","08-growth",
    "09-solution/arch","09-solution/data","09-solution/api","09-solution/security","09-solution/infra-ops",
    "09-solution/observability","09-solution/test","09-solution/impl","09-solution/ml",
    "10-delivery/conventions","10-delivery/tasks","10-delivery/verification","10-delivery/operations"]
# Per-area deliverables: glossary.md / actors.md may appear in ANY area folder (no shared root singletons).
AREA_FILES = ["glossary.md", "actors.md"]
AREA_DIR = {"problem-validation":"01-discovery","product-vision":"02-product/vision",
    "customer-discovery":"02-product/customers","market":"02-product/market","goals":"02-product/goals","constraints":"03-constraints","system-context":"03-system-context",
    "ddd":"04-domain/ddd","derive-functional":"05-requirements/functional","quality":"05-requirements/quality",
    "data-reqs":"05-requirements/data","integration-reqs":"05-requirements/integration",
    "security-reqs":"05-requirements/security","ux-reqs":"05-requirements/ux","design-system":"05-requirements/design-system","compliance":"05-requirements/compliance","ml-reqs":"05-requirements/ml",
    "monetization":"06-commercial","go-to-market":"07-gtm","growth":"08-growth",
    "derive-architecture":"09-solution/arch","derive-data-architecture":"09-solution/data",
    "derive-api-contracts":"09-solution/api","derive-security-architecture":"09-solution/security",
    "derive-infra-ops":"09-solution/infra-ops","derive-observability":"09-solution/observability",
    "derive-test-strategy":"09-solution/test","derive-impl-design":"09-solution/impl","derive-ml-architecture":"09-solution/ml",
    "derive-conventions":"10-delivery/conventions","derive-tasks":"10-delivery/tasks",
    "conformance-review":"10-delivery/verification"}
# Which ID-prefixes are DEFINED in which directory (enforces stage purity / no-unrelated-content).
PREFIX_OWNER = {"UC":"05-requirements/functional","AC":"05-requirements/functional",
    "CMD":"04-domain/ddd","EVT":"04-domain/ddd","AGG":"04-domain/ddd",
    "NFR":"05-requirements/quality","ASR":"05-requirements/quality","DATA":"05-requirements/data",
    "SEC":"05-requirements/security","OBL":"05-requirements/compliance","API":"09-solution/api",
    "SLO":"09-solution/observability","EXP":"08-growth","T":"10-delivery/tasks","DS":"05-requirements/design-system"}
def file_layer(r):
    if r.startswith("04-domain/ddd"): return 1
    if r.startswith("05-requirements/"): return 2
    if r.startswith("06-commercial"): return 2
    if r.startswith("08-growth"): return 2
    if r.startswith("09-solution/"): return 3
    if r.startswith("10-delivery/"): return 4
    return 0  # constraints, 02-product/*, discovery, singletons
ID_LAYER = {"CMD":1,"EVT":1,"AGG":1,"UC":2,"AC":2,"NFR":2,"ASR":2,"SEC":2,"DATA":2,"OBL":2,"EXP":2,"DS":2,"API":3,"SLO":3,"T":4,"ADR":0}
def id_layer(tok): return ID_LAYER.get(tok.split("-")[0].upper(), 0)
PROSE_WORDS = 40

F = []
def add(sev, path, msg, line=0): F.append((sev, str(path), line, msg))
def read(p):
    try: return p.read_text(encoding="utf-8")
    except Exception: return ""
rel = lambda p: p.relative_to(SPEC).as_posix()
allfiles = [p for p in SPEC.rglob("*") if p.is_file()]
def cmd_files():
    for p in allfiles:
        r = rel(p)
        if r.endswith(".md") and os.path.basename(r) != ".gitkeep": yield p, r
def under_leaf(r): return any(r == d or r.startswith(d + "/") for d in LEAF_DIRS)

# 1 closed world
def allowed(r):
    if os.path.basename(r) == ".gitkeep": return True
    if os.path.basename(r) in AREA_FILES: return True            # per-area glossary/actors, any folder
    if r.endswith(".md") and (r.startswith("adr/") or "/adr/" in r): return True  # the shared ADR folder
    return under_leaf(r)
for p in allfiles:
    r = rel(p)
    if not allowed(r):
        add("ERROR", r, "file outside the defined structure (not a leaf file, a glossary/actors, or an ADR in adr/) - relocate it")

# (glossary/actors are per-area deliverables now; no shared-singleton uniqueness check)

# 2b ADR filename format: ADR-<PREFIX>-NNN.md (PREFIX = area code -> no two skills collide)
ADRNAME = re.compile(r"^ADR-[A-Z][A-Z0-9]*-\d+(?:-[a-z0-9-]+)?\.md$")
for p in allfiles:
    r = rel(p)
    if not (r.endswith(".md") and (r.startswith("adr/") or "/adr/" in r)): continue
    b = os.path.basename(r)
    if b == "template.md" or "_archive/" in r: continue
    if not ADRNAME.match(b):
        add("ERROR", r, "ADR filename must be ADR-<PREFIX>-NNN.md (PREFIX = your area code, e.g. ADR-DDD-007)")

# 3 file-header contract (adr/* use the ADR format instead)
HDR = re.compile(r"<!--\s*scope:(.*?)\|\s*excludes:(.*?)\|\s*format:(.*?)-->", re.S | re.I)
for p, r in cmd_files():
    if r.startswith("adr/") or "/adr/" in r: continue
    txt = read(p)
    if txt.strip() == "": continue
    m = HDR.search("\n".join(txt.splitlines()[:6]))
    if not m:
        add("ERROR", r, "missing file header  <!-- scope: ... | excludes: ... | format: ... -->")
    else:
        for k, v in zip(("scope", "excludes", "format"), m.groups()):
            if v.strip() == "": add("ERROR", r, "file header '" + k + "' is empty")
            elif "\u2026" in v: add("WARN", r, "file header '" + k + "' looks unfilled")

# 4 placeholder / stale tokens (template.md may keep them)
TOK = re.compile(r"\{\{|\}\}|\bTODO\b|\bTKTK\b|\bFIXME\b|\bNNNN\b")
for p, r in cmd_files():
    if os.path.basename(r) == "template.md" and "adr/" in r: continue
    if "NNNN" in os.path.basename(r):
        add("ERROR", r, "unfilled ADR filename (NNNN) - use the real number")
    for i, l in enumerate(read(p).splitlines(), 1):
        if TOK.search(l): add("ERROR", r, "placeholder/stale token: " + l.strip()[:60], i)

# 5 dangling local links
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
for p, r in cmd_files():
    for i, l in enumerate(read(p).splitlines(), 1):
        for t in LINK.findall(l):
            t = t.split("#")[0].strip()
            if not t or t.startswith(("http://", "https://", "mailto:")): continue
            if not (p.parent / t).exists() and not (SPEC / t).exists():
                add("ERROR", r, "dangling link -> " + t, i)

# 6/7 (removed) — assumptions and open points are no longer side-ledger files. They live INLINE
#   in each artifact: an assumption carries its status (Untested/Testing/Validated/Invalidated/
#   Accepted-risk) beside what it supports; a Deferred point carries its revisit trigger. The
#   authoring model + the grilling lenses enforce this, not a file check.

# 8 readiness vs reality
def ccount(d):
    base = SPEC / d
    if not base.exists(): return 0
    return sum(1 for q in base.rglob("*") if q.is_file() and q.name != ".gitkeep" and read(q).strip())
rd = SPEC / "_readiness.md"
if rd.exists():
    AL = re.compile(r"\*\*([a-z0-9-]+)\*\*\s*[-\u2014]+\s*([a-z\- ()0-9]+)", re.I)
    for i, l in enumerate(read(rd).splitlines(), 1):
        m = AL.search(l)
        if not m: continue
        area = m.group(1).lower(); st = m.group(2).lower()
        d = AREA_DIR.get(area)
        if not d: continue
        c = ccount(d)
        if "done" in st and c == 0: add("WARN", "_readiness.md", "'" + area + "' marked done but its folder is empty", i)
        if "not-started" in st and c > 0: add("WARN", "_readiness.md", "'" + area + "' has content but is marked not-started", i)

# 9 gate order
if any(ccount(d) > 0 for d in LEAF_DIRS if d.startswith("09-solution/")):
    empty = [d for d in LEAF_DIRS if d.startswith("05-requirements/") and ccount(d) == 0]
    if empty:
        add("WARN", "(gate)", "09-solution/* has content but requirements incomplete (" + ", ".join(empty) + ") - architecture-readiness gate not met")

# 10 prose heuristic - flag prose BLOCKS (consecutive long non-structural lines), not a lone clarifying sentence
def struct(l):
    s = l.strip()
    return s == "" or s.startswith(("#", "-", "*", ">", "|", "<!--", "```", "<", "_")) or bool(re.match(r"\d+\.", s))
for p, r in cmd_files():
    if not under_leaf(r): continue
    lines = read(p).splitlines()
    longp = [k for k, l in enumerate(lines) if not struct(l) and len(l.split()) > PROSE_WORDS]
    lset = set(longp)
    for k in longp:
        if (k-1) in lset or (k+1) in lset or len(lines[k].split()) > 2*PROSE_WORDS:
            add("WARN", r, "dense prose block (consecutive >%d-word lines) - lead with structure; a lone clarifying sentence is fine" % PROSE_WORDS, k+1)

# 11 stable-ID references resolve (the traceability spine)
ID = r"(?:UC|AC|CMD|EVT|AGG|NFR|ASR|API|SEC|DATA|OBL|SLO|EXP|DS|T|ADR)-[A-Za-z0-9._-]*[A-Za-z0-9]"
defined = set()
defsites = {}                                                # id -> set of files that define it
DEF1 = re.compile(r"^\s*[-*#]*\s*\|?\s*\**(" + ID + r")\b")          # ID as first token of a line/cell (after any leading -, *, #, |, or bold marker)
DEF2 = re.compile(r"\bid:\s*(" + ID + r")\b", re.I)          # id: <ID>
for p, r in cmd_files():
    if os.path.basename(r) == "traceability.md": continue   # the traceability matrix references IDs (ID->task->code); it never defines them
    for l in read(p).splitlines():
        m = DEF1.match(l)
        if m: defined.add(m.group(1)); defsites.setdefault(m.group(1), set()).add(r)
        for m in DEF2.finditer(l): defined.add(m.group(1)); defsites.setdefault(m.group(1), set()).add(r)
# ADR ids also defined by their file in adr/ (prefixed ADR-<PREFIX>-NNN)
for p in allfiles:
    b = os.path.basename(rel(p))
    m = re.match(r"(ADR-[A-Za-z][A-Za-z0-9]*-\d+)", b)
    if (rel(p).startswith("adr/") or "/adr/" in rel(p)) and m: defined.add(m.group(1).upper())
REFMARK = re.compile(r"(?:implements?|depends(?:-on)?|refs?|references?|see|satisf(?:y|ies|ied-by)|covers?|covered-by|maps?-?to|reali[sz]es?|traces?-?to|verif(?:y|ies)|validates?|addresses|supersedes|->|\u2192)\s*:?\s*([^\n]*)", re.I)
IDTOK = re.compile(ID)
refset = set()                                               # every ID referenced anywhere
for p, r in cmd_files():
    for i, l in enumerate(read(p).splitlines(), 1):
        m = DEF1.match(l)
        selfid = m.group(1) if m else None      # the ID this row defines - don't count it as a self-reference
        for mk in REFMARK.finditer(l):
            for tok in IDTOK.findall(mk.group(1)):
                if tok == selfid: continue
                refset.add(tok)
                if tok not in defined:
                    add("ERROR", r, "reference to undefined ID '" + tok + "'", i)
                if tok.split("-")[0].upper() != "ADR" and id_layer(tok) > file_layer(r):
                    add("ERROR", r, "illegal downward reference: L%d file -> %s (L%d); references must be upstream-only" % (file_layer(r), tok, id_layer(tok)), i)

# 12 no duplicate ID definition (an ID is defined in exactly one place)
for tok, files in defsites.items():
    if len(files) > 1:
        add("ERROR", sorted(files)[0], "ID '" + tok + "' defined in multiple files (" + ", ".join(sorted(files)) + ") - define once, reference elsewhere")

# 13 per-directory scope: each tracked ID-type is DEFINED only under its owning directory
#    (mechanical stage-purity / no-unrelated-content)
for tok, files in defsites.items():
    pre = tok.split("-")[0].upper()
    owner = PREFIX_OWNER.get(pre)
    if not owner: continue
    for r in files:
        if not (r == owner or r.startswith(owner + "/")):
            add("ERROR", r, "%s defined outside its owning area '%s/' (found in %s) - wrong directory for this content" % (tok, owner, r))

# 14 structural coverage = the GAP-DETECTION surface (WARN: every X should have its downstream Y)
COV_HINT = {"CMD":"expected a use-case (UC-) projecting it","EVT":"no downstream consumer",
    "AGG":"expected persistence (DATA-) / a use-case","UC":"expected acceptance criteria (AC-) or a task",
    "AC":"not exercised by any test/task","OBL":"no control (SEC-/DATA-/arch) addresses it",
    "SLO":"no alert/runbook references it","NFR":"no test/SLO evidences it","ASR":"no verifying test",
    "API":"no consumer/test","EXP":"no analytics event/task wires it","DATA":"no consumer"}
trace_ids = set()
_tp = SPEC / "10-delivery" / "verification" / "traceability.md"
if _tp.exists():
    for l in read(_tp).splitlines():
        trace_ids |= set(IDTOK.findall(l))
# a parent with a keyed child is covered by it (UC-014 by AC-014a; NFR-014 by ASR-014) even with no explicit ref
keyed_parents = set()
for d in defined:
    pp = d.split("-")[0].upper()
    if pp == "AC":
        mk = re.match(r"^AC-(\d+)[a-z]+$", d)
        if mk: keyed_parents.add("UC-" + mk.group(1))
    elif pp == "ASR":
        mk = re.match(r"^ASR-(.+)$", d)
        if mk: keyed_parents.add("NFR-" + mk.group(1))
for tok in sorted(defined):
    pre = tok.split("-")[0].upper()
    if pre not in COV_HINT: continue
    if tok in refset or tok in trace_ids or tok in keyed_parents: continue
    add("WARN", sorted(defsites.get(tok, ["(?)"]))[0],
        "coverage: '" + tok + "' has no downstream reference - " + COV_HINT[pre] + " (structural gap to resolve or mark N/A)")



add("INFO", "(semantic)", "ID references are now checked; event->consumer logic and entitlement->feature *meaning* remain semantic - the conductor judges those")

# 15 no task ships with an unresolved gap (the last-responsible-moment forcing checkpoint, enforced)
for p, r in cmd_files():
    if not r.startswith("10-delivery/tasks/") or r.split("/")[-1] == "build-order.md": continue
    for i, l in enumerate(read(p).splitlines(), 1):
        if re.search(r"\bGAP\b", l) and re.search(r"\bUNRESOLVED\b", l, re.I):
            add("ERROR", r, "unresolved GAP in task - complete it (upstream), mark N/A, or accept (ADR) before it can be implemented", i)

# 16 correlated child->parent traceability: a child ID carries its parent's number; the parent must exist
#    (AC keys to its use-case; ASR keys to its NFR) - enforces the mapping, no orphan or flat children
CHILD_PARENT = [
    ("AC",  "UC",  r"^AC-(\d+)[a-z]+$",  "use-case", "AC-<ucnum><letter> (e.g. UC-014 -> AC-014a, AC-014b)"),
    ("ASR", "NFR", r"^ASR-(.+)$",          "NFR",      "ASR-<nfr-suffix>, matching its NFR (NFR-014 -> ASR-014; NFR-REL-2 -> ASR-REL-2)"),
]
for cpre, ppre, keyed, pname, conv in CHILD_PARENT:
    for cid in sorted(d for d in defined if d.split("-")[0].upper() == cpre):
        loc = sorted(defsites.get(cid, ["(?)"]))[0]
        m = re.match(keyed, cid)
        if m:
            parent = ppre + "-" + m.group(1)
            if parent not in defined:
                add("ERROR", loc, cid + " keys to " + parent + ", which is not defined - every " + cpre + " must map to a real " + pname + " (" + ppre + ")")
        else:
            add("ERROR", loc, cid + " is not keyed to a " + pname + " - use " + conv)

# 17 an obsolete ADR (in _archive/, or status superseded/deprecated) must not be referenced as live
superseded = set()
for p, r in cmd_files():
    if not (r.startswith("adr/") or "/adr/" in r): continue
    mnum = re.match(r"(ADR-[A-Za-z][A-Za-z0-9]*-\d+)", r.split("/")[-1])
    if not mnum: continue
    adr = mnum.group(1).upper()
    if (r.startswith("adr/_archive/") or "/adr/_archive/" in r) or re.search(r"(?im)^[\s>*#-]*\**\s*status\**\s*:?\s*\**\s*(?:superseded|deprecated)", read(p)):
        superseded.add(adr)
if superseded:
    LIVE = re.compile(r"\b(?:implements|depends-on|satisfies|refs|see|covers|maps-to|realizes|realises|traces-to|verifies|validates|addresses)\b[^\n]*?(ADR-[A-Za-z]+-\d+)", re.I)
    for p, r in cmd_files():
        if r.startswith("adr/") or "/adr/" in r: continue
        for i, l in enumerate(read(p).splitlines(), 1):
            for mm in LIVE.finditer(l):
                if mm.group(1) in superseded:
                    add("WARN", r, "references obsolete " + mm.group(1) + " (superseded/deprecated) as live - point to its replacement", i)

# 18 every afk:blocked task has a human-input entry (so the handoff is not lost)
_hin = SPEC / "_human-input.md"
_htxt = read(_hin) if _hin.exists() else ""
for p, r in cmd_files():
    if not r.startswith("10-delivery/tasks/") or r.split("/")[-1] == "build-order.md": continue
    if re.search(r"afk:\s*blocked", read(p), re.I):
        for tid in [d for d in defined if d.split("-")[0].upper() == "T" and r in defsites.get(d, set())]:
            if tid not in _htxt:
                add("WARN", r, tid + " is afk:blocked but absent from _human-input.md - queue the human ask so the handoff is not lost")

order = {"ERROR": 0, "WARN": 1, "INFO": 2}
F.sort(key=lambda x: (order[x[0]], x[1], x[2]))
e = sum(1 for x in F if x[0] == "ERROR"); wn = sum(1 for x in F if x[0] == "WARN")
for sev, path, line, msg in F:
    loc = (path + ":" + str(line)) if line else path
    print("%-5s %-44s %s" % (sev, loc, msg))
print("\n%d error(s), %d warning(s)." % (e, wn))
sys.exit(1 if e else 0)
