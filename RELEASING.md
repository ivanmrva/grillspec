# Releasing

Everything ships from `dist/`, produced by `python build/build.py --zip`. Two repos, plus
optional per-post plugins.

## 1. Public skills repo (the skill database — MIT)

The "own the asset" collection of individually-usable skills.

```
python build/build.py skills
rm -rf <skills-repo>/skills && cp -r dist/skills/. <skills-repo>/skills/
cd <skills-repo> && git add -A && git commit -m "regenerate skills" && git push
```

Readers copy any single folder into `~/.claude/skills/` and invoke `/<skill>`.

## 2. Marketplace / full-system plugin (Apache-2.0)

The whole orchestrated system, installed once.

```
python build/build.py full
# dist/full-system/ is the marketplace repo: push its contents to github.com/<owner>/grillspec
```

Install:

```
/plugin marketplace add <owner>/grillspec
/plugin install grillspec@<owner>
/reload-plugins
```

Bump `plugin/.claude-plugin/plugin.json` `version` before each release, or users keep the cached
copy (Claude Code uses the version as the update key). Note the change in `plugin/CHANGELOG.md`.

## 3. Per-cluster plugins (optional — MIT)

Only if you want a managed `/plugin install` path for a blog post's skills.

```
python build/build.py plugins      # builds every entry in CLUSTERS (build.py)
# dist/plugins/<cluster>/ is a standalone plugin — publish per repo, or add to a marketplace
```

Default clusters (edit `CLUSTERS` in `build.py`): `grill-ddd`, `derive-tasks`,
`implement-and-review` (= implement-task + run-tests + conformance-review).

## Licensing

- Full system (`plugin/`, `dist/full-system/`): **Apache-2.0**.
- Public skills and cluster plugins (`dist/skills/`, `dist/plugins/`): **MIT** (copy-and-own),
  written by the pipeline from `build/licenses/MIT.txt`.

## Before any release

```
python plugin/tools/selfcheck.py plugin     # source integrity (must say VERDICT: PASS)
python build/build.py --zip                  # rebuild all artifacts
```
