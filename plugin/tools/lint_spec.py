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
    "06-requirements/integration","06-requirements/security","08-ux","07-design-system","06-requirements/compliance","06-requirements/ml","06-requirements/entitlements",
    "11-commercial/monetization","11-commercial/go-to-market","11-commercial/growth",
    "09-solution/arch","09-solution/data","09-solution/api","09-solution/security","09-solution/infra-ops",
    "09-solution/observability","09-solution/test","09-solution/ml",
    "10-delivery/conventions","10-delivery/tasks","10-delivery/impl-design","10-delivery/verification","12-operate"]
# Per-area deliverables: glossary.md / actors.md may appear in ANY area folder (no shared root singletons).
AREA_FILES = ["glossary.md", "actors.md"]
AREA_DIR = {"problem-validation":"01-discovery","product-vision":"02-product/vision",
    "customer-discovery":"02-product/customers","market":"02-product/market","goals":"02-product/goals","constraints":"03-constraints","system-context":"03-system-context",
    "ddd":"04-domain/ddd","derive-functional":"05-functional-spec","quality":"06-requirements/quality",
    "data-reqs":"06-requirements/data","integration-reqs":"06-requirements/integration",
    "security-reqs":"06-requirements/security","ux-reqs":"08-ux","design-system":"07-design-system","compliance":"06-requirements/compliance","ml-reqs":"06-requirements/ml","entitlements":"06-requirements/entitlements",
    "monetization":"11-commercial/monetization","go-to-market":"11-commercial/go-to-market","growth":"11-commercial/growth",
    "derive-architecture":"09-solution/arch","derive-data-architecture":"09-solution/data",
    "derive-api-contracts":"09-solution/api","derive-security-architecture":"09-solution/security",
    "derive-infra-ops":"09-solution/infra-ops","derive-observability":"09-solution/observability",
    "derive-test-strategy":"09-solution/test","derive-impl-design":"10-delivery/impl-design","derive-ml-architecture":"09-solution/ml",
    "derive-conventions":"10-delivery/conventions","derive-tasks":"10-delivery/tasks",
    "conformance-review":"10-delivery/verification"}
# Which ID-prefixes are DEFINED in which directory (enforces stage purity / no-unrelated-content).
# The type-prefix set here is the SINGLE source of truth; selfcheck.py diffs it against the prefixes
# the skills declare, so adding a prefix to a skill without registering it here is caught.
PREFIX_OWNER = {"UC":"05-functional-spec","AC":"05-functional-spec",
    "CMD":"04-domain/ddd","EVT":"04-domain/ddd","AGG":"04-domain/ddd",
    "VO":"04-domain/ddd","HOT":"04-domain/ddd","POL":"04-domain/ddd","RM":"04-domain/ddd","ENT":"04-domain/ddd",
    "NFR":"06-requirements/quality","ASR":"06-requirements/quality","DATA":"06-requirements/data",
    "SEC":"06-requirements/security","THR":"06-requirements/security","OBL":"06-requirements/compliance","API":"09-solution/api","ML":"06-requirements/ml",
    "ENTL":"06-requirements/entitlements",
    "SLO":"09-solution/observability","EXP":"11-commercial/growth","T":"10-delivery/tasks","DS":"07-design-system"}
def file_layer(r):
    if r.startswith("04-domain/ddd"): return 1
    if r.startswith("05-functional-spec") or r.startswith("06-requirements/"): return 2
    if r.startswith("11-commercial/"): return 2          # monetization · go-to-market · growth (post-launch sinks)
    if r.startswith("07-design-system"): return 3        # the visual + interaction contract (consumes requirements)
    if r.startswith("08-ux"): return 4                   # journeys (consume the design system + requirements)
    if r.startswith("09-solution/"): return 5
    if r.startswith("10-delivery/"): return 6
    if r.startswith("12-operate"): return 6
    return 0  # constraints, 02-product/*, discovery, singletons
ID_LAYER = {"CMD":1,"EVT":1,"AGG":1,"VO":1,"HOT":1,"POL":1,"RM":1,"ENT":1,"UC":2,"AC":2,"NFR":2,"ASR":2,"SEC":2,"THR":2,"DATA":2,"OBL":2,"ENTL":2,"EXP":2,"ML":2,"DS":3,"API":5,"SLO":5,"T":6,"ADR":0}
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
if any(ccount(d) > 0 for d in LEAF_DIRS if d.startswith("09-solution/")):
    empty = [d for d in LEAF_DIRS if (d.startswith("05-functional-spec") or d.startswith("06-requirements/") or d.startswith("07-design-system") or d.startswith("08-ux")) and ccount(d) == 0]
    if empty:
        add("WARN", "(gate)", "09-solution/* has content but requirements/design-system/ux incomplete (" + ", ".join(empty) + ") - architecture-readiness gate not met")

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
REFMARK = re.compile(r"(?:\b(?:implements?|depends(?:-on)?|refs?|references?|see|satisf(?:y|ies|ied-by)|covers?|covered-by|maps?-?to|reali[sz]es?|traces?-?to|verif(?:y|ies)|validates?|addresses|supersedes|surfaces?|renders?|displays?|mitigat(?:es|ed-by)|prices?|priced-by|gates?|gated-by|enforces?|enforced-by|evidences?|evidenced-by|whenever|reacts?-to|consumed-by|consumes)\b|->|→)\s*:?\s*([^\n]*)", re.I)
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
# An authorization matrix (header first-cell command/cmd/operation, other cols = actors) keys its rows by
# CMD- as a ROW-KEY REFERENCE, not a definition (the command is defined in ddd). Precompute those body-row
# line numbers so the definition scan skips them — same spirit as the traceability.md exemption.
authz_rows = {}                                             # rel-path -> set of 1-based body-row line numbers
for p, r in cmd_files():
    lines = read(p).splitlines(); i = 0
    while i < len(lines):
        if lines[i].strip().startswith("|") and i+1 < len(lines) and SEP.match(lines[i+1]):
            hdr = [c.strip().lower() for c in lines[i].strip().strip("|").split("|")]; j = i+2
            is_authz = bool(hdr) and hdr[0] in ("command", "cmd", "cmd-id", "operation") and len(hdr) >= 2 and r.startswith("06-requirements/security")
            while j < len(lines) and lines[j].strip().startswith("|") and not SEP.match(lines[j]):
                if is_authz: authz_rows.setdefault(r, set()).add(j+1)
                j += 1
            i = j
        else:
            i += 1
for p, r in cmd_files():
    if os.path.basename(r) == "traceability.md": continue   # the traceability matrix references IDs (ID->task->code); it never defines them
    lines = read(p).splitlines()
    arows = authz_rows.get(r, ())
    for i, l in enumerate(lines):
        if "|" in l and i+1 < len(lines) and SEP.match(lines[i+1]):
            continue                                         # table HEADER row — first cell is a column label, not an ID definition
        if (i+1) in arows:
            continue                                         # authz-matrix body row — leading CMD- is a row-key reference, not a definition
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
# their drivers downward by design) and traceability.md (the cross-layer trace spine). Skip fenced code +
# the scope header; an id in an absent area (partial spec) is suppressed like the undefined check.
dn_seen = set()
for p, r in cmd_files():
    if is_adr_file(r) or os.path.basename(r) == "traceability.md" or ("/" not in r and r.startswith("_")): continue   # last: spec-root orchestration dashboards (_readiness/_human-input) span all layers by design
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
COV_HINT = {"CMD":"expected a use-case (UC-) projecting it","EVT":"no downstream consumer (a UC-, a 'whenever EVT-' POL- reaction, the asyncapi contract, or an intentional audit-only/internal sink)",
    "AGG":"expected persistence (DATA-) / a use-case","RM":"expected a view use-case (UC-) surfacing it, or N/A for an internal projection","UC":"expected acceptance criteria (AC-) or a task",
    "AC":"not exercised by any test/task","OBL":"no control (SEC-/DATA-/arch) addresses it",
    "THR":"no mitigating control (SEC-/ADR-/OBL-/DATA-) addresses it and it isn't marked accepted-risk",
    "SLO":"no alert/runbook references it","NFR":"no test/SLO evidences it","ASR":"no verifying test",
    "API":"no consumer/test","EXP":"no analytics event/task wires it","DATA":"no consumer"}
trace_ids = set()
_tp = SPEC / "10-delivery" / "verification" / "traceability.md"
if _tp.exists():
    for l in read(_tp).splitlines():
        trace_ids |= set(IDTOK.findall(l))
# The machine contracts (openapi/asyncapi under solution/api) are REAL artifacts, but the scan above is
# .md-only - so an EVT-/API- whose only consumer is the YAML contract would false-WARN 'no downstream
# consumer'. Credit raw ID tokens found in the contract YAML as references for coverage purposes only
# (never as definitions; check_contracts.py validates the contracts' own id references).
_apidir = SPEC / "09-solution" / "api"
if _apidir.exists():
    for _yf in sorted(_apidir.glob("*.yaml")) + sorted(_apidir.glob("*.yml")):
        refset.update(IDTOK.findall(read(_yf)))
# THR / EVT coverage exceptions the back-reference test (tok in refset) structurally misses, read from the
# element's OWN definition block (its def line through the line before the next def in the same file):
#  - a THR is covered when its block forward-cites a CONTROL — SEC-/ADR-/OBL- (a security control, an ADR
#    structural layer, a compliance obligation), or a DATA- control NEAR a mitigation cue — or is marked
#    accepted-risk; none of those back-reference the THR, so refset never sees it.
#  - an EVT is complete when its block marks it an intentional terminal SINK (audit-only /
#    operator-console-internal — deliberately absent from the published asyncapi catalog, consumed by nothing).
CTRLID = re.compile(r"\b(?:SEC|ADR|OBL)-[A-Za-z0-9._-]*[A-Za-z0-9]\b")   # control-type id: a forward cite IS a mitigation (not an asset)
DATAID = re.compile(r"\bDATA-[A-Za-z0-9._-]*[A-Za-z0-9]\b")
MITCUE = re.compile(r"mitigat|control|address|counter|defen|residual|remediat|safeguard|protect", re.I)
ACCRISK = re.compile(r"accept(?:ed|s)?[ \-]risk", re.I)
EVTSINK = re.compile(r"audit-only|operator-console-internal|internal[ \-]sink|terminal[ \-]sink|intentional[ \-]sink|no[ \-]consumer[ \-]by[ \-]design", re.I)
thr_covered, evt_sinks = set(), set()
for _p, _r in cmd_files():
    if os.path.basename(_r) == "traceability.md": continue
    _lines = read(_p).splitlines()
    _dpos = []                                                # (lineno, id) definition positions, in file order
    for _i, _l in enumerate(_lines):
        if "|" in _l and _i + 1 < len(_lines) and SEP.match(_lines[_i + 1]): continue   # table header row
        _ll = RANGE.sub(" ", _l)
        _m = DEF1.match(_ll)
        _gid = _m.group(1) if _m else None
        if not _gid:
            for _m3 in DEF3.finditer(_l):
                if in_owner_area(_m3.group(1), _r): _gid = _m3.group(1); break
        if _gid: _dpos.append((_i, _gid))
    for _j, (_ln, _gid) in enumerate(_dpos):
        _pre = _gid.split("-")[0].upper()
        if _pre not in ("THR", "EVT"): continue
        _end = _dpos[_j + 1][0] if _j + 1 < len(_dpos) else len(_lines)
        _block = "\n".join(_lines[_ln:_end])
        if _pre == "THR" and (CTRLID.search(_block) or ACCRISK.search(_block) or (DATAID.search(_block) and MITCUE.search(_block))):
            thr_covered.add(_gid)
        if _pre == "EVT" and EVTSINK.search(_block):
            evt_sinks.add(_gid)
# downstream type a coverage WARN expects; if NONE of that type exists yet, the downstream layer is
# simply empty (early stage) and the WARN is noise, not a gap — suppress it. (#7: a CMD has no UC only
# once use-cases exist; before then "CMD has no UC" is 100% expected and drowns real within-layer gaps.)
DOWN_TYPE = {"CMD":("UC",),"EVT":("UC",),"AGG":("DATA",),"RM":("UC",),"UC":("AC",),"AC":("T",),
    "OBL":("SEC","DATA"),"THR":("SEC",),"NFR":("ASR","SLO"),"ASR":("T",),"API":("T",),"EXP":("T",)}
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
    if pre == "THR" and tok in thr_covered: continue            # mitigated by a non-SEC control / accepted-risk (its own block)
    if pre == "EVT" and tok in evt_sinks: continue              # intentional audit-only / operator-console-internal sink
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

# 19 every task traces UP: a T- file must cite at least one upstream spec ID (the UC-/AC-/CMD-/NFR-/…
#    it implements). A task that references nothing has no spec basis - its code can't be conformance-traced.
for p, r in cmd_files():
    if not r.startswith("10-delivery/tasks/") or r.split("/")[-1] == "build-order.md": continue
    upstream = [t for t in IDTOK.findall(RANGE.sub(" ", read(p))) if t.split("-")[0].upper() not in ("T", "ADR")]
    if not upstream:
        add("WARN", r, "task cites no upstream spec ID - a task must trace to what it implements (a UC-/AC-/CMD-/NFR-/DATA-/API-…), else its code has no spec basis to conformance-check against")

# 20 every ADR declares a recognized lifecycle status - makes the obsolete-ADR check (#17) reliable and
#    keeps supersession trackable. (template.md / _archive/ exempt.)
ADRSTATUS = re.compile(r"(?im)^[\s>*#-]*\**\s*status\**\s*:?\s*\**\s*(?:proposed|accepted|superseded|deprecated|rejected|draft)\b")
for p, r in cmd_files():
    if not (r.startswith("adr/") or "/adr/" in r): continue
    b = os.path.basename(r)
    if b == "template.md" or "_archive/" in r: continue
    if not ADRSTATUS.search(read(p)):
        add("WARN", r, "ADR has no recognized 'status:' (Proposed/Accepted/Superseded/Deprecated/Rejected) - record the lifecycle status so supersession stays trackable")

# ── structured-fact enforcement (state machines · authz matrix · typed scalar facts) ──
# These reward the canonical-form structure the skills emit: a structured slot is a question the author had
# to answer, so the check both verifies it AND forces completeness. All WARN — a partial artifact is legal
# mid-spec, and value-normalization is heuristic; ERROR is reserved for the unambiguous violations above.
def md_tables(lines):
    """Yield (lowercased-header-cells, [body-row-cell-lists]) for each markdown table in `lines`."""
    i = 0
    while i < len(lines):
        l = lines[i].strip()
        if l.startswith("|") and i + 1 < len(lines) and SEP.match(lines[i+1]):
            header = [c.strip().lower() for c in l.strip("|").split("|")]
            body, j = [], i + 2
            while j < len(lines) and lines[j].strip().startswith("|") and not SEP.match(lines[j]):
                body.append([c.strip() for c in lines[j].strip().strip("|").split("|")]); j += 1
            yield header, body; i = j
        else:
            i += 1

# 21 state-machine integrity (ddd only). A transition table = header carrying 'from' and 'to' (+ optional
#    'trigger'/'event', 'guard'). Build the graph and flag unreachable / dead-end / nondeterministic states.
SMARK = re.compile(r"^[\-—*•]+$|^\(?(?:initial|start|terminal|final|end|none)\)?$", re.I)
def nstate(s):
    return re.sub(r"\s*\((?:initial|start|terminal|final|end)\)\s*$", "", s, flags=re.I).strip(" *`_·").strip()
def split_states(raw):
    # a compound 'A / B' from/to cell is shorthand for several states sharing the row's trigger/guard;
    # split on ' / ' (spaces required, so kebab names like 'awaiting-retry' and 'n/a' are untouched) and normalize each
    return [x for x in (nstate(s) for s in re.split(r"\s+/\s+", raw.strip())) if x]
for p, r in cmd_files():
    if not r.startswith("04-domain/ddd"): continue
    for header, body in md_tables(read(p).splitlines()):
        if "from" not in header or "to" not in header or ("trigger" not in header and "event" not in header): continue
        fi, ti = header.index("from"), header.index("to")
        gi = header.index("guard") if "guard" in header else None
        tri = header.index("trigger") if "trigger" in header else (header.index("event") if "event" in header else None)
        trans, initials, terminals, states = [], set(), set(), set()
        for row in body:
            if len(row) <= max(fi, ti): continue
            fr_raw, to_raw = row[fi], row[ti]
            trig = row[tri] if tri is not None and len(row) > tri else ""
            guard = row[gi] if gi is not None and len(row) > gi else ""
            fr_init = bool(SMARK.match(fr_raw.strip())) or "(initial" in fr_raw.lower() or "(start" in fr_raw.lower()
            to_term = bool(SMARK.match(to_raw.strip())) or "(terminal" in to_raw.lower() or "(final" in to_raw.lower() or "(end" in to_raw.lower()
            for fr in (split_states(fr_raw) or [""]):
                for to in (split_states(to_raw) or [""]):
                    if ("(terminal" in fr_raw.lower() or "(final" in fr_raw.lower()) and fr: terminals.add(fr)
                    if ("(initial" in to_raw.lower() or "(start" in to_raw.lower()) and to: initials.add(to)
                    if fr_init and to: initials.add(to)
                    if to_term and fr: terminals.add(fr)
                    if fr and not fr_init: states.add(fr)
                    if to and not to_term: states.add(to)
                    if fr and to and not fr_init and not to_term: trans.append((fr, trig.strip(), to, guard.strip()))
        if len(states) < 2: continue
        outgoing = {}
        for fr, trig, to, g in trans: outgoing.setdefault(fr, []).append((trig, to, g))
        tos = {to for _, _, to, _ in trans}
        roots = initials or {s for s in states if s not in tos}
        seen, stack = set(roots), list(roots)
        while stack:
            for _, to, _ in outgoing.get(stack.pop(), []):
                if to not in seen: seen.add(to); stack.append(to)
        for s in sorted(states - seen):
            add("WARN", r, "state-machine: '%s' is unreachable (nothing transitions into it, not marked initial) - add an entering transition or mark it initial" % s)
        for s in sorted(states - set(outgoing) - terminals):
            add("WARN", r, "state-machine: '%s' is a dead-end (nothing transitions out, not marked terminal) - add an exit transition or mark it terminal/final" % s)
        bytrig = {}
        for fr, trig, to, g in trans: bytrig.setdefault((fr, trig.lower()), []).append((to, g))
        for (fr, trig), outs in bytrig.items():
            if len({to for to, _ in outs}) > 1 and any(not g for _, g in outs):
                add("WARN", r, "state-machine: from '%s' on '%s' multiple targets (%s) lack a distinguishing guard - the transition is nondeterministic" % (fr, trig or "?", ", ".join(sorted({to for to, _ in outs}))))

# 22 authorization completeness, in either authored shape:
#    matrix  — header[0] ∈ command/cmd/operation, other cols = actors, cells = a decision; OR
#    longform— rows keyed by SEC-, with an 'actor' col + a 'command' col + a decision col.
#    Flag empty decision cells; flag any defined CMD- with no rule/row (default-deny still wants it explicit).
seen_cmds, have_authz = set(), False
for p, r in cmd_files():
    if not r.startswith("06-requirements/security"): continue   # authz matrices/rules are authored only here
    for header, body in md_tables(read(p).splitlines()):
        if not header: continue
        if header[0] in ("command", "cmd", "cmd-id", "operation") and len(header) >= 2:   # matrix form
            have_authz = True; actors = header[1:]
            for row in body:
                key = (row[0] if row else "").strip(" *`_")
                mk = re.match(r"^(" + IDCORE + r")", key)
                if mk and mk.group(1).split("-")[0].upper() == "CMD": seen_cmds.add(mk.group(1))
                for ci, actor in enumerate(actors, start=1):
                    if (row[ci].strip() if ci < len(row) else "") == "":
                        add("WARN", r, "authorization matrix: '%s' × '%s' has no decision - every actor × command cell is allow / deny / a named condition" % (key or "?", actor))
        elif "actor" in header and ("command" in header or "cmd" in header):            # long form
            have_authz = True
            ai = header.index("actor"); ci2 = header.index("command") if "command" in header else header.index("cmd")
            di = next((header.index(k) for k in ("decision", "access", "allow", "rule") if k in header), None)
            for row in body:
                if ci2 < len(row):
                    for mk in re.finditer(r"(" + IDCORE + r")", row[ci2]):
                        if mk.group(1).split("-")[0].upper() == "CMD": seen_cmds.add(mk.group(1))
                for idx, label in [(ai, "actor"), (ci2, "command")] + ([(di, "decision")] if di is not None else []):
                    if (row[idx].strip() if idx < len(row) else "") == "":
                        add("WARN", r, "authorization rule with an empty %s cell - actor, command, and decision are all required (default-deny means every command needs an explicit who-may rule)" % label)
if have_authz and seen_cmds:
    for cmd in sorted(d for d in defined if d.split("-")[0].upper() == "CMD"):
        if cmd not in seen_cmds:
            add("WARN", sorted(defsites.get(cmd) or def3sites.get(cmd) or ["(?)"])[0],
                "authorization: command '%s' has no rule/row in any authorization model - default-deny still wants each command's who-may rule explicit (or mark it system/unguarded)" % cmd)

# 23 typed scalar facts, harvested in BOTH authored forms: an inline '<key>: <value>' (attributed to the
#    nearest preceding ID on the line), AND a table COLUMN whose header is a typed key (attributed to the
#    row's leading ID). Flag (a) the same (ID, key) carrying differing values across the spec - a likely
#    contradiction (retention 30d vs 90d); (b) a DATA- element declaring none of class/retention/residency.
#    WARN throughout — value normalization is heuristic, and a partial element is legal mid-spec.
TYPED_LIST = ["retention", "residency", "classification", "class", "sla", "limit", "quota", "price", "tier"]
TF = re.compile(r"\b(" + "|".join(TYPED_LIST) + r")\s*:\s*([^|<>\n]+?)\s*(?:\||$)", re.I)
EMPTY_CELL = {"", "—", "-", "–", "n/a", "tbd", "…"}
def nval(v):
    v = v.strip().lower().rstrip(".")
    v = re.sub(r"\byears?\b|\byrs?\b", "y", v); v = re.sub(r"\bmonths?\b|\bmos?\b", "mo", v)
    v = re.sub(r"\bdays?\b", "d", v); v = re.sub(r"\bhours?\b|\bhrs?\b", "h", v)
    return re.sub(r"\s+", "", v)
def canon_key(k): return "class" if k.lower() == "classification" else k.lower()
fieldvals, data_fields = {}, {}
def record(owner, key, val, r, ln):
    key = canon_key(key)
    fieldvals.setdefault((owner, key), []).append((nval(val), r, ln, val.strip()))
    if owner.split("-")[0].upper() == "DATA" and key in ("class", "retention", "residency"):
        data_fields.setdefault(owner, set()).add(key)
for p, r in cmd_files():
    if is_adr_file(r): continue
    lines = read(p).splitlines()
    for i, l in enumerate(lines, 1):                                                   # inline form
        idpos = [(m.start(), m.group(0)) for m in IDTOK.finditer(l)]
        if not idpos: continue
        for mk in TF.finditer(l):
            prior = [tok for pos, tok in idpos if pos <= mk.start()]
            record(prior[-1] if prior else idpos[0][1], mk.group(1), mk.group(2), r, i)
    for header, body in md_tables(lines):                                              # table-column form
        keycols = {}
        for ci, h in enumerate(header):
            for k in TYPED_LIST:
                if h == k or h.startswith(k + " ") or h.startswith(k + "("): keycols[ci] = k; break
        if not keycols: continue
        for row in body:
            mk = re.match(r"^[*`_ ]*(" + IDCORE + r")", row[0]) if row else None
            if not mk: continue
            for ci, k in keycols.items():
                cell = row[ci].strip() if ci < len(row) else ""
                if cell.lower() not in EMPTY_CELL and not cell.lower().startswith("deferred"):
                    record(mk.group(1), k, cell, r, 0)
def floc(e): return ("%s:%d" % (e[1], e[2])) if e[2] else e[1]
for (idk, key), es in fieldvals.items():
    if len({e[0] for e in es}) > 1:
        where = "; ".join("%s=%s" % (floc(e), e[3]) for e in sorted(es, key=lambda x: (x[1], x[2]))[:4])
        add("WARN", es[0][1], "typed field '%s' for %s has conflicting values (%s) - state one canonical value, or supersede" % (key, idk, where))
for did in sorted(d for d in defined if d.split("-")[0].upper() == "DATA"):
    if not data_fields.get(did):
        add("WARN", sorted(defsites.get(did) or def3sites.get(did) or ["(?)"])[0],
            "data element '%s' declares no class/retention/residency - a data element carries each as a typed field/column (a value, or 'deferred until <trigger>')" % did)

# 24 the task dependency graph must be a DAG. Edges from explicit 'depends-on: T-…' under 10-delivery/tasks/
#    (source = the task the file/row defines; targets = the T- it depends on). A cycle is unbuildable - the
#    execution loop cannot sequence it - so it is a hard ERROR (IDs + an explicit verb = a sound parse).
DEP = re.compile(r"\bdepends(?:-on)?\b\s*:?\s*([^\n]*)", re.I)
file_tid, tdeps = {}, {}
for tid, files in defsites.items():
    if tid.split("-")[0].upper() == "T":
        for f in files:
            if f.startswith("10-delivery/tasks/"): file_tid.setdefault(f, tid)
for p, r in cmd_files():
    if not r.startswith("10-delivery/tasks/"): continue
    for l in read(p).splitlines():
        ls = RANGE.sub(" ", l)
        lead = re.match(r"^\s*[-*#]*\s*\|?\s*\**(" + IDCORE + r")", ls)
        src = lead.group(1) if (lead and lead.group(1).split("-")[0].upper() == "T") else file_tid.get(r)
        if not src: continue
        for mk in DEP.finditer(l):
            for tok in IDTOK.findall(mk.group(1)):
                if tok.split("-")[0].upper() == "T" and tok != src: tdeps.setdefault(src, set()).add(tok)
# iterative three-colour DFS (no recursion limit — a task graph can be arbitrarily deep)
color, cyc = {}, []
for root in list(tdeps):
    if color.get(root, 0) != 0: continue
    stack = [(root, iter(tdeps.get(root, ())))]; path = [root]; color[root] = 1
    while stack and not cyc:
        u, it = stack[-1]
        advanced = False
        for v in it:
            if color.get(v, 0) == 1: cyc.append(path[path.index(v):] + [v])
            elif color.get(v, 0) == 0:
                color[v] = 1; path.append(v); stack.append((v, iter(tdeps.get(v, ())))); advanced = True
            if cyc or advanced: break
        if cyc: break
        if not advanced:
            color[u] = 2; stack.pop(); path.pop()
if cyc:
    add("ERROR", "10-delivery/tasks/", "task dependency cycle: " + " -> ".join(cyc[0]) + " - the build order is not a DAG and cannot be sequenced; break it (split a task, or invert a dependency)")

# 25 every NFR names HOW it's enforced (a bar with no teeth is an adjective). Recognize an enforcement field
#    ('enforced-by'/'enforcement'/'verified-by'/'verification') inline or as a table column; WARN an NFR-
#    (owned by the quality area) that names none. (ASR enforcement = its fitness function, derived later.)
ENF_INLINE = re.compile(r"\b(?:enforced-by|enforcement|verified-by|verification|evidenced-by)\b\s*:?\s*([^|<>\n]+)", re.I)
enforced = set()
for p, r in cmd_files():
    if not r.startswith("06-requirements/quality"): continue
    lines = read(p).splitlines()
    for l in lines:
        idpos = [(m.start(), m.group(0)) for m in IDTOK.finditer(l)]
        if not idpos: continue
        for mk in ENF_INLINE.finditer(l):
            if mk.group(1).strip(" —-–·"):
                prior = [tok for pos, tok in idpos if pos <= mk.start()]
                owner = prior[-1] if prior else idpos[0][1]
                if owner.split("-")[0].upper() in ("NFR", "ASR"): enforced.add(owner)
    for header, body in md_tables(lines):
        ecols = [ci for ci, h in enumerate(header) if h.startswith("enforc") or h.startswith("verif") or h.startswith("evidence")]
        if not ecols: continue
        for row in body:
            mk = re.match(r"^[*`_ ]*(" + IDCORE + r")", row[0]) if row else None
            if not mk or mk.group(1).split("-")[0].upper() not in ("NFR", "ASR"): continue
            if any(ci < len(row) and row[ci].strip().lower() not in EMPTY_CELL for ci in ecols): enforced.add(mk.group(1))
for nid in sorted(d for d in defined if d.split("-")[0].upper() == "NFR"):
    sites = defsites.get(nid) or def3sites.get(nid) or set()
    if not any(s.startswith("06-requirements/quality") for s in sites): continue
    if nid not in enforced:
        add("WARN", sorted(sites or ["(?)"])[0], "%s names no enforcement - every NFR carries how it's verified (test · gate/fitness-function · lint · infra · SLO · review) as an 'enforced-by' field/column, not just a number" % nid)

# 26 every module in the architecture module-map declares a role (the ports-&-adapters contract codegen and
#    conformance-review check dependency direction against). Recognize a map (header has 'module' + 'role');
#    WARN a module row whose role cell is empty.
for p, r in cmd_files():
    if not r.startswith("09-solution/arch"): continue
    for header, body in md_tables(read(p).splitlines()):
        if "module" not in header or "role" not in header: continue
        mi, ri = header.index("module"), header.index("role")
        for row in body:
            name = row[mi].strip() if (row and mi < len(row)) else ""
            if not name or name.lower() in EMPTY_CELL: continue
            if (row[ri].strip() if ri < len(row) else "").lower() in EMPTY_CELL:
                add("WARN", r, "module '%s' declares no role - each module names its role (domain · driving-port · driven-port · application-service · adapter) so its inward-only dependency direction is checkable" % name)

order = {"ERROR": 0, "WARN": 1, "INFO": 2}
F.sort(key=lambda x: (order[x[0]], x[1], x[2]))
e = sum(1 for x in F if x[0] == "ERROR"); wn = sum(1 for x in F if x[0] == "WARN")
for sev, path, line, msg in F:
    loc = (path + ":" + str(line)) if line else path
    print("%-5s %-44s %s" % (sev, loc, msg))
print("\n%d error(s), %d warning(s)." % (e, wn))
sys.exit(1 if e else 0)
