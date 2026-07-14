# Releasing

Everything ships from `dist/`, produced by `python build/build.py --zip`. The `main` branch carries
the canonical source and both marketplace catalogs; the `marketplace` branch carries only the
generated portable plugin root. A separate public skill collection remains optional.

## 1. Public skills repo (the skill database — MIT)

The "own the asset" collection of individually-usable skills.

```
python build/build.py skills
rm -rf <skills-repo>/skills && cp -r dist/skills/. <skills-repo>/skills/
cd <skills-repo> && git add -A && git commit -m "regenerate skills" && git push
```

Readers copy any single folder into `~/.claude/skills/` and invoke `/<skill>` in Claude Code, or
into `~/.agents/skills/` and invoke `$<skill>` in Codex.

## 2. Dual-host marketplace / full-system plugin (Apache-2.0)

The whole orchestrated system, installed once.

```
python build/build.py marketplace
# Publish the contents of dist/marketplace/plugins/grillspec/ at the root of the
# marketplace branch. Do not replace the canonical source on main.
```

Create the version tag and GitHub release from the resulting `marketplace` commit. Attach
`dist/grillspec-marketplace.zip`, `dist/grillspec-skills.zip`, both host-specific plugin ZIPs, and
any cluster ZIPs. The catalogs on `main` already resolve the `marketplace` branch.

Install:

```
/plugin marketplace add <owner>/grillspec
/plugin install grillspec@<owner>
/reload-plugins
```

Codex:

```bash
codex plugin marketplace add <owner>/grillspec
```

Then open `/plugins` in Codex CLI (or Settings > Plugins in the IDE), select that marketplace, and
install Grill Spec. Start a new session and invoke `$grillspec:grill-spec-conductor`.

Bump both `plugin/.claude-plugin/plugin.json` and `plugin/.codex-plugin/plugin.json` to the same
version before each release, and note the change in `plugin/CHANGELOG.md`.

## 3. Per-cluster plugins (optional — MIT)

Only if you want a narrower managed plugin for a blog post's skills.

```
python build/build.py plugins      # builds every entry in CLUSTERS (build.py)
# dist/plugins/<cluster>/ is a dual-host standalone plugin — publish or add to a marketplace
```

Default clusters (edit `CLUSTERS` in `build.py`): `grill-ddd`, `derive-tasks`,
`implement-and-review` (= implement-task + run-tests + conformance-review).

## Licensing

- Full system (`plugin/`, `dist/marketplace/`, host-specific builds): **Apache-2.0**.
- Public skills and cluster plugins (`dist/skills/`, `dist/plugins/`): **MIT** (copy-and-own),
  written by the pipeline from `build/licenses/MIT.txt`.

## Before any release

```
python plugin/tools/selfcheck.py plugin     # source integrity (must say VERDICT: PASS)
python plugin/tools/test_project_state.py   # neutral project paths + canonical AGENTS.md/CLAUDE.md
python plugin/tools/test_emit_standalone.py # auxiliary generator remains portable + dual-host
python build/build.py --zip                  # rebuild all artifacts
python build/check_dist.py                   # host-neutral generated-surface audit
```
