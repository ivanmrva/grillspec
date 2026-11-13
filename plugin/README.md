# Grill Spec System (`grillspec`)

A plugin for Claude Code and Codex that helps you build software from a specification you can trust. It interviews you about what you want to build (or questions the documents you already have), writes down what the product must do and the decisions that are costly to reverse, breaks the work into tasks an agent can build one at a time, and then drives the coding test-first, checking each task against the code and tests. It keeps the spec as small as the project needs: a solo, pre-launch product gets a thin one.

One conductor skill routes the work across 44 focused skills. Small tools check the spec's structure and whether a task that claims to be done really is.

This directory is the authoring source. Release users install the bundle generated in `dist/marketplace/`.

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

Open `/plugins` in the Codex CLI (or Settings > Plugins in the IDE), select the marketplace, and install Grill Spec. Start a new session and invoke `$grillspec:grill-spec-conductor`.

You can also invoke one skill directly, for example `/grillspec:grill-ddd` in Claude Code or `$grillspec:grill-ddd` in Codex.

## First session

The conductor asks two things once and stores them in `.grillspec/project.json`:

| Setting | Values | Meaning |
|---|---|---|
| `profile` | `lite` · `standard` · `regulated` | how much spec the project carries; the conductor recommends the smallest that fits |
| `delivery` | `trunk` · `pr` | whether work lands on the default branch with local verification, or through a pull request with the full gate in CI |

Both can be raised later. [docs/HOW-IT-WORKS.md](docs/HOW-IT-WORKS.md) explains them.

## What it adds to your project

The plugin installs no global hooks. In a project it works on, it keeps its own state under `.grillspec/` (the settings file, a copy of the tools the hooks run, waivers) and adds two hooks:

- a git pre-commit hook that blocks a commit which breaks the spec's structure, or marks a task done that the code and tests do not back;
- an edit hook, wired into `.claude/settings.json` and `.codex/hooks.json` by `tools/install_exec_gates.py`, that denies an edit which adds a skipped test or a fake in production code.

Commit `.grillspec/tools/` and both hook configurations so every checkout has them. Codex users review and trust the project hook through `/hooks`.

`AGENTS.md` is the one project guide for coding agents; `CLAUDE.md` contains only `@AGENTS.md`, so sessions in either host read the same instructions.

## Individual skills

The build emits each worker skill as a self-contained Agent Skill in `dist/skills/`: `SKILL.md`, the shared method files it loads, the scripts it needs, and `agents/openai.yaml` metadata.

```bash
python3 build/build.py skills
cp -r dist/skills/grill-ddd ~/.claude/skills/  # Claude Code
cp -r dist/skills/grill-ddd ~/.agents/skills/  # Codex
```

The method files are defined once under `grill-shared/`; the build bundles what each skill needs.

## Editing and releasing

Edit this source, then check and build from the repository root:

```bash
python3 plugin/tools/selfcheck.py plugin
python3 build/build.py --zip
```

Keep `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` on the same version, update `CHANGELOG.md`, and publish `dist/marketplace/plugins/grillspec/` at the root of the repository's `marketplace` branch. The marketplace catalogs stay on `main`.

## Docs

| Page | Covers |
|---|---|
| [docs/HOW-IT-WORKS.md](docs/HOW-IT-WORKS.md) | profiles, delivery modes, stages, tasks, tools |
| [docs/WORKING.md](docs/WORKING.md) | working fast; unattended building |
| [docs/SPEC-CHECKS.md](docs/SPEC-CHECKS.md) | every automated check |
| [docs/skills/](docs/skills/README.md) | a guide per skill |
| [docs/DEPENDENCY-GRAPH.md](docs/DEPENDENCY-GRAPH.md) | what each area reads and produces |
| [docs/LIVE-TEST.md](docs/LIVE-TEST.md) | checking a live install |
