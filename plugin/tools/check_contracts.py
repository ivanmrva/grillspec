#!/usr/bin/env python3
# check_contracts.py - bind the machine contracts (openapi.yaml / asyncapi.yaml) to the grillspec ID graph.
#
# Division of labour: Spectral (`spectral:oas`) validates OpenAPI/AsyncAPI *structure & style*; THIS checks the
# cross-layer linkage no off-the-shelf tool can see, because it needs the spec's defined-ID set:
#   (a) every grillspec id a contract REFERENCES (x-grillspec-id · x-serves · SEC- scopes · x-data · channel ids)
#       resolves to a real definition in spec/**.md - a contract pointing at a use-case/command/data/rule that
#       does not exist is a hard ERROR;
#   (b) every REST operation carries its traceability hooks (x-grillspec-id: API-, x-serves: UC-/CMD-), a
#       per-operation security scope on mutations, and an error response - WARN (Spectral owns the rest).
#
# Requires PyYAML. No-ops cleanly when PyYAML or spec/09-solution/api is absent (so CI never hard-fails on a
# project without contracts yet). Run from the project root:  python3 tools/check_contracts.py [spec_dir]
import sys, re, pathlib
try:
    import yaml
except ImportError:
    print("check_contracts: PyYAML not installed (pip install pyyaml) - skipping (Spectral still validates structure)")
    sys.exit(0)

SPEC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "spec")
API = SPEC / "09-solution" / "api"
if not API.exists():
    print("check_contracts: no spec/09-solution/api - nothing to check.")
    sys.exit(0)

# Mirror lint_spec's type-prefix vocabulary (kept in sync via selfcheck).
TYPES = "UC|AC|CMD|EVT|AGG|VO|HOT|POL|RM|ENTL|ENT|NFR|ASR|API|SEC|THR|DATA|OBL|SLO|EXP|DS|ML|ADR|T"
IDCORE = r"(?:" + TYPES + r")-[A-Za-z0-9._-]*[A-Za-z0-9]"   # mirrors lint_spec's IDCORE: a trailing '.'/',' from prose ('Realizes RM-601.') is NOT captured
IDTOK = re.compile(r"(?<![A-Za-z0-9-])" + IDCORE)
DEF1 = re.compile(r"^\s*[-*#]*\s*\|?\s*\**(" + IDCORE + r")\b")        # ID as the first token of a line/cell (after leading -, *, #, |, or bold)
DEF2 = re.compile(r"\bid:\s*(" + IDCORE + r")", re.I)                 # id: <ID>
DEF3 = re.compile(r"(?:^|[·;:,|←→⟵⟶])\s*[*`_]*\s*(" + IDCORE + r")\s+[A-Z]")   # lint_spec DEF3: inline '<ID> <Name>' enumeration (grill-ddd's 'commands: CMD-201 ExtractAtoms · CMD-204 …', event-flow 'EVT- ⟵ CMD-')

# Defined-id set from markdown. Mirrors lint_spec's definition harvest (leading row-key / `id:` / inline
# '<ID> <Name>' enumeration). Errs toward MORE-defined, never a false "undefined".
defined = set()
for p in SPEC.rglob("*.md"):
    try: txt = p.read_text(encoding="utf-8", errors="replace")
    except Exception: continue
    for l in txt.splitlines():
        m = DEF1.match(l) or DEF2.search(l)
        if m: defined.add(m.group(1))
        for m in DEF3.finditer(l): defined.add(m.group(1))   # commands/events/read-models enumerated inline as '<ID> <Name>'
for p in SPEC.rglob("ADR-*.md"):
    m = re.match(r"(ADR-[A-Za-z][A-Za-z0-9]*-\d+)", p.name)
    if m: defined.add(m.group(1).upper())

F = []
def add(sev, where, msg): F.append((sev, where, msg))

def walk_ids(node):
    """Yield every grillspec id appearing anywhere in the parsed contract (keys and scalar values)."""
    if isinstance(node, dict):
        for k, v in node.items():
            for t in IDTOK.findall(str(k)): yield t
            yield from walk_ids(v)
    elif isinstance(node, list):
        for v in node: yield from walk_ids(v)
    else:
        for t in IDTOK.findall(str(node)): yield t

def load(yf):
    try: return yaml.safe_load(yf.read_text(encoding="utf-8"))
    except Exception as e:
        add("ERROR", yf.name, "not valid YAML: %s" % str(e).splitlines()[0]); return None

METHODS = {"get", "put", "post", "delete", "patch", "options", "head", "trace"}

# --- OpenAPI (REST) ---
for yf in sorted(API.glob("openapi*.y*ml")):
    doc = load(yf)
    if not isinstance(doc, dict): continue
    root_security = doc.get("security")   # OpenAPI: a document-level security requirement applies to every operation unless the operation overrides it
    # API- ids are MINTED by the contract (an operation's x-grillspec-id), not referenced from spec/ - collect
    # them so they are not flagged as undefined; every OTHER id type is a cross-layer reference that must resolve.
    minted = set()
    for item in (doc.get("paths") or {}).values():
        if isinstance(item, dict):
            for op in item.values():
                if isinstance(op, dict):
                    gid = op.get("x-grillspec-id") or op.get("x-id")
                    if gid and str(gid).upper().startswith("API-"): minted.add(str(gid))
    local_defined = defined | minted
    for tok in sorted(set(walk_ids(doc))):
        if tok not in local_defined:
            add("ERROR", yf.name, "references undefined grillspec id '%s' (no definition in spec/**.md) - the contract points at a spec element that does not exist" % tok)
    for path, item in (doc.get("paths") or {}).items():
        if not isinstance(item, dict): continue
        for method, op in item.items():
            if method.lower() not in METHODS or not isinstance(op, dict): continue
            loc = "%s %s" % (method.upper(), path)
            gid = op.get("x-grillspec-id") or op.get("x-id")
            if not (gid and str(gid).upper().startswith("API-")):
                add("WARN", yf.name, "%s has no 'x-grillspec-id: API-NNN' - the operation is not traceable to the API catalogue" % loc)
            if not op.get("x-serves"):
                add("WARN", yf.name, "%s has no 'x-serves: [UC-… / CMD-…]' - every endpoint serves a use-case or command" % loc)
            # effective security per OpenAPI inheritance: the operation's own 'security' (even an explicit []) overrides the document-level one
            eff_sec = op["security"] if "security" in op else root_security
            if method.lower() in {"post", "put", "patch", "delete"} and not eff_sec and not op.get("x-public"):
                add("WARN", yf.name, "%s is a mutation with no effective 'security' scope (no per-operation rule and no document-level default) - default-deny wants an explicit authz rule (or 'x-public: true')" % loc)
            responses = op.get("responses") or {}
            if not any(str(c).startswith(("4", "5")) or c == "default" for c in responses):
                add("WARN", yf.name, "%s declares no 4xx/5xx/default response - every endpoint carries an RFC 9457 problem+json error model" % loc)

# --- AsyncAPI (events): id resolution only; Spectral/AsyncAPI-CLI own the structural rules ---
for yf in sorted(API.glob("asyncapi*.y*ml")):
    doc = load(yf)
    if not isinstance(doc, dict): continue
    for tok in sorted(set(walk_ids(doc))):
        if tok not in defined:
            add("ERROR", yf.name, "references undefined grillspec id '%s' (no definition in spec/**.md)" % tok)

order = {"ERROR": 0, "WARN": 1}
for sev, where, msg in sorted(F, key=lambda x: (order[x[0]], x[1], x[2])):
    print("%-5s %-20s %s" % (sev, where, msg))
e = sum(1 for x in F if x[0] == "ERROR")
print("\n%d error(s), %d warning(s)." % (e, len(F) - e))
sys.exit(1 if e else 0)
