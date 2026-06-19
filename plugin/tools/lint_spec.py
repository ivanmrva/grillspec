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
    "04-domain/ddd","05-functional-spec","06-requirements/quality","06-requirements/data",
    "06-requirements/integration","06-requirements/security","06-requirements/ux","06-requirements/design-system","06-requirements/compliance","06-requirements/ml","06-requirements/entitlements",
    "09-commercial/monetization","09-commercial/go-to-market","09-commercial/growth",
    "07-solution/arch","07-solution/data","07-solution/api","07-solution/security","07-solution/infra-ops",
    "07-solution/observability","07-solution/test","07-solution/impl","07-solution/ml",
    "08-delivery/conventions","08-delivery/tasks","08-delivery/verification","10-operate"]
# Per-area deliverables: glossary.md / actors.md may appear in ANY area folder (no shared root singletons).
AREA_FILES = ["glossary.md", "actors.md"]
AREA_DIR = {"problem-validation":"01-discovery","product-vision":"02-product/vision",
    "customer-discovery":"02-product/customers","market":"02-product/market","goals":"02-product/goals","constraints":"03-constraints","system-context":"03-system-context",
    "ddd":"04-domain/ddd","derive-functional":"05-functional-spec","quality":"06-requirements/quality",
    "data-reqs":"06-requirements/data","integration-reqs":"06-requirements/integration",
    "security-reqs":"06-requirements/security","ux-reqs":"06-requirements/ux","design-system":"06-requirements/design-system","compliance":"06-requirements/compliance","ml-reqs":"06-requirements/ml","entitlements":"06-requirements/entitlements",
    "monetization":"09-commercial/monetization","go-to-market":"09-commercial/go-to-market","growth":"09-commercial/growth",
    "derive-architecture":"07-solution/arch","derive-data-architecture":"07-solution/data",
    "derive-api-contracts":"07-solution/api","derive-security-architecture":"07-solution/security",
    "derive-infra-ops":"07-solution/infra-ops","derive-observability":"07-solution/observability",
    "derive-test-strategy":"07-solution/test","derive-impl-design":"07-solution/impl","derive-ml-architecture":"07-solution/ml",
    "derive-conventions":"08-delivery/conventions","derive-tasks":"08-delivery/tasks",
    "conformance-review":"08-delivery/verification"}
# Which ID-prefixes are DEFINED in which directory (enforces stage purity / no-unrelated-content).
# The type-prefix set here is the SINGLE source of truth; selfcheck.py diffs it against the prefixes
# the skills declare, so adding a prefix to a skill without registering it here is caught.
PREFIX_OWNER = {"UC":"05-functional-spec","AC":"05-functional-spec",
    "CMD":"04-domain/ddd","EVT":"04-domain/ddd","AGG":"04-domain/ddd",
    "VO":"04-domain/ddd","HOT":"04-domain/ddd","POL":"04-domain/ddd","RM":"04-domain/ddd","ENT":"04-domain/ddd",
    "NFR":"06-requirements/quality","ASR":"06-requirements/quality","DATA":"06-requirements/data",
    "SEC":"06-requirements/security","THR":"06-requirements/security","OBL":"06-requirements/compliance","API":"07-solution/api","ML":"06-requirements/ml",
    "ENTL":"06-requirements/entitlements",
    "SLO":"07-solution/observability","EXP":"09-commercial/growth","T":"08-delivery/tasks","DS":"06-requirements/design-system"}
def file_layer(r):
    if r.startswith("04-domain/ddd"): return 1
    if r.startswith("05-functional-spec") or r.startswith("06-requirements/"): return 2
    if r.startswith("09-commercial/"): return 2          # monetization · go-to-market · growth (post-launch sinks)
    if r.startswith("07-solution/"): return 3
    if r.startswith("08-delivery/"): return 4
    if r.startswith("10-operate"): return 4
    return 0  # constraints, 02-product/*, discovery, singletons
ID_LAYER = {"CMD":1,"EVT":1,"AGG":1,"VO":1,"HOT":1,"POL":1,"RM":1,"ENT":1,"UC":2,"AC":2,"NFR":2,"ASR":2,"SEC":2,"THR":2,"DATA":2,"OBL":2,"ENTL":2,"EXP":2,"DS":2,"ML":2,"API":3,"SLO":3,"T":4,"ADR":0}
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
    if "/" not in r and r.startswith("_") and r.endswith(".md"): return True  # spec-root orchestration files (_readiness, _human-input, …) — the conductor writes these
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
if any(ccount(d) > 0 for d in LEAF_DIRS if d.startswith("07-solution/")):
    empty = [d for d in LEAF_DIRS if (d.startswith("05-functional-spec") or d.startswith("06-requirements/")) and ccount(d) == 0]
    if empty:
        add("WARN", "(gate)", "07-solution/* has content but requirements incomplete (" + ", ".join(empty) + ") - architecture-readiness gate not met")

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
# TYPES = the SINGLE source of truth for type-prefixes (selfcheck.py reads this line to detect drift
#         against the prefixes the skills declare). Keep it one flat alternation on one line.
TYPES = "UC|AC|CMD|EVT|AGG|VO|HOT|POL|RM|ENTL|ENT|NFR|ASR|API|SEC|THR|DATA|OBL|SLO|EXP|DS|ML|ADR|T"
# IDCORE = the type-prefixed token, no boundary (used in ANCHORED definition matches).
# ID = IDCORE behind a left boundary that also excludes '-' so a known prefix is NOT mined out of a
#      longer token: 'HOT-005' no longer yields 'T-005', 'SUR-AGG-250' no longer yields 'AGG-250'.
IDCORE = r"(?:" + TYPES + r")-[A-Za-z0-9._-]*[A-Za-z0-9]"
ID = r"(?<![A-Za-z0-9-])" + IDCORE
TYPESET = set(TYPES.split("|"))
# Numeric RANGE / LIST shorthand in prose - 'ML-102..109', 'VO-416..421', 'API-002/003' - is a house-style
# abbreviation, NOT an ID. Left intact it tokenizes as a bogus bare ID ('ML-102..109') and false-errors as
# undefined / defined-twice. Stripped from each line before the definition + reference passes. Distinct from
# a real dotted field id ('DATA-Customer.id', single dot, name-suffixed) and a slash-list of FULL ids
# ('T-014/T-015', each prefixed) - both keep their per-id resolution because the middle here is pure digits.
RANGE = re.compile(r"(?<![A-Za-z0-9-])(?:" + TYPES + r")-\d+(?:(?:\.\.|/)\d+)+")
# Reference markers — used to find ID *references* in the resolution pass below. Word markers are
# \b-anchored so they match only as whole words: 'invalidates' must not match 'validates', etc. The
# symbols (->, →) sit outside \b.
REFMARK = re.compile(r"(?:\b(?:implements?|depends(?:-on)?|refs?|references?|see|satisf(?:y|ies|ied-by)|covers?|covered-by|maps?-?to|reali[sz]es?|traces?-?to|verif(?:y|ies)|validates?|addresses|supersedes|surfaces?|renders?|displays?)\b|->|→)\s*:?\s*([^\n]*)", re.I)
defined = set()
defsites = {}                                                # id -> files that AUTHORITATIVELY define it (row-key / heading / id:) — drives define-once + owning-area checks
def3sites = {}                                               # id -> files where it appears inline as '<ID> <Name>' in its OWN area (supplementary; not subject to define-once)
DEF1 = re.compile(r"^\s*[-*#]*\s*\|?\s*\**(" + IDCORE + r")\b")      # ID as first token of a line/cell (after any leading -, *, #, |, or bold marker)
DEF2 = re.compile(r"\bid:\s*(" + IDCORE + r")\b", re.I)      # id: <ID>
# '<ID> <Name>' pair in a list / event-flow / table cell: after line-start or a separator (· ; : , | → ⟵),
# skipping bold/backtick markup, an ID followed by its PascalCase name. The SAME surface form is used both
# to DEFINE (ddd's nested 'commands: CMD-201 ExtractAtoms · CMD-204 ReExtract') and to REFERENCE (a
# use-case listing the commands it projects). Disambiguate STRUCTURALLY by owning area, NOT by refmark
# presence: it is a definition only inside the id-type's PREFIX_OWNER folder; anywhere else it's a
# reference (left to the resolution pass). It registers as supplementary (def3sites) so the same id in
# two files of its own area — an aggregate block and the event-flow — is not a 'defined twice' error.
DEF3 = re.compile(r"(?:^|[·;:,|←→⟵⟶])\s*[*`_]*\s*(" + IDCORE + r")\s+[A-Z]")
# A markdown table SEPARATOR row (the |---|:--:|---| under a header). Cells are dashes-only (≥2, optional
# alignment colons); used to detect — and skip — the HEADER row above it, whose first cell is a column
# LABEL ('OBL-id', 'DS-id', 'NFR-evidence'), not an ID definition. Real ids are defined in body rows.
SEP = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
def in_owner_area(tok, r):
    owner = PREFIX_OWNER.get(tok.split("-")[0].upper())
    return bool(owner) and (r == owner or r.startswith(owner + "/"))
for p, r in cmd_files():
    if os.path.basename(r) == "traceability.md": continue   # the traceability matrix references IDs (ID->task->code); it never defines them
    lines = read(p).splitlines()
    for i, l in enumerate(lines):
        if "|" in l and i+1 < len(lines) and SEP.match(lines[i+1]):
            continue                                         # table HEADER row — first cell is a column label, not an ID definition
        l = RANGE.sub(" ", l)                                # drop numeric range/list shorthand before tokenizing
        m = DEF1.match(l)
        if m: defined.add(m.group(1)); defsites.setdefault(m.group(1), set()).add(r)
        for m in DEF2.finditer(l): defined.add(m.group(1)); defsites.setdefault(m.group(1), set()).add(r)
        for m in DEF3.finditer(l):                           # inline '<ID> <Name>' is a definition ONLY in the id's owning area; elsewhere it's a reference
            if in_owner_area(m.group(1), r):
                defined.add(m.group(1)); def3sites.setdefault(m.group(1), set()).add(r)
# ADR ids also defined by their file in adr/ (prefixed ADR-<PREFIX>-NNN)
for p in allfiles:
    b = os.path.basename(rel(p))
    m = re.match(r"(ADR-[A-Za-z][A-Za-z0-9]*-\d+)", b)
    if (rel(p).startswith("adr/") or "/adr/" in rel(p)) and m: defined.add(m.group(1).upper())
IDTOK = re.compile(ID)
def is_adr_file(r): return r.startswith("adr/") or "/adr/" in r
refset = set()                                               # every ID referenced anywhere
# Robust to a legitimately-PARTIAL spec (derived/downstream areas deleted to review the grilled core): a
# reference whose owning AREA is entirely absent (no files present) is an artifact of that missing area, not a
# real dangling/illegal ref. ABSENT_TYPES = the id-types whose owning directory holds no content right now;
# refs to them are suppressed (undefined + downward-ref), mirroring the coverage-WARN 'downstream layer empty'
# suppression. A typo inside a PRESENT area still errors (its dir has files); a FULL spec has no absent areas,
# so behaviour there is unchanged. Reported once as an INFO so the suppression is never silent.
ABSENT_TYPES = {pre for pre, owner in PREFIX_OWNER.items() if ccount(owner) == 0}
absent_refs = set()
def note_ref(tok, r, i, selfid):
    if tok == selfid: return
    refset.add(tok)
    if tok.split("-")[0].upper() in ABSENT_TYPES:            # owning area not present in this (partial) spec
        absent_refs.add(tok); return
    if tok not in defined:
        add("ERROR", r, "reference to undefined ID '" + tok + "'", i)
    # (the illegal-downward-reference check is NOT here — it runs comprehensively over every id token below,
    #  not only reference-detected ones, so a downward id in plain prose can't evade the upstream-only invariant.)
for p, r in cmd_files():
    for i, l in enumerate(read(p).splitlines(), 1):
        l = RANGE.sub(" ", l)                                # drop numeric range/list shorthand before tokenizing
        m = DEF1.match(l)
        selfid = m.group(1) if m else None      # the ID this row defines - don't count it as a self-reference
        for mk in REFMARK.finditer(l):
            for tok in IDTOK.findall(mk.group(1)):
                note_ref(tok, r, i, selfid)
        # an inline '<ID> <Name>' OUTSIDE its owning area is a REFERENCE (a use-case listing the commands
        # it projects, a security rule naming a command). In its own area it's a definition (handled above).
        for m in DEF3.finditer(l):
            if not in_owner_area(m.group(1), r):
                note_ref(m.group(1), r, i, selfid)
# 11b illegal-downward-reference — enforced over EVERY id token, not only reference-detected ones, so a
# downward id sitting in plain prose (no refmark/arrow) can't evade the upstream-only invariant. High
# precision: every hit is a real downward occurrence (a definition / same-layer mention has id_layer ==
# file_layer, never > , so it never fires). Exemptions mirror the reference checks: ADR source files (cite
# their drivers downward by design), traceability.md (the cross-layer trace spine), and the JIT impl area
# (derive-impl-design names the task it elaborates — the one acknowledged layer wrinkle). Skip fenced code +
# the scope header; an id in an absent area (partial spec) is suppressed like the undefined check.
dn_seen = set()
for p, r in cmd_files():
    if is_adr_file(r) or os.path.basename(r) == "traceability.md" or r.startswith("07-solution/impl") or ("/" not in r and r.startswith("_")): continue   # last: spec-root orchestration dashboards (_readiness/_human-input) span all layers by design
    fl = file_layer(r); fence = False
    for i, l in enumerate(read(p).splitlines(), 1):
        s = l.lstrip()
        if s.startswith("```"): fence = not fence; continue
        if fence or s.startswith("<!--"): continue
        for tok in IDTOK.findall(RANGE.sub(" ", l)):
            pre = tok.split("-")[0].upper()
            if pre == "ADR" or pre in ABSENT_TYPES: continue
            if id_layer(tok) > fl and (r, tok) not in dn_seen:
                dn_seen.add((r, tok))
                add("ERROR", r, "illegal downward reference: L%d file -> %s (L%d); references must be upstream-only (the invariant covers every mention, not just marked references)" % (fl, tok, id_layer(tok)), i)
if absent_refs:
    shown = ", ".join(sorted(absent_refs)[:10]) + (" …" if len(absent_refs) > 10 else "")
    add("INFO", "(partial)", "%d reference(s) to areas not present in this spec were not error-checked (partial spec — derived/downstream areas absent): %s" % (len(absent_refs), shown))

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

# 13b context-namespaced IDs are banned: an ID must lead with a BARE type prefix (AGG-NNN), never
#     <CTX>-AGG-NNN. A namespaced token doesn't register as a definition but its bare suffix may be
#     referenced elsewhere -> phantom 'undefined'. Flag it honestly instead of letting it go silent.
NS = re.compile(r"(?<![A-Za-z0-9-])([A-Za-z][A-Za-z0-9]*)-(" + TYPES + r")-[A-Za-z0-9._-]*[A-Za-z0-9]")
TYPESET = set(TYPES.split("|"))
for p, r in cmd_files():
    if os.path.basename(r) == "traceability.md": continue
    for i, l in enumerate(read(p).splitlines(), 1):
        for m in NS.finditer(l):
            if m.group(1).upper() in TYPESET: continue   # e.g. AC-014a's own 'AC' lead — already a real ID
            add("ERROR", r, "context-namespaced ID '" + m.group(0) + "' - IDs must lead with a bare type prefix (" + m.group(2) + "-NNN, never " + m.group(1) + "-" + m.group(2) + "-NNN); namespace inside the suffix or use disjoint numeric bands for parallel work", i)

# 13c an ID that sits only in a NON-LEADING table cell never registers as a definition (DEF1 keys on the
#     leading cell) -> downstream refs to it read as 'undefined'. Nudge toward the convention: ID = row key.
CELLID = re.compile(r"^(?:[*`]*)(" + IDCORE + r")(?:[*`]*)$")
for p, r in cmd_files():
    if os.path.basename(r) == "traceability.md": continue
    for i, l in enumerate(read(p).splitlines(), 1):
        s = l.strip()
        if not (s.startswith("|") and s.count("|") >= 2): continue          # a table row
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells or not cells[0] or CELLID.match(cells[0]): continue    # leading cell empty or already an ID -> fine
        for c in cells[1:]:
            m = CELLID.match(c)
            if m and m.group(1) not in defined:
                add("WARN", r, "ID '" + m.group(1) + "' sits in a non-leading table cell and is defined nowhere as a row key - define an ID in the LEADING column (the row key) so it registers", i)
                break

# 14 structural coverage = the GAP-DETECTION surface (WARN: every X should have its downstream Y)
COV_HINT = {"CMD":"expected a use-case (UC-) projecting it","EVT":"no downstream consumer",
    "AGG":"expected persistence (DATA-) / a use-case","RM":"expected a view use-case (UC-) surfacing it, or N/A for an internal projection","UC":"expected acceptance criteria (AC-) or a task",
    "AC":"not exercised by any test/task","OBL":"no control (SEC-/DATA-/arch) addresses it",
    "SLO":"no alert/runbook references it","NFR":"no test/SLO evidences it","ASR":"no verifying test",
    "API":"no consumer/test","EXP":"no analytics event/task wires it","DATA":"no consumer"}
trace_ids = set()
_tp = SPEC / "08-delivery" / "verification" / "traceability.md"
if _tp.exists():
    for l in read(_tp).splitlines():
        trace_ids |= set(IDTOK.findall(l))
# downstream type a coverage WARN expects; if NONE of that type exists yet, the downstream layer is
# simply empty (early stage) and the WARN is noise, not a gap — suppress it. (#7: a CMD has no UC only
# once use-cases exist; before then "CMD has no UC" is 100% expected and drowns real within-layer gaps.)
DOWN_TYPE = {"CMD":("UC",),"EVT":("UC",),"AGG":("DATA",),"RM":("UC",),"UC":("AC",),"AC":("T",),
    "OBL":("SEC","DATA"),"NFR":("ASR","SLO"),"ASR":("T",),"API":("T",),"EXP":("T",)}
present_types = {d.split("-")[0].upper() for d in defined}
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
    dts = DOWN_TYPE.get(pre)
    if dts and not any(t in present_types for t in dts): continue   # downstream layer empty - premature to warn
    if tok in refset or tok in trace_ids or tok in keyed_parents: continue
    add("WARN", sorted(defsites.get(tok) or def3sites.get(tok) or ["(?)"])[0],
        "coverage: '" + tok + "' has no downstream reference - " + COV_HINT[pre] + " (structural gap to resolve or mark N/A)")



add("INFO", "(semantic)", "ID references are now checked; event->consumer logic and entitlement->feature *meaning* remain semantic - the conductor judges those")

# 14b advisory content checks (INFO - the conductor's semantic sweep judges/strips; INFO never fails CI).
# Each flags a CANDIDATE the linter can't decide deterministically without false hits, so it stays advisory.
# (i) DEVTRACE - development-trace / changelog language. The spec is a TIMELESS source of truth: it states the
#     system as it is NOW, with no record of how the document evolved. Only the UNAMBIGUOUS forms are flagged;
#     a bare "New tables" vs. a domain "new booking" is left to the conductor (a regex can't tell them apart).
#     A forward-looking "(deferred until <trigger>)" is legitimate scope - not flagged.
DEVTRACE = [re.compile(p, re.I) for p in [
    r"\bthis (?:round|revision|rewrite|rework|edit) (?:add|remov|introduc|defer|renam|split|merg|mov|chang)\w*",
    r"\bas we (?:discussed|agreed|decided|noted)\b",
    r"\bper our (?:conversation|chat|call|discussion)\b",
    r"\bnewly (?:added|created|introduced|split|renamed|merged|defined)\b",
    r"\((?:formerly\b[^)]*|previously\b[^)]*|was:\s*[^)]*|renamed\b[^)]*|moved\s+from\b[^)]*)\)",
    r"\brenamed from\b", r"\bformerly known as\b", r"\bused to be\b",
]]
# (ii) SELFREF - the spec has no awareness of this system: it must read as standalone project documentation,
#      never naming a skill, engine, tool, or generation step.
SELFREF = re.compile(r"\b(?:grill-[a-z]\w*|(?:derive|exec)-engine|derive-(?:functional|architecture|data-architecture|"
    r"api-contracts|security-architecture|infra-ops|observability|test-strategy|impl-design|ml-architecture|"
    r"conventions|tasks)|lint_spec|guard_derived|selfcheck|plugin_feedback|gen_depgraph|gen_docsite|skill_guide|"
    r"spec_status|impact\.py|re-deriv(?:e|ed|es|ing)|seeded by)\b", re.I)
# (iii) CTXID - a context-namespaced id '<CTX>-TYPE-NNN' silently fails to register while bare references to it
#       resolve. Real ids use a bare type prefix; ADR-<AREA>-NNN is the one legitimate two-segment form (the
#       lead segment is the ADR type), so a lead segment that IS a known type is skipped.
CTXID = re.compile(r"(?<![A-Za-z0-9-])([A-Z][A-Za-z0-9]*)-(?:" + TYPES + r")-\d[\w.]*")
for p, r in cmd_files():
    fence = False
    for i, l in enumerate(read(p).splitlines(), 1):
        s = l.lstrip()
        if s.startswith("```"): fence = not fence; continue
        if fence or s.startswith("<!--"): continue          # skip fenced code and the scope header
        for rx in DEVTRACE:
            m = rx.search(l)
            if m:
                add("INFO", r, "development-trace language '" + m.group(0).strip() + "' - state the system as it is now, not how the document evolved; rephrase timelessly (or, for scope, an exclusion ADR / 'deferred until <trigger>')", i)
                break
        ms = SELFREF.search(l)
        if ms:
            add("INFO", r, "self-reference '" + ms.group(0).strip() + "' - the spec reads as standalone project documentation; never name a skill, engine, tool, or generation step", i)
        for mc in CTXID.finditer(l):
            if mc.group(1).upper() not in TYPESET:
                add("INFO", r, "context-namespaced id '" + mc.group(0).strip() + "' - use a bare type prefix ('" + mc.group(0).split("-", 1)[1].strip() + "'); a '<CTX>-TYPE-NNN' id silently fails to register while bare references to it resolve", i)

# 14c unquantified quality adjective in a requirement (INFO; requirements area only). Every requirement is a
# measurable bar + how it's enforced, never an adjective. Flag a quality adjective on a line carrying NO
# measurable bar (a comparator+number or number+unit); the conductor/author pins or rephrases it.
ADJ = re.compile(r"\b(fast|slow|scalable|secure|robust|reliable|performant|efficient|responsive|user-friendly|"
    r"intuitive|seamless|flexible|maintainable|lightweight|snappy|quick|smooth|highly available|"
    r"high-performance|low-latency|high-throughput)\b", re.I)
BAR = re.compile(r"[<>≤≥]\s*\d|\b\d[\d.,]*\s*(?:ms|s|sec|m|min|h|hr|%|rps|qps|tps|MB|GB|KB|TB|bytes|users|"
    r"requests|req|connections|nodes|replicas|days|x|×)\b", re.I)
for p, r in cmd_files():
    if not (r.startswith("05-functional-spec") or r.startswith("06-requirements/")): continue
    fence = False
    for i, l in enumerate(read(p).splitlines(), 1):
        s = l.lstrip()
        if s.startswith("```"): fence = not fence; continue
        if fence or s.startswith("<!--") or BAR.search(l): continue
        m = ADJ.search(l)
        if m:
            add("INFO", r, "unquantified quality adjective '" + m.group(0) + "' with no measurable bar - a requirement is a number + how it's enforced, never an adjective", i)

# 15 no task ships with an unresolved gap (the last-responsible-moment forcing checkpoint, enforced)
for p, r in cmd_files():
    if not r.startswith("08-delivery/tasks/") or r.split("/")[-1] == "build-order.md": continue
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
    if not r.startswith("08-delivery/tasks/") or r.split("/")[-1] == "build-order.md": continue
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
