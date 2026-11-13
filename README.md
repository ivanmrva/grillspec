# Grill Spec System — source project

Grill Spec is a plugin for Claude Code and Codex that turns an idea into a specification a coding agent can build from, and then drives the build. What it does and how to use it is in [plugin/README.md](plugin/README.md).

This repository is the single source for the system and holds the one pipeline that produces every distribution artifact. Nothing is duplicated in source: the 44 skills (one conductor and 43 workers) and the three method engines they share live once under `plugin/`, and `build/build.py` assembles every output from them.

## Layout

```
grillspec/
├── plugin/                  # the source — also a working plugin as it stands
│   ├── .claude-plugin/plugin.json
│   ├── .codex-plugin/plugin.json
│   ├── skills/              # 44 skills, one folder each (SKILL.md, plus a worked example for each worker)
│   ├── grill-shared/        # 3 method engines (grill, derive, exec), the shared rules, the dependency graph
│   ├── tools/               # 25 Python tools, the pre-commit hook script, a Spectral ruleset, 16 regression suites
│   ├── agents/              # 2 helper agents (explorer, test-runner)
│   ├── docs/                # how it works, the checks, a guide per skill
│   └── CHANGELOG.md
├── build/
│   ├── build.py             # the build pipeline
│   ├── check_dist.py        # checks the built artifacts
│   └── licenses/MIT.txt     # license for the public skill and cluster artifacts
├── .claude-plugin/          # Claude Code marketplace catalog
├── .agents/plugins/         # Codex marketplace catalog
├── .github/workflows/       # plugin-check.yml: selfcheck, the regression suites, the build
├── dist/                    # generated output (git-ignored)
├── RELEASING.md
├── LICENSE                  # Apache-2.0 (the system)
└── README.md
```

The tools fall into four groups:

| Group | Tools |
|---|---|
| spec | `lint_spec.py` · `impact.py` · `spec_status.py` · `check_contracts.py` · `project_config.py` |
| build | `check_task.py` · nine code-facing checkers (`check_no_fakes.py`, `check_no_skips.py`, `check_orphan_tests.py`, `check_mock_budget.py`, `check_test_tiers.py`, `check_e2e_target.py`, `check_config_drift.py`, `check_deploy_real.py`, `check_migration_real.py`) · `tier_contract.py` (their shared parser) |
| hooks | `gate_exec.py` (the edit hook) · `install_exec_gates.py` · `spec_governance_hook.sh` (the git pre-commit hook) |
| plugin maintenance | `selfcheck.py` · `gen_depgraph.py` · `gen-guides.py` · `skill_guide.py` · `gen_docsite.py` · `emit-standalone.py` · `plugin_feedback.py` |

The plugin installs no global hooks; the two hooks above are installed into the project the plugin works on. [plugin/docs/SPEC-CHECKS.md](plugin/docs/SPEC-CHECKS.md) lists what every tool checks.

## Check the source

```
python3 plugin/tools/selfcheck.py plugin
```

Run it after editing a skill, an engine or a tool. It checks the manifests, each skill's frontmatter and engine reference, the ID-prefix vocabulary across the tools, and the dependency graph.

## Build everything

```
python build/build.py            # produce all artifacts in dist/
python build/build.py --zip      # …and zip each one
```

Or build one target: `python build/build.py skills | claude | codex | marketplace | plugins`.

## What the pipeline produces

| `dist/` output | What it is | License | Goes to |
| :-- | :-- | :-- | :-- |
| `dist/skills/` | the skill database: 43 worker skills, each a self-contained Agent Skill with its references, scripts and Codex metadata | MIT | a public skills repository, or direct copy |
| `dist/marketplace/` | the combined release: one plugin bundle with both the Claude Code and the Codex marketplace manifests | Apache-2.0 | the release ZIP and the `marketplace` branch |
| `dist/claude/` | the Claude Code marketplace artifact | Apache-2.0 | an optional host-specific release |
| `dist/codex/` | the Codex marketplace artifact | Apache-2.0 | an optional host-specific release |
| `dist/plugins/<c>/` | optional per-cluster plugins: subsets configured in `CLUSTERS` | MIT | per-post repositories, or a shared marketplace |

The engines are reused, not copied in source. The build resolves each skill's references and scripts from `plugin/grill-shared/` and `plugin/tools/` and writes a self-contained folder. Frontmatter that only Claude Code understands becomes Codex policy metadata, so no host-specific field leaks into the portable skill.

## User guides (generated)

The pipeline writes a user guide into every output:

- `dist/GUIDE.md` — the master guide: how to generate everything and how to use it.
- `dist/skills/GUIDE.md` — how to use the individual skills, with the full catalog.
- `dist/marketplace/GUIDE.md` — how to install and drive the whole system in either host.
- `dist/claude/GUIDE.md` and `dist/codex/GUIDE.md` — host-specific installation.
- `dist/plugins/<c>/GUIDE.md` — how to install and use that cluster.

Every catalog is generated from the skills' own `SKILL.md` descriptions, so the guides cannot drift from what the skills do.

## Filling the public skills repository

`dist/skills/` is the directory the public repository should contain. Regenerate and overwrite:

```
python build/build.py skills
rm -rf /path/to/skills-repo/skills && cp -r dist/skills /path/to/skills-repo/skills
```

Each folder can be copied on its own into `~/.claude/skills/` (Claude Code) or `~/.agents/skills/` (Codex).

## What to ship

- **Required: one plugin release.** Publish `dist/marketplace/plugins/grillspec/` at the root of the `marketplace` branch. The catalogs committed on `main` both resolve that branch, so there is no second source to maintain. Attach the generated ZIPs to the GitHub release. [RELEASING.md](RELEASING.md) has the steps.
- **Optional: the per-cluster plugins.** They hold the same content as the matching skill-database entries, packaged for `/plugin install`. Ship them only if you want readers to install a narrower bundle instead of copying a folder. Add or remove clusters in the `CLUSTERS` dict in `build.py`.

The skill database serves anyone who wants one skill to copy and own; the marketplace plugin serves anyone who wants the whole system. Cluster plugins are the only optional extra.
