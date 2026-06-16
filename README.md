# Grill Spec System — source project

This is the **single source of truth** for the Grill Spec System and the **one pipeline**
that produces every distribution artifact. Nothing is duplicated in source: the three method
engines and the 44 skills live once under `plugin/`, and `build/build.py` assembles every
output from them.

## Layout

```
grillspec/
├── plugin/                 # THE source of truth — also a working plugin as-is
│   ├── .claude-plugin/plugin.json
│   ├── skills/             # 44 skills: 1 conductor + 43 workers (SKILL.md each)
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

Or build one target: `python build/build.py skills | full | plugins`.

## What the pipeline produces

| `dist/` output      | What it is                                                                 | License     | Goes to                                   |
| :------------------ | :------------------------------------------------------------------------- | :---------- | :---------------------------------------- |
| `dist/skills/`      | **The skill database** — every worker skill as a self-contained, individually-usable plain skill (`SKILL.md` + the one engine it loads, bundled as a sibling, `${CLAUDE_PLUGIN_ROOT}` rewritten away). 43 folders. | MIT         | the public **skills repo** (overwrite its skill dir) |
| `dist/full-system/` | **The whole system as one plugin** — `plugin/` verbatim under a marketplace wrapper (conductor + 43 workers + engines + tools + agents). | Apache-2.0  | the **marketplace/plugin repo**           |
| `dist/plugins/<c>/` | **Optional per-cluster plugins** — same skills as the database, packaged as installable plugins for the managed `/plugin install` experience. Set in `CLUSTERS` in `build.py`. | MIT         | per-post repos / a shared marketplace     |

The engines are **reused, not copied in source**: each skill-database folder and each cluster
plugin gets exactly the engine(s) its skills load, resolved transitively from the single
`plugin/grill-shared/` copy.

## User guides (generated)

The pipeline writes a full user guide into every output, so each project ships its own docs:

- `dist/GUIDE.md` — master guide: how to generate everything **and** how to use everything.
- `dist/skills/GUIDE.md` — how to use the individual skills (+ full catalog).
- `dist/full-system/GUIDE.md` — how to install and drive the whole system (+ workflow + catalog).
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
`~/.claude/skills/`.

## Plugin delivery — what to ship

- **Required: one plugin** — `dist/full-system/` (the whole orchestrated system, Apache-2.0).
  This is the only plugin you actually need.
- **Optional: the per-cluster plugins** — only worth shipping if you want blog readers to
  `/plugin install grill-ddd@…` (managed install + the `/grill-ddd` command) instead of copying
  a folder from the skill database. They are **redundant in content** with the skill database, so
  they are a UX/marketing convenience, not a second system. Add or remove clusters by editing the
  `CLUSTERS` dict in `build.py`.
- Nothing else (no kernel/sub-plugin split) — it adds packaging complexity with no payoff at this
  size.

The individual-skill need is served by the **skill database** (plain skills, copy-and-own); the
whole-system need is served by the **full-system plugin**. Those two cover everything; cluster
plugins are the only optional extra.
