#!/usr/bin/env python3
# check_freshness.py - flag spec artifacts that may be STALE: an upstream definition they CITE has
# changed since the artifact was last (re)written. The complement of guard_derived.py:
#   guard_derived  = hash-of-SELF     -> "was this regenerate-only file hand-edited?"   (gate, derived zone only)
#   check_freshness = hash-of-UPSTREAM -> "did an upstream def this artifact cites move since it was written?"
# It covers BOTH zones (grilled + derived) and is ADVISORY (default exit 0) - an audit aid that sharpens the
# staleness judgment, NOT a commit gate. The system prevents stale work by PROPAGATION, not by a status flag;
# this only tells the auditor WHERE to look, never blocks. Granularity is the ID's definition BLOCK (its def
# line through the line before the next def in the same file), so an unrelated edit elsewhere never false-flags.
#   check (default): for every artifact, compare the recorded hash of each upstream id it cites to the current
#                    hash; print artifacts whose cited definitions have drifted (stale candidates). Exit 0
#                    (advisory) unless --strict, then exit 1 on any drift.
#   --record [paths...]: (re)capture the upstream-input hashes for the given artifacts (or all). Run right
#                        after writing/reconciling an area (the conductor does this beside guard_derived
#                        --record), so a freshly reconciled artifact baselines clean.
# Stdlib only. Run from the project root:  python3 tools/check_freshness.py [check|--record [paths...]] [--strict]
import sys, os, re, json, hashlib, pathlib

SPEC = pathlib.Path("spec")
LOCK = os.path.join(".claude", "freshness.lock")

# TYPES mirrors lint_spec.py's vocabulary (selfcheck guards them in sync) - resolve ids against the same set.
TYPES = "UC|AC|CMD|EVT|AGG|VO|INV|HOT|POL|RM|ENTL|ENT|NFR|ASR|API|SEC|THR|DATA|OBL|SLO|EXP|DS|JRN|ML|FAC|REPO|SVC|IF|MOD|CA|ADR|T"
ID = r"(?:" + TYPES + r")-[A-Za-z0-9._-]*[A-Za-z0-9]"
DEF1 = re.compile(r"^\s*[-*#]*\s*\|?\s*\**(" + ID + r")\b")        # id as first token of a line/cell
DEF2 = re.compile(r"^\s*id:\s*(" + ID + r")\b", re.I)             # id: <ID>
IDTOK = re.compile(r"(?<![A-Za-z0-9-])" + ID)   # left boundary matches lint_spec: a preceding alnum or '-' blocks it


def read(p):
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def def_blocks():
    """{id: sha256(definition-block)} and {id: defining-file-relpath}. First definition wins."""
    blocks, owner = {}, {}
    for p in sorted(SPEC.rglob("*.md")):
        if p.name == "traceability.md":
            continue   # references ids, never defines them (matches impact.py)
        rel = p.relative_to(SPEC).as_posix()
        lines = read(p).splitlines()
        defs = [(i, (DEF1.match(l) or DEF2.match(l)).group(1))
                for i, l in enumerate(lines) if DEF1.match(l) or DEF2.match(l)]
        for j, (ln, gid) in enumerate(defs):
            end = defs[j + 1][0] if j + 1 < len(defs) else len(lines)
            block = "\n".join(lines[ln:end])
            if gid not in blocks:
                blocks[gid] = hashlib.sha256(block.encode("utf-8")).hexdigest()
                owner[gid] = rel
    return blocks, owner


def upstream_refs(p, own_ids, blocks):
    """ids cited by artifact p that are DEFINED ELSEWHERE (upstream-only is enforced by lint) and trackable."""
    cited = set()
    for l in read(p).splitlines():
        for m in IDTOK.finditer(l):
            cited.add(m.group(0))
    return {c for c in cited if c in blocks and c not in own_ids}


def own_of(rel, owner):
    return {i for i, f in owner.items() if f == rel}


def load_lock():
    try:
        return json.load(open(LOCK))
    except Exception:
        return {}


def save_lock(d):
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    json.dump({k: dict(sorted(v.items())) for k, v in sorted(d.items())}, open(LOCK, "w"), indent=0)
    open(LOCK, "a").write("\n")


def artifacts():
    return [p.relative_to(SPEC).as_posix() for p in sorted(SPEC.rglob("*.md")) if p.name != "traceability.md"]


def record(paths):
    blocks, owner = def_blocks()
    lock = load_lock()
    targets = [pathlib.Path(p).as_posix() for p in paths] if paths else artifacts()
    # accept either spec-relative or project-relative paths for the given targets
    rels = []
    for t in targets:
        t = t[len("spec/"):] if t.startswith("spec/") else t
        if (SPEC / t).is_file():
            rels.append(t)
    n = 0
    for rel in rels:
        own = own_of(rel, owner)
        lock[rel] = {c: blocks[c] for c in upstream_refs(SPEC / rel, own, blocks)}
        n += 1
    save_lock(lock)
    print("freshness.lock updated for %d artifact(s)." % n)
    return 0


def check(strict):
    if not SPEC.exists():
        print("check_freshness: no spec/ dir - nothing to check.")
        return 0
    lock = load_lock()
    if not lock:
        print("check_freshness: no .claude/freshness.lock yet - run `--record` after writing areas to baseline.")
        return 0
    blocks, owner = def_blocks()
    stale, untracked = [], []
    for rel in artifacts():
        if rel not in lock:
            untracked.append(rel)
            continue
        recorded = lock[rel]
        for cid, h in recorded.items():
            if cid in blocks and blocks[cid] != h:
                stale.append((rel, cid, owner.get(cid, "?")))
    if stale:
        print("STALE CANDIDATES: an upstream definition cited by these artifacts changed since they were last reconciled.")
        print("(advisory - judge whether the change is materially relevant, then re-run the area and `--record`.)")
        w = max(len(a) for a, _, _ in stale)
        for art, cid, src in sorted(stale):
            print("  %-*s  cites %s  (defined in %s) - CHANGED" % (w, art, cid, src))
    else:
        print("OK: no cited upstream definition has drifted since each artifact was last recorded.")
    if untracked:
        print("\n%d artifact(s) not yet in the lock (run `--record` to baseline): %s"
              % (len(untracked), ", ".join(untracked[:8]) + (" …" if len(untracked) > 8 else "")))
    return 1 if (stale and strict) else 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--strict"]
    strict = "--strict" in sys.argv
    if args and args[0] == "--record":
        sys.exit(record(args[1:]))
    sys.exit(check(strict))
