# Changelog

All notable changes to the `grillspec` plugin. Versions follow
[semantic versioning](https://semver.org). Bump `version` in
`.claude-plugin/plugin.json` to release.

## 1.1.0

Separation of concerns: workers are now standalone, the conductor owns all orchestration, and the project can emit copy-able standalone skills.

### Architecture
- The shared engines (grill/derive/exec) are now **conductor-unaware**: a worker is a pure "input -> one artifact" unit. Removed from the engines and the 38 worker profiles: all conductor references, hard gates, required-upstream refusal, closed-world tree ownership, project-wide tool runs, and downstream propagation. Each engine now states its job edges - works from whatever input it is given, behind no gate; writes its artifact to a given target or a self-named default; flags missing input rather than refusing; does not arrange the wider structure, reconcile across artifacts, lint, or chase dependents.
- The **conductor** now explicitly owns all orchestration and hands each worker its input and its target location, then reads each worker's output and reconciles the cross-area views (glossary, actors, ADR index, bets) — there are no shared singletons — and runs the linters, consistency checks, and propagation. Workers know nothing of it. The conductor is model-invocable; the 38 workers stay manual.

### Build
- Added `tools/emit-standalone.py`: copies a chosen skill plus the engine(s) it references (resolved transitively) into a self-contained, copy-able bundle under `dist/standalone/<name>/` (no transformation; the post-refactor source is already shippable). `--public` bundles ship an MIT LICENSE. The single source stays duplication-free; duplication exists only in emitted artifacts. People can copy just the subset they want and compose them through documents, with no conductor and no full tree.

### Docs
- Added `tools/gen-guides.py` + `tools/skill_guide.py`: generate a **user guide per skill** into `docs/skills/<name>.md` plus a catalog index, built from each skill's own fields - purpose, input, output, and a "how to tell it did its job" checklist drawn from the skill's `coverage` (grill/derive) or `never pass on` + `verdict` (exec) rules. The emit build ships each standalone skill with its own `README.md` guide. These are both the release documentation and the per-skill verification surface.

### Net effect
Two distributions from one source: the **bundle plugin** (whole system, shared engine, install once, use any skill) and **standalone skills** (copy a subset, work independently).

## 1.0.0

First packaged release - the system distributed as a Claude Code plugin via a
marketplace (previously a generated `.claude/` tree copied per project).

### Packaging
- Converted to the standard plugin layout: `.claude-plugin/plugin.json`, plus
  `skills/`, `grill-shared/`, `tools/`, `agents/`, and `hooks/` at the plugin
  root; marketplace catalog at the repo root.
- Migrated every internal file reference from project-relative `.claude/...`
  paths to `${CLAUDE_PLUGIN_ROOT}/...`, so engines, tools, and hook scripts
  resolve from the install cache. Required because marketplace plugins run from
  a copy and cannot reference files outside their own directory.
- Hooks moved to `hooks/hooks.json` (same guards: PreToolUse scope guard,
  PostToolUse spec-lint + impact, Stop derived-artifact guard).
- Added `tools/selfcheck.py` - source-integrity check for the authoring workflow
  (frontmatter, engine references, stale paths, manifest/hook JSON, hook script
  wiring, tool compilation).
- Added `docs/LIVE-TEST.md` - live-agent verification protocol.

### Behaviour (carried in from recent work)
- Correlated-ID check generalized to suffix matching, so namespaced ids work
  (`NFR-REL-2 -> ASR-REL-2`) alongside plain-numeric (`NFR-014 -> ASR-014`).
- Conductor reference in worker skills made mode-aware (orchestrated by the
  conductor in the full system; invoked directly when run standalone).
- `repo-layout` documents that a partial/standalone subset is valid and needs no
  trimming.
- Output-hygiene rule in both engines: `spec/` never names a skill, a tool, or
  narrates the producer.
- ADR lifecycle: one flat append-only `decisions/` log classified by `Class:`;
  superseded ADRs are archived (number never reused), live truth stays at the
  top level.

### Known follow-ups
- Run `docs/LIVE-TEST.md` against a real project - the only unverified surface is
  live-agent adherence (engine resolution, grilling depth, gate discipline, the
  autorun verdict contract).
- Optionally make the conductor model-invocable (drop `disable-model-invocation`
  on it only) so a spec task auto-engages it while workers stay manual.
- Optional sub-plugins (a kernel plugin + feature bundles with plugin
  `dependencies`) if a lower always-on token cost or true minimal installs are
  wanted.
