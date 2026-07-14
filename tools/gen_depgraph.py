#!/usr/bin/env python3
"""
gen_depgraph.py - render (and validate) the system dependency graph.

Single source of truth: grill-shared/dependencies.json (the CONDUCTOR reads that to know what to hand
each skill). This tool turns it into the human doc docs/DEPENDENCY-GRAPH.md (a stage table + a Mermaid
DAG) and cross-checks it against the rest of the system so the two can't drift:
  - every 'produces_ids' prefix is known to lint_spec.py (TYPES) and is owned by this area's folder
    (lint_spec.py PREFIX_OWNER) - the graph and the linter agree on who mints what;
  - every 'consumes' target is a real area; the graph is acyclic; every 'skill' folder exists.

Usage:
    python3 tools/gen_depgraph.py            # validate + (re)write docs/DEPENDENCY-GRAPH.md
    python3 tools/gen_depgraph.py --check    # validate + verify the committed doc is up to date (no write)

Exit 0 = ok. Exit 1 = a validation error or (in --check) the doc is stale. Stdlib only.
"""
import sys, os, re, json, ast, pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
DEPS = ROOT / "grill-shared" / "dependencies.json"
DOC = ROOT / "docs" / "DEPENDENCY-GRAPH.md"
LINT = ROOT / "tools" / "lint_spec.py"

STAGE_LABEL = {
    "0-discovery": "0 · Discovery", "0-foundation": "0 · Foundation", "1-domain": "1 · Domain",
    "2-requirements": "2 · Requirements", "3-design-system": "3 · Design system", "4-ux": "4 · UX",
    "5-solution": "5 · Solution",
    "6-delivery-prep": "6 · Delivery prep", "7-execution": "7 · Execution", "8-operate": "8 · Operate",
    "9-commercial": "post-launch · Commercial", "any": "Any stage",
}


def load_linter_tables():
    src = LINT.read_text()
    types = set(re.search(r'^TYPES\s*=\s*"([^"]+)"', src, re.M).group(1).split("|"))
    owner = ast.literal_eval(re.search(r"^PREFIX_OWNER\s*=\s*(\{.*?\})", src, re.S | re.M).group(1))
    return types, owner


def validate(data, types, owner):
    errs = []
    areas = data["areas"]
    stages = data["stages"]
    keys = set(areas)
    for st in stages:
        if st not in STAGE_LABEL:
            errs.append(f"stage '{st}' has no STAGE_LABEL entry (render() would KeyError) - add it to STAGE_LABEL")
    for a, m in areas.items():
        if m["stage"] not in stages:
            errs.append(f"{a}: unknown stage '{m['stage']}'")
        for c in m["consumes"]:
            if c not in keys:
                errs.append(f"{a}: consumes unknown area '{c}'")
        for p in m["produces_ids"]:
            if p not in types:
                errs.append(f"{a}: produces_id '{p}' is unknown to lint_spec.py TYPES")
            elif p in owner and not m["folder"].startswith(owner[p]):
                errs.append(f"{a}: claims to produce '{p}-' but lint_spec.py owns it under '{owner[p]}/' (folder='{m['folder']}')")
        if m["kind"] in ("elicit", "derive", "model"):
            if not (ROOT / "skills" / m["skill"] / "SKILL.md").exists():
                errs.append(f"{a}: skill '{m['skill']}' has no skills/{m['skill']}/SKILL.md")
    # acyclicity (DFS)
    WHITE, GREY, BLACK = 0, 1, 2
    color = {a: WHITE for a in keys}

    def dfs(u, stack):
        color[u] = GREY
        for v in areas[u]["consumes"]:
            if color.get(v) == GREY:
                errs.append("cycle: " + " -> ".join(stack + [u, v]))
            elif color.get(v) == WHITE:
                dfs(v, stack + [u])
        color[u] = BLACK
    for a in keys:
        if color[a] == WHITE:
            dfs(a, [])
    return errs


def render(data):
    areas = data["areas"]
    stages = data["stages"]
    ordered = sorted(areas.items(), key=lambda kv: (stages.index(kv[1]["stage"]), kv[0]))
    out = []
    out.append("<!-- scope: the system's static skill-dependency graph | excludes: a project's runtime ID-reference graph (that is impact.py) | format: generated -->")
    out.append("# Dependency graph — what each area consumes & produces\n")
    out.append("**Generated from `grill-shared/dependencies.json` by `tools/gen_depgraph.py` — do not hand-edit.**")
    out.append("The conductor reads the JSON to know, before running an area's skill, which upstream artifacts/IDs to gather and hand it. `Consumes` = the upstream areas it builds from; `Produces` = the stable-ID prefixes it mints.\n")

    # table grouped by stage
    cur = None
    out.append("| Area | Skill | Kind | Consumes (upstream) | Produces (IDs) |")
    out.append("|---|---|---|---|---|")
    for a, m in ordered:
        if m["stage"] != cur:
            cur = m["stage"]
            out.append(f"| **{STAGE_LABEL[cur]}** | | | | |")
        cons = ", ".join(m["consumes"]) or "—"
        prod = ", ".join(p + "-" for p in m["produces_ids"]) or "—"
        out.append(f"| `{a}` | {m['skill']} | {m['kind']} | {cons} | {prod} |")

    # mermaid DAG
    out.append("\n## Diagram\n")
    out.append("```mermaid")
    out.append("flowchart TD")
    nid = lambda a: re.sub(r"[^0-9A-Za-z]", "_", a)        # area node id (starts with a letter)
    sid = lambda s: "stage_" + re.sub(r"[^0-9A-Za-z]", "_", s)  # subgraph id (no dots / leading digit)
    by_stage = {}
    for a, m in ordered:
        by_stage.setdefault(m["stage"], []).append(a)
    for st in stages:
        if st not in by_stage:
            continue
        out.append(f'  subgraph {sid(st)}["{STAGE_LABEL[st]}"]')
        for a in by_stage[st]:
            prod = "<br/>" + " ".join(p + "-" for p in areas[a]["produces_ids"]) if areas[a]["produces_ids"] else ""
            out.append(f'    {nid(a)}["{a}{prod}"]')
        out.append("  end")
    for a, m in ordered:
        for c in m["consumes"]:
            out.append(f"  {nid(c)} --> {nid(a)}")
    out.append("```")
    out.append("")
    return "\n".join(out)


def main():
    check = "--check" in sys.argv[1:]
    data = json.loads(DEPS.read_text())
    types, owner = load_linter_tables()
    errs = validate(data, types, owner)
    if errs:
        print("dependency-graph: VALIDATION FAILED")
        for e in errs:
            print("  -", e)
        return 1
    rendered = render(data)
    if check:
        current = DOC.read_text() if DOC.exists() else ""
        if current.strip() != rendered.strip():
            print("dependency-graph: docs/DEPENDENCY-GRAPH.md is STALE - run `python3 tools/gen_depgraph.py`")
            return 1
        print(f"dependency-graph: OK ({len(data['areas'])} areas, doc up to date)")
        return 0
    DOC.write_text(rendered + "\n", encoding="utf-8")
    print(f"dependency-graph: wrote {DOC.relative_to(ROOT)} ({len(data['areas'])} areas)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
