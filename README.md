# Grill Spec System (`grillspec`)

A dual-host plugin for spec-driven engineering. It interviews an idea—or grills existing docs—into
a Domain-Driven Design specification, derives architecture and a task graph, and runs the build loop.
One conductor coordinates 46 focused worker skills; deterministic tools validate the spec and guard
derived artifacts.

This directory is the canonical authoring source. Release users should consume the portable bundle
generated in `dist/marketplace/`.

## Install

Claude Code:

```text
/plugin marketplace add ivanmrva/grillspec
/plugin install grillspec@ivanmrva
/reload-plugins
```

Start with `/grillspec:grill-spec-conductor`.

Codex:

```bash
codex plugin marketplace add ivanmrva/grillspec
```

Open `/plugins` in Codex CLI (or Settings > Plugins in the IDE), select the marketplace, and install
Grill Spec. Start a new session and invoke `$grillspec:grill-spec-conductor`.

You can also invoke a focused skill directly, for example `/grillspec:grill-ddd` in Claude Code or
`$grillspec:grill-ddd` in Codex.

## Individual skills

The build emits each worker as a self-contained Agent Skill in `dist/skills/`. A generated folder
contains standard `SKILL.md` frontmatter, its transitive references, required scripts, and
`agents/openai.yaml` policy/UI metadata.

```bash
python3 build/build.py skills
cp -r dist/skills/grill-ddd ~/.claude/skills/  # Claude Code
cp -r dist/skills/grill-ddd ~/.agents/skills/  # Codex
```

The canonical engines remain defined once under `grill-shared/`; the build resolves and bundles only
what each portable skill needs.

## Project-local governance

The plugin installs no global hooks. Execution skills run `tools/install_exec_gates.py`, which
vendors the gate once under `.grillspec/tools/` and merges equivalent `PreToolUse` adapters into:

- `.claude/settings.json` for Claude Code
- `.codex/hooks.json` for Codex

All other GrillSpec-owned project state—tools, locks, waivers, gate configuration, and transient
gate records—lives under `.grillspec/`.

The gate enforces red-before-green, prevents unsupported done claims, and rejects newly introduced
test skips or production fakes. Both host adapters execute the one copy under `.grillspec/tools/`;
commit that shared tool tree and both hook configurations so worktrees inherit them. Codex users
should review and trust the project hook through `/hooks`.

The walking skeleton also installs the repository-scoped git pre-commit governance hook and CI
checks. `AGENTS.md` is the canonical project guide; `CLAUDE.md` contains only `@AGENTS.md`, so
ordinary sessions in either host receive one identical instruction source.

## Editing and releasing

Edit only this canonical source, then validate and build:

```bash
python3 tools/selfcheck.py
python3 ../build/build.py --zip
```

Keep `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` on the same version, update
`CHANGELOG.md`, and publish `dist/marketplace/plugins/grillspec/` at the root of the repository's
`marketplace` branch. The marketplace catalogs stay on `main`.

## Docs

- `docs/skills/` — per-skill guides and catalog
- `docs/HOW-IT-WORKS.md` — stages, tools, and execution loop
- `docs/LIVE-TEST.md` — live behavior verification
- `docs/WORKING.md` — working notes
