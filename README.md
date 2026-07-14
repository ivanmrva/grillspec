# Grill Spec System — source project

This is the **single source of truth** for the Grill Spec System and the **one pipeline**
that produces every distribution artifact. Nothing is duplicated in source: the three method
engines and 47 skills (one conductor plus 46 workers) live once under `plugin/`, and `build/build.py` assembles every
output from them.

## Layout

```
grillspec/
├── plugin/                 # THE source of truth — also a working plugin as-is
│   ├── .claude-plugin/plugin.json
│   ├── .codex-plugin/plugin.json
│   ├── skills/             # 47 skills: 1 conductor + 46 workers (SKILL.md each)
│   ├── grill-shared/       # the 3 method engines (grill/derive/exec) + shared docs  <-- reused everywhere
│   ├── tools/              # deterministic tools (lint_spec, impact, guard_derived, plugin_feedback, spec_governance_hook, …)
│   ├── agents/             # 2 subagents (explorer, test-runner)
│   └── docs/               # how-it-works + per-skill guides   (no global hooks — governance is project-local)
├── build/
│   ├── build.py            # the single pipeline (run this)
│   └── licenses/MIT.txt    # license for the public skill / cluster artifacts
├── dist/                   # GENERATED output (git-ignored) — see below
├── LICENSE                 # Apache-2.0 (the system)
└── README.md
```

## Build everything

```
python build/build.py            # produce all artifacts in dist/
python build/build.py --zip      # …and zip each one
```

Or build one target: `python build/build.py skills | claude | codex | marketplace | plugins`.

## What the pipeline produces

| `dist/` output      | What it is                                                                 | License     | Goes to                                   |
| :------------------ | :------------------------------------------------------------------------- | :---------- | :---------------------------------------- |
| `dist/skills/`      | **The skill database** — 46 worker skills as self-contained Agent Skills with portable references, scripts, and Codex metadata. | MIT | a public skills repo or direct copy |
| `dist/marketplace/` | **Combined release archive** — one portable plugin bundle with both Claude Code and Codex marketplace manifests. | Apache-2.0 | release ZIP / local marketplace |
| `dist/claude/`      | Claude Code-specific marketplace artifact. | Apache-2.0 | optional host-specific release |
| `dist/codex/`       | Codex-specific marketplace artifact. | Apache-2.0 | optional host-specific release |
| `dist/plugins/<c>/` | **Optional per-cluster plugins** — portable dual-host subsets configured in `CLUSTERS`. | MIT | per-post repos / a shared marketplace |

The engines are **reused, not copied in source**. The build resolves each skill's transitive
references and scripts from `plugin/grill-shared/` and `plugin/tools/`, then renders a self-contained
Agent Skills-compatible folder. Claude-specific frontmatter becomes Codex policy metadata instead of
leaking host-specific fields into the portable skill.

## User guides (generated)

The pipeline writes a full user guide into every output, so each project ships its own docs:

- `dist/GUIDE.md` — master guide: how to generate everything **and** how to use everything.
- `dist/skills/GUIDE.md` — how to use the individual skills (+ full catalog).
- `dist/marketplace/GUIDE.md` — how to install and drive the whole system in either host.
- `dist/claude/GUIDE.md` and `dist/codex/GUIDE.md` — host-specific installation guides.
- `dist/plugins/<c>/GUIDE.md` — how to install and use that cluster.

Every catalog is generated from the skills' own `SKILL.md` descriptions, so the guides never drift
from what the skills actually do.

## Filling the public skills repo

`dist/skills/` is the skill directory the public repo should contain. Regenerate and overwrite:

```
python build/build.py skills
rm -rf /path/to/skills-repo/skills && cp -r dist/skills /path/to/skills-repo/skills
```

(Or point CI at `dist/skills/` and commit it.) Each folder is independently copyable into
`~/.claude/skills/` (Claude Code) or `~/.agents/skills/` (Codex).

## Plugin delivery — what to ship

- **Required: one plugin release** — publish `dist/marketplace/plugins/grillspec/` at the root of
  the `marketplace` branch. The catalogs committed on `main` both resolve that branch, so there is
  no second maintained source system. Attach the generated ZIPs to the GitHub release.
- **Optional: the per-cluster plugins** — only worth shipping if you want blog readers to
  install a narrower bundle instead of copying
  a folder from the skill database. They are **redundant in content** with the skill database, so
  they are a UX/marketing convenience, not a second system. Add or remove clusters by editing the
  `CLUSTERS` dict in `build.py`.
- Nothing else (no kernel/sub-plugin split) — it adds packaging complexity with no payoff at this
  size.

The individual-skill need is served by the **skill database** (plain skills, copy-and-own); the
whole-system need is served by the **dual-host marketplace plugin**. Those two cover everything; cluster
plugins are the only optional extra.
