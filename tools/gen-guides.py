#!/usr/bin/env python3
"""
gen-guides.py - generate a user guide per skill into docs/skills/, plus a catalog index.

Run from the project root:  python3 tools/gen-guides.py
Each guide is built from the skill's own fields (skill_guide.py), so it always matches the skill.
Reading docs/skills/<name>.md is the verification surface: purpose, input, output, and the
"how to tell it did its job" checklist all come straight from the profile.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import skill_guide

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "skills"

CONDUCTOR_BLURB = """# Spec conductor — user guide

**Invoke:** `/grillspec:grill-spec-conductor` — or just describe a spec task; it is model-invocable.

*The orchestrator — the one skill that knows the whole system. The {nworkers} worker skills know nothing about it.*

## What it does
{desc}

## When to use it
When you want the full system to drive end to end. It picks the next area, **hands each worker its input and its exact target slot** in the `spec/` tree, then reads each worker's output to reconcile cross-area views, runs the linter + derived-guard, checks cross-area consistency, and propagates changes downstream. Use a worker skill directly instead when you only want one artifact.

## What it needs
A working repo. On start it runs the linter, scans the tree, and offers a **menu of next actions** (recommended next area, resume, fix cross-area issues, test the riskiest assumption, …). It never starts an area you didn't pick.

## How to run it
`/grillspec:grill-spec-conductor`, then choose from the menu — or state your goal and let it route.

## How to tell it did its job  *(verification)*
- It never silently starts an area you didn't choose.
- The linter (`lint_spec.py`) is green; the derived-guard blocks hand-edits to generated artifacts.
- The three gates (architecture-, implementation-, delivery-readiness) are respected, not skipped.
- The `spec/` tree stays stage-pure (one leaf folder per skill) and cross-area references resolve.
"""

def catalog(rows):
    order = {"conductor": 0, "grill": 1, "derive": 2, "exec": 3}
    head = {"conductor": "Orchestrator", "grill": "Interview skills (grill — ask you, write a spec artifact)",
            "derive": "Derivation skills (derive — generate from recorded input)",
            "exec": "Build / verify skills (exec — do work in the repo)"}
    rows.sort(key=lambda r: (order[r[0]], r[1]))
    out = ["# Skill catalog & user guides", "",
           "One guide per skill. Each is generated from the skill itself, so it always reflects what the skill actually does — and doubles as the verification surface (purpose · input · output · how to tell it worked).", ""]
    cur = None
    for fam, name, title, where in rows:
        if fam != cur:
            out += ["", f"## {head[fam]}", "", "| Skill | Produces | Default output |", "|---|---|---|"]
            cur = fam
        out.append(f"| [`{name}`]({name}.md) | {title} | `{where}` |")
    return "\n".join(out) + "\n"

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    skill_paths = sorted((ROOT / "skills").glob("*/SKILL.md"))
    nworkers = len(skill_paths) - 1   # all skills minus the conductor — keeps the blurb count in sync
    for p in skill_paths:
        name = p.parent.name
        text = p.read_text()
        if name == "grill-spec-conductor":
            title = "Orchestrates the whole system"
            md = CONDUCTOR_BLURB.format(desc=skill_guide._description(text), nworkers=nworkers)
            fam, where = "conductor", "spec/ (whole tree)"
        else:
            title, md = skill_guide.build_guide(name, text)
            fam = skill_guide._family(text)
            kind, where = skill_guide._standalone(text)
            where = (where + "/") if kind == "folder" else (where or "—")
        (OUT / f"{name}.md").write_text(md)
        rows.append((fam, name, title, where))
    (OUT / "README.md").write_text(catalog(rows))
    print(f"generated {len(rows)} guides + catalog -> docs/skills/")

if __name__ == "__main__":
    main()
