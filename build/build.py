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

  dist/claude/        the whole system as a Claude Code plugin + marketplace.

  dist/codex/         the same system as a Codex plugin + native marketplace.

  dist/marketplace/   a combined release archive: both marketplace manifests point at
                      one dual-host portable plugin bundle. Publish its plugins/grillspec/
                      directory at the root of the repository's marketplace branch.

  dist/plugins/<c>/   OPTIONAL per-cluster plugins (e.g. one per blog post). MIT.
                      Same content as the matching skill-database entries, but packaged
                      as installable plugins for the managed /plugin install experience.
                      Configure the set in CLUSTERS below.

Usage:
  python build/build.py                # build every target
  python build/build.py skills         # just the skill database
  python build/build.py claude         # just the Claude Code plugin
  python build/build.py codex          # just the Codex plugin
  python build/build.py marketplace    # combined Claude Code + Codex release repo
  python build/build.py full           # compatibility alias: both full plugins
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

SHARED_REF   = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/grill-shared/([A-Za-z0-9_-]+\.(?:md|json))")
SHARED_PREFIX = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/grill-shared/")
TOOL_PREFIX   = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/tools/")
DOC_PREFIX    = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/docs/")

# Standalone skills cannot depend on a plugin install root. These are the deterministic tools
# referenced by the skill profiles and shared engines. At 160 KB total, bundling the set into a
# skill that needs tooling is smaller and safer than maintaining a fragile Python-import resolver.
PORTABLE_TOOLS = (
    "check_freshness.py", "check_task_record.py", "gate_exec.py", "guard_derived.py",
    "impact.py", "install_exec_gates.py", "lint_spec.py", "plugin_feedback.py",
)

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

def all_skills():
    return sorted(d.name for d in SKILLS.iterdir() if d.is_dir())

def to_sibling(text):
    """Rewrite ${CLAUDE_PLUGIN_ROOT}/grill-shared/X.md -> X.md (engine bundled alongside)."""
    return SHARED_PREFIX.sub("", text)

def portable_frontmatter(text):
    """Keep the Agent Skills standard core; product-specific policy is emitted separately."""
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return text
    out = [lines[0]]
    i = 1
    while i < len(lines):
        line = lines[i]
        if line == "---":
            out.extend(lines[i:])
            return "\n".join(out) + ("\n" if text.endswith("\n") else "")
        if re.match(r"^(argument-hint|disable-model-invocation):", line):
            i += 1
            continue
        out.append(line)
        i += 1
    return text

def portable_text(text):
    """Render plugin-root references as resources relative to the installed skill root."""
    text = portable_frontmatter(text)
    text = SHARED_PREFIX.sub("references/", text)
    text = TOOL_PREFIX.sub("scripts/", text)
    text = DOC_PREFIX.sub("references/", text)
    return text

def _resource_note(text):
    marker = "<!-- grillspec-portable-resources -->"
    if marker in text:
        return text
    m = re.match(r"^(---\n.*?\n---\n)", text, re.S)
    if not m:
        return text
    note = ("\n" + marker + "\n"
            "> Resource paths in this skill are relative to this installed skill directory. "
            "Resolve `references/...` and `scripts/...` from that directory, not from the project "
            "working directory; use an absolute path when executing a bundled script.\n")
    return text[:m.end()] + note + text[m.end():]

def _display_name(name):
    return " ".join(p.upper() if p in {"api", "ddd", "ml", "ui", "ux"} else p.title()
                    for p in name.split("-"))

def _short_description(description):
    plain = re.sub(r"[`*_#]", "", description).strip()
    if len(plain) > 61:
        plain = plain[:61].rsplit(" ", 1)[0].rstrip(".,;:") + "…"
    if len(plain) < 25:
        plain = (plain + " workflow for Grill Spec").strip()
    return plain[:64]

def openai_yaml(name, description, allow_implicit):
    prompt = f"Use ${name} to {description[:1].lower() + description[1:]}"
    if len(prompt) > 180:
        prompt = prompt[:177].rsplit(" ", 1)[0] + "…"
    return ("interface:\n"
            f"  display_name: {json.dumps(_display_name(name))}\n"
            f"  short_description: {json.dumps(_short_description(description))}\n"
            f"  default_prompt: {json.dumps(prompt)}\n"
            "policy:\n"
            f"  allow_implicit_invocation: {'true' if allow_implicit else 'false'}\n")

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
python build/build.py claude     # only the Claude Code plugin
python build/build.py codex      # only the Codex plugin
python build/build.py full       # both full-system plugins
python build/build.py plugins    # only the cluster plugins
```

| Target  | Output              | What it is                                                   | License    |
| :------ | :------------------ | :----------------------------------------------------------- | :--------- |
| skills  | `dist/skills/`      | portable standalone Agent Skills for Claude Code and Codex   | MIT        |
| claude  | `dist/claude/`      | the whole system as a Claude Code plugin + marketplace       | Apache-2.0 |
| codex   | `dist/codex/`       | the whole system as a Codex plugin + native marketplace      | Apache-2.0 |
| marketplace | `dist/marketplace/` | combined dual-host marketplace archive                 | Apache-2.0 |
| plugins | `dist/plugins/<c>/` | optional dual-host per-cluster plugins (one per blog post) | MIT        |

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

Spec-driven engineering for Claude Code and Codex: interview an idea (or existing docs) into a complete
Domain-Driven Design spec, derive the architecture and task breakdown from it, then run the build
loop. One conductor orchestrates {len(names)} worker skills; deterministic tools keep the spec
consistent. Apache-2.0 (system) / MIT (public skills).

This guide covers **how to generate** every artifact and **how to use** each one.

{_PIPELINE_MD}
## Use it - three ways to consume the system

**1. Individual skills** (the skill database, `dist/skills/`). Copy one folder and use it alone:
```
cp -r dist/skills/grill-ddd ~/.claude/skills/        # Claude Code, personal
cp -r dist/skills/grill-ddd ~/.agents/skills/        # Codex, personal
```
Each folder is self-contained (`SKILL.md` + references/scripts). Invoke with `/grill-ddd` in
Claude Code or `$grill-ddd` in Codex. No plugin required.

**2. The whole system** (`dist/claude/` or `dist/codex/`). Install once:
```
# Claude Code
/plugin marketplace add ivanmrva/grillspec
/plugin install grillspec@ivanmrva
/reload-plugins

# Codex CLI: add the source, then open /plugins and install Grill Spec
codex plugin marketplace add ivanmrva/grillspec
```
Then drive everything through the conductor - `/grillspec:grill-spec-conductor` in Claude Code or
`$grillspec:grill-spec-conductor` in Codex - which scans the
spec, recommends the next step, hands each worker its input and target, runs the linters, and
propagates changes.

**3. A blog-post cluster** (optional plugins, `dist/plugins/<c>/`). The same skills, packaged as
dual-host plugins for a narrower install.

{_WORKFLOW_MD}
## Reference - every skill

{_catalog(names)}
"""

def skills_guide(names):
    return f"""# Skill Collection - User Guide

{len(names)} standalone, individually-usable Agent Skills for Claude Code and Codex. Each folder is
self-contained: `SKILL.md`, references, required scripts, and product metadata. MIT (copy-and-own).

## Use a skill
```
cp -r <skill-folder> ~/.claude/skills/               # Claude Code, personal
cp -r <skill-folder> <repo>/.claude/skills/          # Claude Code, project
cp -r <skill-folder> ~/.agents/skills/               # Codex, personal
cp -r <skill-folder> <repo>/.agents/skills/          # Codex, project
```
Invoke it with `/<skill>` in Claude Code or `$<skill>` in Codex, or describe the task and let the
agent match its description. Hand a skill the upstream artifact(s) it needs and it produces its one
output. No plugin and no other skills required.

## Chain them by hand
The skills compose through documents - run one, feed its output into the next (e.g. `grill-ddd` ->
`derive-functional` -> `derive-tasks` -> `implement-task`). For automatic orchestration with gates
and propagation, use the full-system plugin instead.

## Skills

{_catalog(names)}
"""

def full_guide(names):
    return f"""# Grill Spec System for Claude Code - User Guide

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

def codex_guide(names):
    return f"""# Grill Spec System for Codex - User Guide

The complete spec-driven engineering system: one conductor orchestrating {len(names)} worker skills,
portable bundled references and deterministic tools. Apache-2.0.

## Install
```bash
codex plugin marketplace add ivanmrva/grillspec
```

Open `/plugins` in Codex CLI (or Settings > Plugins in the IDE), select the marketplace, and install
Grill Spec. Start a new session after installation.

Start a new task after installation or update, then invoke the conductor:
```text
$grillspec:grill-spec-conductor
```

Worker skills remain explicitly invocable, for example `$grillspec:grill-ddd`. Resource and script
paths in the Codex bundle are resolved from each installed skill directory.

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

Standalone dual-host plugin bundling: {', '.join('`' + s + '`' for s in skills)}. MIT.

## Install
```
/plugin marketplace add <owner>/{cluster}            # or add it to your marketplace
/plugin install {cluster}@<owner>
/reload-plugins
```
Or load locally to test: `claude --plugin-dir dist/plugins/{cluster}`. For Codex, add the containing
marketplace or place the plugin in a local marketplace, then install it through `/plugins`.

## Use
Invoke a skill with `/{cluster}:<skill>` in Claude Code or `${cluster}:<skill>` in Codex (for example,
`/{cluster}:{first}` or `${cluster}:{first}`). Each skill contains its required references and scripts.

## Skills in this plugin
{cat}
"""

def fresh(d):
    if d.exists(): shutil.rmtree(d)
    d.mkdir(parents=True)
    return d

# ---------------------------------------------------------------- skill database
def build_portable_skill(name, out):
    """Render one self-contained, open-standard skill from the canonical plugin sources."""
    src = SKILLS / name
    source_text = (src / "SKILL.md").read_text(encoding="utf-8")
    bundled = transitive_shared(shared_refs(source_text))
    shared_text = "\n".join(
        (SHARED / f).read_text(encoding="utf-8") for f in bundled if (SHARED / f).is_file())
    extras_text = "\n".join(
        p.read_text(encoding="utf-8") for p in src.rglob("*.md") if p.name != "SKILL.md")
    combined = source_text + "\n" + shared_text + "\n" + extras_text

    d = out / name
    d.mkdir(parents=True, exist_ok=True)
    rendered = _resource_note(portable_text(source_text))
    (d / "SKILL.md").write_text(rendered, encoding="utf-8")

    if bundled:
        refs = d / "references"
        refs.mkdir()
        for f in bundled:
            sp = SHARED / f
            if sp.is_file():
                (refs / f).write_text(portable_text(sp.read_text(encoding="utf-8")),
                                      encoding="utf-8")

    for extra in sorted(src.iterdir()):
        if extra.name in {"SKILL.md", "agents"}:
            continue
        target = d / extra.name
        if extra.is_dir():
            shutil.copytree(extra, target)
            for md in target.rglob("*.md"):
                md.write_text(portable_text(md.read_text(encoding="utf-8")), encoding="utf-8")
        elif extra.suffix == ".md":
            target.write_text(portable_text(extra.read_text(encoding="utf-8")), encoding="utf-8")
        else:
            shutil.copy2(extra, target)

    if "${CLAUDE_PLUGIN_ROOT}/tools/" in combined:
        scripts = d / "scripts"
        scripts.mkdir()
        for fn in PORTABLE_TOOLS:
            shutil.copy2(PLUGIN / "tools" / fn, scripts / fn)

    if "${CLAUDE_PLUGIN_ROOT}/docs/DEPENDENCY-GRAPH.md" in combined:
        refs = d / "references"
        refs.mkdir(exist_ok=True)
        shutil.copy2(PLUGIN / "docs" / "DEPENDENCY-GRAPH.md", refs / "DEPENDENCY-GRAPH.md")

    agents = d / "agents"
    agents.mkdir(exist_ok=True)
    description = _description(source_text)
    allow_implicit = "disable-model-invocation: true" not in source_text
    (agents / "openai.yaml").write_text(
        openai_yaml(name, description, allow_implicit), encoding="utf-8")
    (d / "LICENSE").write_text(MIT, encoding="utf-8")

    residual = [str(p.relative_to(d)) for p in d.rglob("*.md")
                if "${CLAUDE_PLUGIN_ROOT}" in p.read_text(encoding="utf-8")]
    if residual:
        raise RuntimeError(f"portable skill {name} retains plugin-root references: {residual}")

def build_skills():
    out = fresh(DIST / "skills")
    names = workers()
    for name in names:
        build_portable_skill(name, out)
    (out / "LICENSE").write_text(MIT, encoding="utf-8")
    (out / "README.md").write_text(_skills_readme(names), encoding="utf-8")
    (out / "GUIDE.md").write_text(skills_guide(names), encoding="utf-8")
    print(f"  skills database: {len(names)} standalone skills (+ GUIDE.md) -> {out}")

def _skills_readme(names):
    L = ["# Grill Spec - Skill Collection", "",
         "Portable, standalone Agent Skills for Claude Code and Codex.",
         "Each folder is self-contained: `SKILL.md`, references, required scripts, and metadata.",
         "Copy any one folder into the skills directory for your agent and it works on its own.", "",
         "MIT licensed (copy-and-own).", "",
         f"## Skills ({len(names)})", ""]
    L += [f"- `{n}/`" for n in names]
    L += ["", "## Use one", "```bash", "cp -r <skill-folder> ~/.claude/skills/  # Claude Code",
          "cp -r <skill-folder> ~/.agents/skills/  # Codex", "```",
          "Invoke it with `/<skill>` in Claude Code or `$<skill>` in Codex.",
          "", "_Generated by `build/build.py` in the Grill Spec source project - do not hand-edit._"]
    return "\n".join(L) + "\n"

# ------------------------------------------------------------ full-system plugins
def claude_marketplace(ver, source):
    return {
        "name": OWNER,
        "description": "Grill Spec plugins for spec-driven software engineering.",
        "metadata": {"description": "Grill Spec plugins for spec-driven software engineering."},
        "owner": {"name": "Ivan Mrva", "url": f"https://github.com/{OWNER}"},
        "plugins": [{
            "name": PLUGIN_NAME,
            "source": source,
            "version": ver,
            "description": (f"Spec-driven engineering system: a conductor plus {len(workers())} "
                            "grilling/derivation/execution skills and deterministic spec linters. "
                            "Turns an idea or existing docs into a complete DDD spec, derives "
                            "architecture and tasks, and runs the build loop."),
            "keywords": ["spec-driven", "domain-driven-design", "requirements", "architecture"],
        }],
    }

def codex_manifest(name=PLUGIN_NAME, ver=None, description=None, license_id="Apache-2.0"):
    ver = ver or version()
    description = description or (
        "Spec-driven engineering from idea and requirements through architecture, tasks, "
        "implementation, verification, and release.")
    return {
        "name": name,
        "version": ver,
        "description": description,
        "author": {"name": "Ivan Mrva", "url": f"https://github.com/{OWNER}"},
        "homepage": f"https://github.com/{OWNER}/{PLUGIN_NAME}",
        "repository": f"https://github.com/{OWNER}/{PLUGIN_NAME}",
        "license": license_id,
        "keywords": ["spec-driven", "domain-driven-design", "requirements", "architecture"],
        "skills": "./skills/",
        "interface": {
            "displayName": "Grill Spec System" if name == PLUGIN_NAME else _display_name(name),
            "shortDescription": "Turn ideas into implementation-ready specifications",
            "longDescription": description,
            "developerName": "Ivan Mrva",
            "category": "Productivity",
            "capabilities": ["Read", "Write"],
            "websiteURL": f"https://github.com/{OWNER}/{PLUGIN_NAME}",
            "defaultPrompt": [
                "Turn this idea into an implementation-ready specification.",
                "Derive the architecture and task plan from the current spec.",
                "Continue the next ready Grill Spec workflow step.",
            ],
        },
    }

def build_claude():
    out = fresh(DIST / "claude")
    shutil.copytree(PLUGIN, out / PLUGIN_NAME,
                    ignore=shutil.ignore_patterns("__pycache__", "dist", ".git"))
    ver = version()
    marketplace = claude_marketplace(ver, f"./{PLUGIN_NAME}")
    (out / ".claude-plugin").mkdir()
    (out / ".claude-plugin" / "marketplace.json").write_text(
        json.dumps(marketplace, indent=2) + "\n", encoding="utf-8")
    if (PLUGIN / "LICENSE").exists():
        shutil.copy2(PLUGIN / "LICENSE", out / "LICENSE")
    (out / "README.md").write_text(_full_readme(ver), encoding="utf-8")
    (out / "GUIDE.md").write_text(full_guide(workers()), encoding="utf-8")
    print(f"  Claude plugin (v{ver}, Apache-2.0, + GUIDE.md) -> {out}")

def build_codex():
    out = fresh(DIST / "codex")
    plugin_out = out / "plugins" / PLUGIN_NAME
    shutil.copytree(PLUGIN, plugin_out, ignore=shutil.ignore_patterns(
        "__pycache__", "dist", ".git", "skills", "agents", ".claude-plugin", ".codex-plugin"))
    skills_out = plugin_out / "skills"
    skills_out.mkdir()
    for name in all_skills():
        build_portable_skill(name, skills_out)

    manifest_dir = plugin_out / ".codex-plugin"
    manifest_dir.mkdir()
    manifest_dir.joinpath("plugin.json").write_text(
        json.dumps(codex_manifest(), indent=2) + "\n", encoding="utf-8")

    marketplace_dir = out / ".agents" / "plugins"
    marketplace_dir.mkdir(parents=True)
    marketplace = {
        "name": OWNER,
        "interface": {"displayName": "Ivan Mrva"},
        "plugins": [{
            "name": PLUGIN_NAME,
            "source": {"source": "local", "path": f"./plugins/{PLUGIN_NAME}"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity",
        }],
    }
    marketplace_dir.joinpath("marketplace.json").write_text(
        json.dumps(marketplace, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(PLUGIN / "LICENSE", out / "LICENSE")
    (out / "README.md").write_text(_codex_readme(version()), encoding="utf-8")
    (out / "GUIDE.md").write_text(codex_guide(workers()), encoding="utf-8")
    print(f"  Codex plugin (v{version()}, Apache-2.0, + GUIDE.md) -> {out}")

def build_marketplace():
    """Build one publishable repository consumed by both Claude Code and Codex."""
    out = fresh(DIST / "marketplace")
    plugin_out = out / "plugins" / PLUGIN_NAME
    shutil.copytree(PLUGIN, plugin_out, ignore=shutil.ignore_patterns(
        "__pycache__", "dist", ".git", "skills", ".claude-plugin", ".codex-plugin"))
    skills_out = plugin_out / "skills"
    skills_out.mkdir()
    for name in all_skills():
        build_portable_skill(name, skills_out)

    shutil.copytree(PLUGIN / ".claude-plugin", plugin_out / ".claude-plugin")
    codex_dir = plugin_out / ".codex-plugin"
    codex_dir.mkdir()
    codex_dir.joinpath("plugin.json").write_text(
        json.dumps(codex_manifest(), indent=2) + "\n", encoding="utf-8")

    claude_dir = out / ".claude-plugin"
    claude_dir.mkdir()
    claude_dir.joinpath("marketplace.json").write_text(
        json.dumps(claude_marketplace(version(), f"./plugins/{PLUGIN_NAME}"), indent=2) + "\n",
        encoding="utf-8")
    codex_market = out / ".agents" / "plugins"
    codex_market.mkdir(parents=True)
    codex_market.joinpath("marketplace.json").write_text(json.dumps({
        "name": OWNER,
        "interface": {"displayName": "Ivan Mrva"},
        "plugins": [{
            "name": PLUGIN_NAME,
            "source": {"source": "local", "path": f"./plugins/{PLUGIN_NAME}"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity",
        }],
    }, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(PLUGIN / "LICENSE", out / "LICENSE")
    (out / "README.md").write_text(_marketplace_readme(version()), encoding="utf-8")
    (out / "GUIDE.md").write_text(master_guide(workers()), encoding="utf-8")
    print(f"  dual-host marketplace (v{version()}, Apache-2.0) -> {out}")

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

def _codex_readme(ver):
    return (f"# Grill Spec System (`{PLUGIN_NAME}`) for Codex\n\n"
            "The complete spec-driven engineering system as a Codex plugin: one conductor, "
            f"{len(workers())} worker skills, bundled references, and deterministic tools.\n\n"
            "## Install\n```bash\n"
            f"codex plugin marketplace add {OWNER}/{PLUGIN_NAME}\n"
            "```\n\n"
            "Then open `/plugins` in Codex CLI (or Settings > Plugins in the IDE), select this "
            "marketplace, and install Grill Spec. Start a new session after installation.\n\n"
            "## Use\n```text\n"
            f"${PLUGIN_NAME}:grill-spec-conductor\n"
            "```\n\n"
            f"Version {ver}. Apache-2.0.\n")

def _marketplace_readme(ver):
    return (f"# Grill Spec dual-host marketplace\n\n"
            "One portable plugin bundle for Claude Code and Codex, generated from the same canonical "
            "skills.\n\n"
            "## Claude Code\n```text\n"
            f"/plugin marketplace add {OWNER}/{PLUGIN_NAME}\n"
            f"/plugin install {PLUGIN_NAME}@{OWNER}\n"
            "/reload-plugins\n```\n\n"
            "## Codex\n```bash\n"
            f"codex plugin marketplace add {OWNER}/{PLUGIN_NAME}\n"
            "```\n"
            "Then open `/plugins` in Codex CLI (or Settings > Plugins in the IDE), install Grill Spec, "
            "and start a new session.\n\n"
            f"Version {ver}. Apache-2.0.\n")

# ------------------------------------------------------------ per-cluster plugins
def build_plugins():
    base = fresh(DIST / "plugins")
    for cluster, skills in CLUSTERS.items():
        out = base / cluster
        (out / ".claude-plugin").mkdir(parents=True)
        (out / ".codex-plugin").mkdir(parents=True)
        for s in skills:
            src = SKILLS / s
            if not (src / "SKILL.md").exists():
                sys.exit(f"ERROR: cluster '{cluster}' names unknown skill '{s}'")
            build_portable_skill(s, out / "skills")
        (out / ".claude-plugin" / "plugin.json").write_text(json.dumps({
            "name": cluster, "version": "1.0.0",
            "description": f"Spec-driven engineering skill(s): {', '.join(skills)}.",
            "keywords": ["spec-driven", "ddd", "claude-code", "skills"],
            "license": "MIT",
        }, indent=2) + "\n", encoding="utf-8")
        (out / ".codex-plugin" / "plugin.json").write_text(json.dumps(
            codex_manifest(cluster, "1.0.0", f"Spec-driven engineering skill(s): {', '.join(skills)}.", "MIT"),
            indent=2) + "\n", encoding="utf-8")
        (out / "LICENSE").write_text(MIT, encoding="utf-8")
        (out / "README.md").write_text(
            f"# {cluster}\n\nStandalone Claude Code and Codex plugin: **{', '.join(skills)}**.\n"
            "Each skill bundles its required references and scripts. MIT licensed. See GUIDE.md.\n",
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
    if targets & {"all", "full", "claude"}: build_claude()
    if targets & {"all", "full", "codex"}:  build_codex()
    if targets & {"all", "full", "marketplace"}: build_marketplace()
    if targets & {"all", "plugins"}: build_plugins()
    (DIST / "GUIDE.md").write_text(master_guide(workers()), encoding="utf-8")
    print(f"  master user guide -> {DIST / 'GUIDE.md'}")
    if do_zip:
        if (DIST / "skills").exists():
            zip_tree(DIST / "skills", DIST / "grillspec-skills.zip")
        if (DIST / "claude").exists():
            zip_tree(DIST / "claude", DIST / "grillspec-claude-plugin.zip")
            zip_tree(DIST / "claude", DIST / "grillspec-full-system.zip")
        if (DIST / "codex").exists():
            zip_tree(DIST / "codex", DIST / "grillspec-codex-plugin.zip")
        if (DIST / "marketplace").exists():
            zip_tree(DIST / "marketplace", DIST / "grillspec-marketplace.zip")
        if (DIST / "plugins").exists():
            for c in sorted((DIST / "plugins").iterdir()):
                if c.is_dir():
                    zip_tree(c, DIST / f"grillspec-plugin-{c.name}.zip")
        print("  zipped artifacts into dist/")

if __name__ == "__main__":
    main(sys.argv[1:])
