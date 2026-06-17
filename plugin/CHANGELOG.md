# Changelog

All notable changes to the `grillspec` plugin. Versions follow
[semantic versioning](https://semver.org). Bump `version` in
`.claude-plugin/plugin.json` to release.

## 1.4.5

### Fixed
- **Numeric range / list shorthand in prose no longer false-errors.** Derivation agents write ID ranges like `ML-102..109` or `VO-416..421` (and slash-lists like `API-002/003`) as a house-style abbreviation, but the linter tokenized the whole range as one bogus bare id (`ML-102..109`) and raised spurious *undefined ID* / *defined in multiple files* ERRORs — forcing authors to spell the ids out or hide them behind a marker. A `RANGE` matcher (`<PREFIX>-<digits>(`..`|`/`<digits>)+`) now strips these shorthands from each line before the definition and reference passes. A real dotted field id (`DATA-Customer.id`, single dot) and a slash-list of *full* ids (`T-014/T-015`, each prefixed) are untouched — they keep per-id resolution, because the range form's middle is pure digits.

### Added
- **Two more INFO-level advisory lints** (joining development-trace from 1.4.4; all advisory, never fail CI, the conductor's semantic sweep judges them):
  - **Self-reference** — the spec must read as standalone project documentation with no awareness of this system; flags a skill / engine / tool name (`grill-*`, `derive-engine`, `derive-tasks`, `lint_spec`, `guard_derived`, …) or a generation step (`re-derived`, `seeded by`) that leaked into an artifact.
  - **Context-namespaced id** — a `<CTX>-TYPE-NNN` id (e.g. `SUR-AGG-250`) silently fails to register while bare references to it resolve; flags it and suggests the bare prefix (`AGG-250`). The one legitimate two-segment form, `ADR-<AREA>-NNN`, is skipped (its lead segment is the `ADR` type).
  - **Unquantified quality adjective** (requirements area only) — every requirement is a measurable bar, never an adjective; flags `fast` / `scalable` / `secure` / … on a requirement line that carries **no** measurable bar (a comparator+number or number+unit), so a quantified line like `p95 < 200 ms` is left alone.

## 1.4.4

### Added
- **INFO-level lint for development-trace language** — a deterministic backstop for the timeless-source-of-truth rule (1.4.3) that also covers *already-generated* content, since `lint_spec.py` runs over all of `spec/` every invocation. It flags the **unambiguous** development-trace forms — conversational meta (`as we discussed`, `per our conversation`), `newly added/created/…`, `this round adds/removes/…`, and bracketed changelog annotations (`(formerly X)`, `(previously X)`, `(was: X)`, `(renamed …)`, `(moved from …)`), plus `renamed from` / `formerly known as` / `used to be`. **INFO severity** (advisory; never fails CI), because a deterministic check *cannot* distinguish a bare `New tables` heading from a domain `new booking` — that disambiguation stays with the conductor's semantic sweep. Skips fenced code and the scope header; a forward-looking `(deferred until <trigger>)` is legitimate and not flagged; the matched phrase is shown for fast judgement.

## 1.4.3

### Fixed
- **The spec no longer narrates its own development history.** On follow-up edits to an already-generated spec, areas were leaking development-trace / changelog language into the artifact — content tagged `new` / `newly added` / `now` / `previously` / `expand→contract`, and notes of what *this* edit added, cut, or deferred (e.g. *"New tables — expand→contract entries (research workspace + deferred Creator-Ops)"*). The generated spec is a **timeless source of truth**: it must read as standalone project documentation describing the system *as it is now*, to someone with no idea how, when, by what tool, or in how many passes it was produced. The existing house-style rule only banned naming a skill/tool or "produced by …"; it's now extended in all three shared engines (`grill-engine`, `derive-engine`, `exec-engine`) to ban edit-history tags and "what changed this round" annotations outright — while keeping the same word legitimate as **domain language** (a `new booking`), and keeping forward-looking scope as a timeless property (an exclusion ADR, or `deferred until <trigger>`). The conductor's cross-area consistency pass now runs a **timeless-source-of-truth sweep** to strip any such language that still slips through, routing the fix to the owning area.

## 1.4.2

### Fixed
- **Table-header column labels no longer register as fake ID definitions** (false coverage WARNs). `DEF1` treats the first cell of a line as an ID definition, and `IDCORE` accepts non-numeric suffixes (real ids are often `AGG-Job`/`DS-Button`/`SLO-checkout-availability`, so a digit can't be required). A column header like `| OBL-id | Rule |` therefore registered a phantom obligation `OBL-id` that then tripped a coverage WARN (no downstream reference) — hit on `OBL-id`, `DS-id`, and `NFR-evidence`, which authors had been dodging by writing `THR- id` with a space. Fixed structurally: the definition pass now **skips a markdown table header row** (a `|`-bearing line immediately followed by a `|---|:--:|` separator), whose first cell is a column label, not an id. Real ids — defined in body rows — still register, resolve, and feed the coverage/define-once/owning-area checks unchanged.

## 1.4.1

### Fixed
- **ADR prose no longer false-errors as an "illegal downward reference."** ADR files map to no stage layer (`file_layer` 0, since `adr/` matches none of the stage prefixes), so the upstream-only reference check errored whenever an ADR cited an upstream requirement id (`NFR-`/`ASR-`/`DATA-`/`SEC-`, all `id_layer` 2) that happened to fall after a REFMARK word (`realize`/`see`/`covers`/`satisfies`/…) or a `->`/`→` arrow on the same line — `L0 file -> NFR-012 (L2)`. The error was incidental to prose punctuation, not reference validity: the same driver citation passed or failed depending on a nearby dash or word (e.g. `ADR-DATA-002` erroring on `same content → same row`). But a derivation ADR legitimately records its drivers by design. ADR **source** files are now exempt from the downward-reference check via `is_adr_file()`, mirroring the existing ADR-**target** exemption. Genuine downward references from real stage files still error.

## 1.4.0

### Added — browsable doc-site generator
- `tools/gen_docsite.py`: a **deterministic, model-free** projection of `spec/` into a self-contained, browsable static HTML site under `docs-site/`. Stdlib-only and **byte-stable across runs** (sorted ordering, no timestamps), so it slots into CI and produces reviewable diffs rather than churn. Like `gen_depgraph.py`, it reads `lint_spec.py`'s `TYPES` + `PREFIX_OWNER` and reuses its definition surfaces (`DEF1/DEF2/DEF3`) at runtime, so **ID detection can't drift from the linter**. It renders the spec's markdown — GFM tables (with alignment + zebra), nested lists, Mermaid diagrams, scope-header badges — **anchors every stable ID at its definition and cross-links every reference** across files, and builds a navigable sidebar plus a home page with a full ID index. Output mirrors the spec tree, so the spec's own relative `.md` links resolve as `.html`; styling is self-contained local CSS (offline-capable) with only Mermaid from a pinned CDN. This is the deterministic *reference-projection* half of documentation — a tool, not a skill — and ships standalone (`python3 tools/gen_docsite.py [spec_dir] [out_dir]`); it is not yet wired into the `generate-docs` skill.

## 1.3.2

### Fixed
- **DEF3 (1.3.1) over-registered downstream `<ID> <Name>` reference-listings as definitions** — it told definitions from references by "no refmark on the line," but the skills use the same `<ID> <Name>` form for both (use-case command lists, authz lists, etc.). On a clean 1.2.0-era spec the upgrade produced ~131 false ERRORs (duplicate-definition + defined-outside-owning-area) plus false coverage WARNs. Now disambiguated **structurally**: an inline `<ID> <Name>` is a definition **only inside the ID-type's owning area** (`PREFIX_OWNER`); anywhere else it's a reference (resolved + coverage-counted, so dangling ones still error). Inline registrations are **supplementary** (don't feed the define-once / owning-area checks), so the same command in both an aggregate block and the event-flow file isn't a false duplicate. The match anchor now also skips `**`/backtick markup and accepts flow arrows + table pipes, so ddd's `- **commands:** CMD-201 …` first-id, the `EVT-210 … ⟵ CMD-201 …` event-flow form, and named policy-table cells register.

## 1.3.1

### Fixed
- **`CMD-`/`EVT-` (and `VO-`/`ENT-`/`POL-`/`RM-`) defined in the domain model's nested-bullet format now register.** grill-ddd prescribes commands/events as `commands: CMD-201 ExtractAtoms · CMD-204 ReExtract` bullets, but the linter only registered an ID as a row-key/heading — so the two highest-traffic ID types went unregistered, breaking command/event traceability (downstream `maps-to: CMD-…` read as undefined) and silencing their coverage checks. The linter now registers `<ID> <Name>` definition pairs in non-reference lists (general — any skill's `ID Name` lists benefit); references are excluded, so no IDs are mis-registered. grill-ddd's stable-ID guidance states the `<ID> <Name>` shape explicitly.

## 1.3.0

A machine-readable dependency graph the system reads when dispatching, plus a linter ref-marker fix.

### Added — dependency graph
- `grill-shared/dependencies.json`: the **machine-readable** dependency graph (per area: stage · skill · kind · `consumes` upstream areas · `produces_ids`). The **conductor reads it before running a skill** to know which upstream artifacts/IDs to gather and hand over — the system now knows its own dependencies, not just the docs.
- `tools/gen_depgraph.py`: generates `docs/DEPENDENCY-GRAPH.md` (a stage table + a Mermaid DAG) from the JSON, and **validates** it — every `produces_id` is known to the linter and owned by the right folder, every `consumes` edge resolves, the graph is acyclic.
- `selfcheck.py` runs `gen_depgraph.py --check`, so the JSON is validated and the rendered doc can't drift from it.
- Backfilled the missing `Consumes:` declarations on `grill-ddd`, `grill-system-context`, `grill-compliance`.

### Fixed
- **Linter ref-marker false positives**: the reference-marker regex matched markers as substrings, so `invalidates`→`validates`, `discovers`→`covers`, etc. captured the following ID and raised spurious undefined / illegal-downward-reference ERRORs. Word markers are now `\b`-anchored (the whole class, not just `validates`).

## 1.2.1

No global hooks — the plugin is now fully passive. Spec governance moved to a project-local enforcer.

### Removed
- **Deleted the three bundled Claude Code hooks** (`hooks/hooks.json` + `guard_scope.sh`, `post_write.sh`, `stop_guard.sh`). They fired install-wide on *every* session with no grillspec-project gate, and interfered with unrelated work: blocking edits to files outside the project (including the user's own `~/.claude` config), blocking destructive/`git push --force` Bash in any repo (by substring), spraying spec-lint output into non-grillspec `spec/` dirs (e.g. RSpec), and falsely flagging any project's own `CLAUDE.md` as a "derived artifact" on every turn. The plugin now installs **no hooks** — it acts only when you invoke a skill, and never touches other projects or your Claude config.

### Added (project-local replacement)
- `tools/spec_governance_hook.sh`: the ready-to-run spec enforcer as a **project-local git pre-commit hook** the walking-skeleton installs into the project. It runs `lint_spec.py` + `guard_derived.py` over `spec/` and blocks a bad commit — scoped to that repo, on commit only, nothing global; no-ops safely when there's no `spec/` or vendored tools. Destructive-command guarding is left to the session permission layer (which already prompts), not re-imposed by the plugin.
- Docs (README, WORKING, LIVE-TEST, derive-tasks) updated to describe governance as project-local.

## 1.2.0

Linter correctness, complete ID coverage, and a self-feedback channel — hardening surfaced by real runs.

### Linter (`tools/lint_spec.py`)
- **Closed world** now accepts spec-root orchestration files (`_readiness.md`, `_human-input.md`); they were read by the linter yet rejected as "outside the structure."
- **Token boundary**: a known prefix is no longer mined out of a longer token — `HOT-005` no longer raises a phantom `T-005`, and `SUR-AGG-250` no longer leaks `AGG-250`.
- **Complete ID type set**: `VO HOT POL RM ENT ML THR` are now registered and checked alongside the rest (added across the regex, layer, and owner tables); a single `TYPES` constant is the source of truth.
- **Context-namespaced IDs** (`SUR-AGG-250`) now get an honest error instead of going silently unregistered.
- **Row-key convention**: WARN when a stable ID sits in a non-leading table cell (it wouldn't register as defined).
- **Coverage noise**: downstream-coverage WARNs are suppressed while the downstream type doesn't exist yet (no more 100%-expected "CMD has no UC" in early stages).

### Self-feedback (`tools/plugin_feedback.py`)
- New tool + `GRILLSPEC-FEEDBACK.md` at the project root: a run that hits a defect or gap in **this system itself** records it for the plugin author — capture-and-route, never self-patch, and never inside `spec/`. Wired into the conductor and all three engines.
- `tools/selfcheck.py` gains an **ID-prefix drift guard**: fails if a skill declares a prefix the linter doesn't know (caught `THR-`).

### Skills & conventions
- Every owning skill now declares the **complete stable-ID set** for its outputs; `grill-ddd` blesses `VO`/`ENT`/`POL`/`RM`/`HOT`.
- The engines, conductor, and playbook document two non-obvious spine rules: **bare type prefix** (never `<CTX>-TYPE-NNN`) and **ID = leading table column**, plus a parallel-drafting checklist and a "prefer a Markdown table for tabular content" house rule.
- Conductor wording corrected: area skills are reference docs you **load and run**, not dispatchable agents (43 of 44 are `disable-model-invocation: true`).

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
