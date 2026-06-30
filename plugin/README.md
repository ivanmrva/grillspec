# Grill Spec System (`grillspec`)

A Claude Code plugin for **spec-driven engineering**. It interviews an idea - or
grills existing docs - into a complete Domain-Driven Design spec, derives the
architecture, solution and task breakdown from that spec, and runs the build
loop. One **conductor** orchestrates a family of grilling, derivation, and execution skills; bundled
**deterministic linters** gate spec consistency and guard derived artifacts.

## Install

```
/plugin marketplace add ivanmrva/grillspec        # GitHub owner/repo (or a git URL, or a local path)
/plugin install grillspec@ivanmrva                # add --scope project to share via the repo
/reload-plugins                                   # then start: /grillspec:grill-spec-conductor
```

See exactly what it adds and its per-session token cost before committing:

```
/plugin details grillspec
```

## Use it

You normally talk only to the conductor; it routes everything else:

```
/grillspec:grill-spec-conductor
```

Or invoke any single skill directly when you want one focused step - they are all
installed and namespaced, e.g.:

```
/grillspec:grill-ddd                 # idea/docs -> domain model
/grillspec:derive-architecture       # spec -> solution architecture
/grillspec:derive-tasks              # spec -> task breakdown
```

Every skill loads a shared engine (`grill-engine`, `derive-engine`, or
`exec-engine`) that carries the interview/derivation discipline; the per-skill
file is only the thin profile of what varies. No skill depends on a sibling
skill, so a subset works on its own.

## Individual skills (standalone)

You **don't need a plugin per skill.** Any skill can be shipped on its own as a
self-contained, copy-able skill - the project emits these by inlining the shared
engine into the skill:

```
python3 tools/emit-standalone.py grill-ddd grill-quality derive-architecture   # a chosen subset
python3 tools/emit-standalone.py --all-grill                                   # every grill-* skill
```

Each lands in `dist/standalone/<name>/` as a `SKILL.md` plus its own `README.md`
guide. To distribute one, the recipient just drops the folder into a skills
directory - no plugin, no marketplace:

```
unzip <skill>.zip -d ~/.claude/skills/     # personal: all their projects
# or commit it to .claude/skills/ in a repo -> teammates get it on clone
```

Standalone skills compose through documents at a shared working root, so a copied
subset (e.g. ddd -> quality -> architecture) still works together.

**When to wrap a single skill as a plugin instead:** only if you want the managed
`/plugin install` experience for it on its own - one-command install, versioning,
auto-update, Discover-tab visibility. Add a `.claude-plugin/plugin.json` to the
skill folder and it loads as a single-skill plugin, or list it as another plugin
entry in the marketplace. Trade-off: each such plugin carries its **own copy of the
engine** (the bundle plugin shares one engine across them all), so prefer the bundle
unless someone genuinely wants just that one skill via managed install.

## What the plugin ships vs. what lives in your project

**Ships in the plugin** (resolved from the install cache via `${CLAUDE_PLUGIN_ROOT}`):
the full skill set, the shared engines and layout map (`grill-shared/`), the spec
linters and the two project-local enforcers - the spec-governance hook and the
exec-gate (`tools/`) - and the subagents (`agents/`). **The plugin installs no
_global_ hooks** - it acts only when you invoke a skill, and never touches other
projects or your `~/.claude` config.

**Created in your project at runtime** by the skills: the `spec/` tree, and -
once the walking-skeleton runs - the two **project-local** enforcers wired into
this repo only: the git **pre-commit** spec hook in `.git/hooks/`, and a Claude
Code **PreToolUse exec-gate** merged into this project's `.claude/settings.json`
(it enforces red-before-green and blocks a hollow done-claim _at tool-call time_,
where commit-time checks can't see the ordering). The system enforces its own
`spec/` layout and **creates it regardless of how your repo is otherwise
organised** - that is expected and part of usage. The plugin install cache stays
read-only; nothing is written to your project's `.claude/` until the
walking-skeleton runs, and never to your `~/.claude/`.

## Recommended project add-ons (optional, not installable by a plugin)

Two things a plugin cannot install for you; add them to the project repo if you
want them:

- **Permission allowlist** for smoother autonomous/AFK runs. Plugin `settings.json`
  only supports `agent`/`subagentStatusLine`, so the bash/edit allowlist belongs
  in your project `.claude/settings.json`. Destructive-command and out-of-scope
  guarding is the **session permission layer's** job (Claude Code already prompts);
  the plugin does not impose its own global command guard.
- **Spec governance (project-local).** The walking-skeleton installs
  `spec_governance_hook.sh` as the project's spec **pre-commit hook** - it runs
  `lint_spec.py` + `guard_derived.py` over `spec/`, scoped to that repo. Run the
  same linters in CI on every push; see `docs/`.
- **Exec-gate (project-local).** The walking-skeleton also runs
  `install_exec_gates.py`, which merges a **PreToolUse hook** into this project's
  `.claude/settings.json` (`gate_exec.py`). It is the tool-call-time sibling of
  the commit-time hook above: it blocks a `src/**` edit until a failing test was
  recorded for the active task (red-before-green), and blocks flipping a task to
  `status: done` while its Verification Record is unmet. Scoped to this repo only.
  Override per call with `GRILLSPEC_GATE_OFF=1` (the analogue of `--no-verify`).

## Governance is project-local, never global

The plugin installs **no _global_ Claude Code hooks**, so it never fires on your
other projects or your `~/.claude` config. Both enforcement layers live inside
the spec repo: the conductor invokes the spec linters each run, the git
**pre-commit hook** (`spec_governance_hook.sh`) + CI enforce spec consistency and
the derived-artifact guard at commit/PR time, and the **project-local PreToolUse
exec-gate** (`gate_exec.py`, wired into this repo's `.claude/settings.json`)
enforces the per-task build _order_ at tool-call time - the one thing a
commit-time check structurally can't see. All three are inside that repo only.

## Editing and releasing

This plugin's source *is* the system - edit the `SKILL.md` files, engines, and
tools directly. After any edit:

```
python3 tools/selfcheck.py        # validates structure, frontmatter, paths, manifests, hooks, tools
```

To ship changes to installed projects, **bump `version` in
`.claude-plugin/plugin.json`** and push; reinstall or let marketplace auto-update
pick it up. (If you leave `version` unset, every commit is treated as a new
version instead.)

## Docs

- **[`docs/skills/`](docs/skills/README.md) — per-skill user guides + catalog.** One guide
  per skill (purpose, input, output, and *how to tell it did its job*), generated from the
  skill itself so it never drifts. Start here to see what each skill does.
- `docs/HOW-IT-WORKS.md` - the pipeline, stages, tools, and the build loop.
- `docs/LIVE-TEST.md` - 20-minute protocol to verify a live agent follows the
  system, and that the plugin resolves correctly post-install.
- `docs/WORKING.md` - working notes.
