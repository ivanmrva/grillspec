#!/usr/bin/env python3
"""
build.py - the single build pipeline for the Grill Spec System.

ONE source of truth: plugin/  (skills + grill-shared engines + tools + agents + hooks).
This pipeline produces every distribution artifact under dist/, reusing the shared
engines instead of duplicating them in source:

  dist/skills/        the SKILL DATABASE - every worker skill as a self-contained,
                      individually-usable plain skill (SKILL.md + the one engine it
                      loads, bundled as a sibling). MIT. Push these into the public
                      skills repo; the pipeline regenerates / overrides that directory.

  dist/full-system/   the whole system as ONE installable plugin + marketplace
                      (the conductor + all workers + engines + tools + agents +
                      hooks). Apache-2.0. This is plugin/ verbatim under a marketplace
                      wrapper, so it stays byte-identical to the working plugin.

  dist/plugins/<c>/   OPTIONAL per-cluster plugins (e.g. one per blog post). MIT.
                      Same content as the matching skill-database entries, but packaged
                      as installable plugins for the managed /plugin install experience.
                      Configure the set in CLUSTERS below.

Usage:
  python build/build.py                # build every target
  python build/build.py skills         # just the skill database
  python build/build.py full           # just the full-system plugin
  python build/build.py plugins        # just the cluster plugins
  python build/build.py all --zip      # build everything and zip each artifact
"""
import sys, re, json, shutil, zipfile
from pathlib import Path

ROOT    = Path(__file__).resolve().parent.parent
PLUGIN  = ROOT / "plugin"
SHARED  = PLUGIN / "grill-shared"
SKILLS  = PLUGIN / "skills"
DIST    = ROOT / "dist"
MIT     = (ROOT / "build" / "licenses" / "MIT.txt").read_text(encoding="utf-8")

CONDUCTOR   = "grill-spec-conductor"   # orchestrator; not an individually-used skill
PLUGIN_NAME = "grillspec"
OWNER       = "ivanmrva"               # marketplace name == GitHub owner

# Which skills become per-cluster plugins (one key => one plugin). Edit freely.
CLUSTERS = {
    "grill-ddd":            ["grill-ddd"],
    "derive-tasks":         ["derive-tasks"],
    "implement-and-review": ["implement-task", "run-tests", "conformance-review"],
}

SHARED_REF   = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/grill-shared/([A-Za-z0-9_-]+\.md)")
SHARED_PREFIX = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/grill-shared/")

def version():
    return json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]

def shared_refs(text):
    return set(SHARED_REF.findall(text))

def transitive_shared(seeds):
    """Every grill-shared/*.md a set of files references, followed transitively."""
    need, seen = set(seeds), set()
    while need - seen:
        f = (need - seen).pop(); seen.add(f)
        p = SHARED / f
        if p.exists():
            need |= shared_refs(p.read_text(encoding="utf-8"))
    return sorted(seen)

def workers():
    return sorted(d.name for d in SKILLS.iterdir() if d.is_dir() and d.name != CONDUCTOR)

def to_sibling(text):
    """Rewrite ${CLAUDE_PLUGIN_ROOT}/grill-shared/X.md -> X.md (engine bundled alongside)."""
    return SHARED_PREFIX.sub("", text)

# --------------------------------------------------------------------- guides
def engine_of(name):
    for r in sorted(shared_refs((SKILLS / name / "SKILL.md").read_text(encoding="utf-8"))):  # sorted = deterministic
        if r.endswith("-engine.md"):
            return r
    return ""

_FAMILY = {
    "grill-engine.md":  "Interview skills (grill-*) - ask you questions, write a spec artifact",
    "derive-engine.md": "Derivation skills (derive-*) - generate strictly from the spec",
    "exec-engine.md":   "Execution & operations - act on code and running systems",
}
_FAMILY_ORDER = list(_FAMILY.values()) + ["Other"]

def _description(text):
    """Extract the frontmatter description (folded or inline). Stdlib only."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return ""
    lines = m.group(1).splitlines(); out = []; i = 0
    while i < len(lines):
        dm = re.match(r"^description:\s*(.*)$", lines[i])
        if dm:
            rest = dm.group(1).strip()
            if rest in (">", ">-", ">+", "|", "|-", "|+", ""):
                i += 1
                while i < len(lines) and (lines[i][:1] in (" ", "\t") or not lines[i].strip()):
                    out.append(lines[i].strip()); i += 1
            else:
                out.append(rest.strip('"').strip("'"))
            break
        i += 1
    return " ".join(x for x in out if x).strip()

def _catalog(names):
    groups = {}
    for n in names:
        groups.setdefault(_FAMILY.get(engine_of(n), "Other"), []).append(n)
    out = []
    for fam in _FAMILY_ORDER:
        if fam not in groups:
            continue
        out.append(f"### {fam}\n")
        for n in sorted(groups[fam]):
            out.append(f"- **`{n}`** - {_description((SKILLS / n / 'SKILL.md').read_text(encoding='utf-8'))}")
        out.append("")
    return "\n".join(out)

_PIPELINE_MD = """## Generate everything (the build pipeline)

Every artifact is produced from the single source in `plugin/` by one command:

```
python build/build.py            # build all targets into dist/
python build/build.py --zip      # ...and zip each one
python build/build.py skills     # only the skill database
python build/build.py full       # only the full-system plugin
python build/build.py plugins    # only the cluster plugins
```

| Target  | Output              | What it is                                               | License    |
| :------ | :------------------ | :------------------------------------------------------- | :--------- |
| skills  | `dist/skills/`      | every worker skill as a standalone, copyable plain skill | MIT        |
| full    | `dist/full-system/` | the whole system as one installable plugin + marketplace | Apache-2.0 |
| plugins | `dist/plugins/<c>/` | optional per-cluster plugins (one per blog post)         | MIT        |

Source lives under `plugin/` - skills in `plugin/skills/`, the three method engines in
`plugin/grill-shared/`. Edit there and rebuild; the engines are defined once and reused by every
artifact. Add or remove cluster plugins via the `CLUSTERS` dict in `build/build.py`.
"""

_WORKFLOW_MD = """## The workflow (full system, end to end)

1. **Discovery & foundation** - `grill-problem-validation`, `grill-product-vision`, and the other
   `grill-*` skills interview you into vision, customers, market, goals, and context.
2. **Domain model** - `grill-ddd` builds the Domain-Driven Design model (the hub).
3. **Requirements** - `derive-functional` projects use-cases/acceptance from the model; the `grill-*`
   requirement skills add quality, data, integration, security, UX, and compliance.
4. **Architecture-readiness gate -> solution** - the `derive-*` skills generate architecture, data,
   API, security, infra/ops, observability, test strategy, and per-module design from the spec.
5. **Delivery prep** - `derive-conventions` + `derive-tasks` produce the build runway and an acyclic
   task DAG (walking-skeleton first).
6. **Execution loop** - per task: `implement-task` -> `run-tests` -> `conformance-review` (or
   `autorun` for the whole queue). Code lives in the project source tree, never in the spec.
7. **Operate & maintain** - `deploy-release`, `migrate-data`, `operate-incident`, `diagnose`;
   learnings feed back to discovery.

The conductor enforces the ordering and the readiness gates; any skill can also be run directly.
"""

def master_guide(names):
    return f"""# Grill Spec System - User Guide

Spec-driven engineering for Claude Code: interview an idea (or existing docs) into a complete
Domain-Driven Design spec, derive the architecture and task breakdown from it, then run the build
loop. One conductor orchestrates {len(names)} worker skills; deterministic tools keep the spec
consistent. Apache-2.0 (system) / MIT (public skills).

This guide covers **how to generate** every artifact and **how to use** each one.

{_PIPELINE_MD}
## Use it - three ways to consume the system

**1. Individual skills** (the skill database, `dist/skills/`). Copy one folder and use it alone:
```
cp -r dist/skills/grill-ddd ~/.claude/skills/        # personal
# or into a repo:  cp -r dist/skills/grill-ddd <repo>/.claude/skills/
```
Each folder is self-contained (`SKILL.md` + its method engine). Invoke with `/grill-ddd` or let
Claude load it by description. No plugin required.

**2. The whole system** (the full-system plugin, `dist/full-system/`). Install once:
```
/plugin marketplace add ivanmrva/grillspec
/plugin install grillspec@ivanmrva
/reload-plugins
```
Then drive everything through the conductor - `/grillspec:grill-spec-conductor` - which scans the
spec, recommends the next step, hands each worker its input and target, runs the linters, and
propagates changes.

**3. A blog-post cluster** (optional plugins, `dist/plugins/<c>/`). The same skills, packaged for
`/plugin install` with slash commands - use when you want a one-command install for a post's skills.

{_WORKFLOW_MD}
## Reference - every skill

{_catalog(names)}
"""

def skills_guide(names):
    return f"""# Skill Collection - User Guide

{len(names)} standalone, individually-usable Claude Code skills for spec-driven engineering. Each
folder is self-contained: a `SKILL.md` plus the method engine it loads. MIT (copy-and-own).

## Use a skill
```
cp -r <skill-folder> ~/.claude/skills/               # personal, every project
# or:  cp -r <skill-folder> <repo>/.claude/skills/    # project, shared via the repo
```
In Claude Code, invoke it with `/<skill>` (e.g. `/grill-ddd`), or just describe your task and Claude
loads it from its description. Hand a skill the upstream artifact(s) it needs and it produces its one
output. No plugin and no other skills required.

## Chain them by hand
The skills compose through documents - run one, feed its output into the next (e.g. `grill-ddd` ->
`derive-functional` -> `derive-tasks` -> `implement-task`). For automatic orchestration with gates
and propagation, use the full-system plugin instead.

## Skills

{_catalog(names)}
"""

def full_guide(names):
    return f"""# Grill Spec System (full plugin) - User Guide

The complete spec-driven engineering system: one conductor orchestrating {len(names)} worker skills,
three shared method engines, deterministic spec linters, two subagents, and governance hooks.
Apache-2.0.

## Install
```
/plugin marketplace add ivanmrva/grillspec
/plugin install grillspec@ivanmrva
/reload-plugins
```

## Use
Drive everything through the conductor:
```
/grillspec:grill-spec-conductor
```
It scans the spec, recommends the next step, hands each worker its input and target location, runs
the linters (`lint_spec`, `guard_derived`) and change propagation, and keeps the cross-area views
consistent. Any individual skill can also be invoked directly with `/grillspec:<skill>`.

{_WORKFLOW_MD}
## Reference - every skill

{_catalog(names)}
"""

def cluster_guide(cluster, skills):
    cat = "\n".join(
        f"- **`{s}`** - {_description((SKILLS / s / 'SKILL.md').read_text(encoding='utf-8'))}"
        for s in skills)
    first = skills[0]
    return f"""# {cluster} - User Guide

Standalone Claude Code plugin bundling: {', '.join('`' + s + '`' for s in skills)}. MIT.

## Install
```
/plugin marketplace add <owner>/{cluster}            # or add it to your marketplace
/plugin install {cluster}@<owner>
/reload-plugins
```
Or load locally to test: `claude --plugin-dir dist/plugins/{cluster}`.

## Use
Invoke a skill with `/{cluster}:<skill>` (e.g. `/{cluster}:{first}`), or describe your task and Claude
picks it up. Each skill loads its method engine from the bundled `grill-shared/`.

## Skills in this plugin
{cat}
"""

def fresh(d):
    if d.exists(): shutil.rmtree(d)
    d.mkdir(parents=True)
    return d

# ---------------------------------------------------------------- skill database
def build_skills():
    out = fresh(DIST / "skills")
    names = workers()
    for name in names:
        src = SKILLS / name
        skill_text = (src / "SKILL.md").read_text(encoding="utf-8")
        bundled = transitive_shared(shared_refs(skill_text))   # the engine(s) it loads
        d = out / name; d.mkdir()
        (d / "SKILL.md").write_text(to_sibling(skill_text), encoding="utf-8")
        for f in bundled:
            sp = SHARED / f
            if sp.exists():
                (d / f).write_text(to_sibling(sp.read_text(encoding="utf-8")), encoding="utf-8")
        if (src / "examples.md").exists():
            shutil.copy2(src / "examples.md", d / "examples.md")
        (d / "LICENSE").write_text(MIT, encoding="utf-8")
        # safety net: nothing should still point at a plugin-only path
        residual = [p.name for p in d.glob("*.md")
                    if "${CLAUDE_PLUGIN_ROOT}" in p.read_text(encoding="utf-8")]
        if residual:
            print(f"  WARN  {name}: residual ${{CLAUDE_PLUGIN_ROOT}} in {residual}")
    (out / "LICENSE").write_text(MIT, encoding="utf-8")
    (out / "README.md").write_text(_skills_readme(names), encoding="utf-8")
    (out / "GUIDE.md").write_text(skills_guide(names), encoding="utf-8")
    print(f"  skills database: {len(names)} standalone skills (+ GUIDE.md) -> {out}")

def _skills_readme(names):
    L = ["# Grill Spec - Skill Collection", "",
         "Standalone, individually-usable Claude Code skills for spec-driven engineering.",
         "Each folder is self-contained: a `SKILL.md` plus the method engine it loads. Copy any",
         "single folder into `~/.claude/skills/` (personal) or a repo's `.claude/skills/` (project)",
         "and it works on its own - no plugin and no other skills required.", "",
         "MIT licensed (copy-and-own).", "",
         f"## Skills ({len(names)})", ""]
    L += [f"- `{n}/`" for n in names]
    L += ["", "## Use one", "```", "cp -r <skill-folder> ~/.claude/skills/", "```",
          "Then invoke it in Claude Code with `/<skill>`, or let Claude pick it up from its description.",
          "", "_Generated by `build/build.py` in the Grill Spec source project - do not hand-edit._"]
    return "\n".join(L) + "\n"

# ------------------------------------------------------------ full-system plugin
def build_full():
    out = fresh(DIST / "full-system")
    shutil.copytree(PLUGIN, out / PLUGIN_NAME,
                    ignore=shutil.ignore_patterns("__pycache__", "dist", ".git"))
    ver = version()
    marketplace = {
        "name": OWNER,
        "owner": {"name": "Ivan Mrva", "url": f"https://github.com/{OWNER}"},
        "plugins": [{
            "name": PLUGIN_NAME,
            "source": f"./{PLUGIN_NAME}",
            "version": ver,
            "description": (f"Spec-driven engineering system: a conductor plus {len(workers())} grilling/derivation "
                            "skills and deterministic spec linters. Turns an idea or existing docs into "
                            "a complete DDD spec, derives architecture and tasks, and runs the build loop."),
            "keywords": ["spec-driven", "domain-driven-design", "requirements", "architecture"],
        }],
    }
    (out / ".claude-plugin").mkdir()
    (out / ".claude-plugin" / "marketplace.json").write_text(
        json.dumps(marketplace, indent=2) + "\n", encoding="utf-8")
    if (PLUGIN / "LICENSE").exists():
        shutil.copy2(PLUGIN / "LICENSE", out / "LICENSE")
    (out / "README.md").write_text(_full_readme(ver), encoding="utf-8")
    (out / "GUIDE.md").write_text(full_guide(workers()), encoding="utf-8")
    print(f"  full-system plugin (v{ver}, Apache-2.0, + GUIDE.md) -> {out}")

def _full_readme(ver):
    return (f"# Grill Spec System (`{PLUGIN_NAME}`)\n\n"
            "The complete spec-driven engineering system as a Claude Code plugin: one conductor\n"
            f"orchestrating {len(workers())} grilling/derivation skills, three shared method engines, deterministic\n"
            "spec linters, two subagents, and governance hooks.\n\n"
            "## Install\n```\n"
            f"/plugin marketplace add {OWNER}/{PLUGIN_NAME}\n"
            f"/plugin install {PLUGIN_NAME}@{OWNER}\n"
            "/reload-plugins\n```\n\n"
            "## Use\n```\n"
            f"/{PLUGIN_NAME}:grill-spec-conductor\n```\n\n"
            f"Version {ver}. Apache-2.0.\n")

# ------------------------------------------------------------ per-cluster plugins
def build_plugins():
    base = fresh(DIST / "plugins")
    for cluster, skills in CLUSTERS.items():
        out = base / cluster
        (out / ".claude-plugin").mkdir(parents=True)
        seed = set()
        for s in skills:
            src = SKILLS / s
            if not (src / "SKILL.md").exists():
                sys.exit(f"ERROR: cluster '{cluster}' names unknown skill '{s}'")
            dst = out / "skills" / s; dst.mkdir(parents=True)
            for fn in ("SKILL.md", "examples.md"):
                if (src / fn).exists():
                    shutil.copy2(src / fn, dst / fn)
            seed |= shared_refs((src / "SKILL.md").read_text(encoding="utf-8"))
        bundled = transitive_shared(seed)
        if bundled:
            (out / "grill-shared").mkdir(parents=True)
            for f in bundled:
                shutil.copy2(SHARED / f, out / "grill-shared" / f)
        (out / ".claude-plugin" / "plugin.json").write_text(json.dumps({
            "name": cluster, "version": "1.0.0",
            "description": f"Spec-driven engineering skill(s): {', '.join(skills)}.",
            "keywords": ["spec-driven", "ddd", "claude-code", "skills"],
            "license": "MIT",
        }, indent=2) + "\n", encoding="utf-8")
        (out / "LICENSE").write_text(MIT, encoding="utf-8")
        (out / "README.md").write_text(
            f"# {cluster}\n\nStandalone Claude Code plugin: **{', '.join(skills)}**.\n"
            "Each skill loads its method engine from `grill-shared/`. MIT licensed. See GUIDE.md.\n",
            encoding="utf-8")
        (out / "GUIDE.md").write_text(cluster_guide(cluster, skills), encoding="utf-8")
        print(f"  cluster plugin '{cluster}' ({', '.join(skills)}, + GUIDE.md) -> {out}")

# ----------------------------------------------------------------------- zipping
def zip_tree(d, zpath):
    """Zip the CONTENTS of d at the archive root (so it unzips to a usable repo/plugin)."""
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(d.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                z.write(p, p.relative_to(d))

def main(argv):
    targets = {a for a in argv if not a.startswith("-")} or {"all"}
    do_zip = "--zip" in argv
    DIST.mkdir(exist_ok=True)
    if targets & {"all", "skills"}:  build_skills()
    if targets & {"all", "full"}:    build_full()
    if targets & {"all", "plugins"}: build_plugins()
    (DIST / "GUIDE.md").write_text(master_guide(workers()), encoding="utf-8")
    print(f"  master user guide -> {DIST / 'GUIDE.md'}")
    if do_zip:
        if (DIST / "skills").exists():
            zip_tree(DIST / "skills", DIST / "grillspec-skills.zip")
        if (DIST / "full-system").exists():
            zip_tree(DIST / "full-system", DIST / "grillspec-full-system.zip")
        if (DIST / "plugins").exists():
            for c in sorted((DIST / "plugins").iterdir()):
                if c.is_dir():
                    zip_tree(c, DIST / f"grillspec-plugin-{c.name}.zip")
        print("  zipped artifacts into dist/")

if __name__ == "__main__":
    main(sys.argv[1:])
