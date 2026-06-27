# Changelog

All notable changes to the `grillspec` plugin. Versions follow
[semantic versioning](https://semver.org). Bump `version` in
`.claude-plugin/plugin.json` to release.

## 4.8.3

### Fixed — two false-positive/over-strict findings surfaced by real derive-tasks output
- **`lint_spec.py` false-fired `defined in multiple files` on the natural derive-tasks output.** `build-order.md` (the task register, whose rows key on `T-` ids) and each `T-NNN.md` (whose H1 leads with the same `T-` id) both live in `10-delivery/tasks/`, so the define-once scan counted every `T-` twice (68× on a real 68-task project). `build-order.md` is a register that *references* the per-file definitions — exactly like `traceability.md` and the verification records, which were already exempt. **Fix:** exempt `build-order.md` from the definition-site scan; its `T-` row-keys now resolve as references. Removes the backtick-the-register workaround.
- **16b `JRN→UC` had no `N/A` escape, but Generic/unmodeled-subdomain journeys legitimately have no `UC-`.** A journey rendering a deliberately-unmodeled **Generic** subdomain (passwordless auth, tier/billing — identity/billing kept Generic, not modelled as use-cases) had no `UC-` to cite and no escape, forcing a mis-citation. **Fix:** `JRN→UC` now allows `N/A — why` (matching its sibling `ML→UC`); a journey declares `N/A — renders <Generic subdomain>, unmodeled`. `SLO→NFR` stays strict **by design** — an SLO operationalises an NFR by definition (a missing NFR is the gap to catch, not an escapable case), so the `N/A` allowance is set per-edge by whether a legitimate no-driver case exists. `grill-ux-reqs` rule + `SPEC-CHECKS.md` updated; the per-edge rationale is documented at the `BACKREF` table.
- Regression tests `build-order-register-not-a-defsite` and `backref-jrn-na-ok`.

## 4.8.2

### Changed — `derive-tasks` manifest is one uniform two-column `field | value` table (refines the 4.8.1 split-fix)
4.8.1 killed the "see table below" split by going to a field list. This refines that: the manifest is a **single `field | value` table** — one row per dimension (title/phase/afk/outcome on their own rows), no dimension escaping to a side block — and the two sub-structured fields render their structure **inside their own cell** with `<br>` line-breaks (a markdown cell can't hold a nested pipe-table). `behavior` is one `<br>`-line per `UC-` with its `AC-`s on following lines; `tests` is one `<br>`-line per AC inside the `tests` cell (`AC-id — tiers — test intent`), never a "table below" pointer and never a re-echoed `@covers` tag. Keeps the uniform table operators preferred while eliminating the split. SKILL.md + Output table + worked example all updated.

### Fixed — propagated 4.8.0/4.8.1 into the human-facing enumerations + freshened `audit-spec` (a consistency sweep found the doc-drift the tools couldn't)
The 4.8.0/4.8.1 changes (the `JRN-`/`INV-` id types, the 16b/16c backref-presence checks, the task-manifest format) were live in the tools but several authoritative *descriptions* of the system still predated them. A full-project sweep fixed all of them:
- **`dependencies.json`** — `ddd.produces_ids` now lists `INV` and `ux-reqs.produces_ids` now lists `JRN` (both owned per `lint_spec.py PREFIX_OWNER` but previously unclaimed); `docs/DEPENDENCY-GRAPH.md` regenerated to match.
- **`audit-spec`** — its "Below it — the linter (don't repeat)" enumeration now names the **16b/16c derived→driver backref-presence checks** (`JRN-`→`UC-`, `SLO-`→`NFR-`, `ML-`→`UC-`; impl-design `<module>.md`→`MOD-`/`T-`) and the fuller downstream-coverage map, so an auditor doesn't redundantly hand-judge them; **Phase 4 per-`T-` readiness** now checks the UI slice's `JRN-` journey reference and that its **`prototype-review` gate is settled** (an open HITL `visual/UX decision` escalation is `blocking`).
- **`generate-ui-prototype`** — `flows.md` is now keyed by the journey's `JRN-` id (it was keyed on the journey but carried only `UC-`/`DS-`, the anchorless pattern `JRN-` exists to kill); SKILL + worked example updated.
- **`docs/SPEC-CHECKS.md`** (map of every check) gains a **Derived→driver backref** row; **`docs/HOW-IT-WORKS.md`** and **`repo-layout.md` / conductor** corrected (08-ux now mints `JRN-`, no longer "no ids — a synthesis").

No tool/behaviour change — documentation and the dependency-graph data only.

## 4.8.1

### Changed — `derive-tasks`: the task manifest is a field list with the tests table inline, and `@covers` is no longer echoed in the manifest
The 4.8.0 AC-keyed tests table could get exiled to a "see table below" pointer when a task was rendered as a two-column `Dimension | Reference` table — a markdown cell can't hold a sub-table. The format now states explicitly: the manifest is a **field list** (`field: value` lines), and the **`AC-`-keyed tests table sits inline directly under `tests:`**, never a pointer to a table elsewhere. The table's third column is the **test intent** (the behaviour that pins the AC), not a re-echoed `@covers AC-` tag — tagging the actual test with the AC id is a test-file convention owned by `derive-conventions`, and the gate (`check_task_record.py`) only greps for the AC *id* in `tests/`, never the literal `@covers` string, so the manifest has no reason to restate it. Guidance + worked example updated; affects newly-generated tasks.

## 4.8.0

### Added — `JRN-` (journeys) and `INV-` (invariants) as first-class IDs, so downstream artifacts trace to them by id
Two upstream elements were referenceable only by prose or a heading anchor, breaking mechanical traceability. **`JRN-`** (owner `08-ux`, layer 4): every `grill-ux-reqs` journey now carries a stable id, so a task/test/traceability row links the journey **by id** instead of a fragile `#anchor` — and each journey cites the `UC-` it renders. **`INV-`** (owner `04-domain/ddd`, layer 1): each `grill-ddd` aggregate invariant carries an id, so an `AC-` traces to the exact domain rule it asserts (the `derive-functional` example's `INV-Job-LeadTime` reference now resolves instead of dangling). Both types are registered across the linter vocabulary and the five secondary tools that carry their own `TYPES` copy (kept in sync by `selfcheck.py`).

### Added — `lint_spec.py` enforces derived→driver backref PRESENCE (checks 16b/16c), not only reference direction
The linter enforced that every ID reference points *upstream*, but the *presence* of a backlink was enforced for only two correlated-keying edges (`AC→UC`, `ASR→NFR`). **16b** now requires a derived id to cite its driver by id **co-located on its own definition row/block** — `JRN→UC`, `SLO→NFR`, `ML→UC` (ERROR; `ML` allows an `N/A — why` escape) — suppressed when the parent's whole type is absent so a partial spec mid-derivation isn't penalised. **16c** requires each `derive-impl-design` `<module>.md` to name the `MOD-` it implements and the `T-` it serves (WARN). Edges whose driver is *not* co-located with the child's definition (`MOD→AGG/UC` — the `MOD-` id lives in `c4.md`, not the `modules.md` realises row; `ML→DATA`; `DATA→AGG` "where-modelled") stay format mandates, deliberately not linted, to avoid false positives. Nine regression tests cover both directions, premature-suppression, the `N/A` escape, and `INV-` resolution.

### Changed — the task manifest is ID-keyed and structured, and `DoD` is a reference, not a restatement
`derive-tasks`: **behavior** lists one `UC-` per line with its `AC-`s indented; **tests** is an `AC-`-keyed table (one row per AC → tiers → the `@covers AC-`-tagged test that pins it) rather than a prose blob with a flat `@covers` dump; **ux** references the `JRN-` journey + its interaction-states; a new **prototype-review** gate reviews the JIT-generated prototype before code — **auto-AFK** when it only renders a ratified journey, escalating to HITL only on a new visual/UX decision; and **`DoD`** now references the standard gate (the per-task Verification Record regenerated by `check_task_record.py --init`) plus the task-specific deltas, instead of hand-restating invariant rows that silently undersold the enforced bar (conformance/deploy/fitness/mutation).

### Changed — system-wide ID-traceability: a named backref field at every derivation hop
Each derived artifact now maps to its upstream driver by id via a named field, the same proven pattern as the existing `maps-to(SEC-)` / `x-serves(UC-/CMD-)`: `derive-architecture` modules record `realises(AGG-/UC-)` (or `N/A — why` for a technical/infra module); `derive-observability` SLOs record `maps-to(NFR-)`; `derive-impl-design` docs lead with `implements MOD- · serves T-`; `grill-ml-reqs` capabilities record `serves(UC-)` and `data-class(DATA-)`; `grill-data-reqs` lineage names the `AGG-`/`DATA-` ids where modelled. Worked examples updated to demonstrate each, including the two that previously mandated a backref in their rules but omitted it from the example (`derive-api-contracts` `x-serves`, `grill-monetization` plan→`ENTL-`).

## 4.7.2

### Fixed — `lint_spec.py` read a downstream *trace table* keyed on an upstream ID as an illegal re-definition
The definition-site scan (`DEF1` = an ID as the first token of a line/cell) registered a leading-cell ID as a *definition* regardless of area, while the inline-pair scan (`DEF3` = `<ID> <Name>`) already treated a leading ID as a definition only *inside its owning area* and as a reference elsewhere. So any downstream trace/evidence table keyed on the upstream ID it traces — exactly what `derive-architecture`'s `09-solution/arch/quality.md` does, one `ASR-` per row — false-fired both a duplicate-ID error (#12) and a defined-outside-owning-area error (#13). The skill's own worked example produced a guaranteed-non-clean spec, and the same false positive recurred across every derive worker that keys a trace/evidence table on an upstream ID.
- **Fix.** A leading-cell ID now registers as a *definition* only inside its owning area, mirroring `DEF3`. A **foreign** leading ID is a trace-table **row-key reference** — credited as a reference (so it resolves to its upstream definition and gives the upstream ID downstream-coverage credit), skipping table-header and authz-matrix rows. The misplaced-definition hole stays closed: a foreign leading ID that resolves to nothing upstream still errors, now as the more accurate `reference to undefined ID` rather than `outside its owning area`. General, not a per-file exemption — it clears the same class of false positive across all derive workers, so the `quality.md` example needs no change.
- Regression tests `foreign-leading-id-is-a-reference` (clean) and `foreign-leading-id-undefined-still-errors` (hole stays closed); the `duplicate-id` / owning-area checks still fire for real in-area collisions.

### Changed — `derive-engine` house style: linter-safe ID forms
Added a "Linter-safe ID forms" block to the shared derivation house style (applies to every derive worker), folding in the surface forms that the traceability tokenizer mis-reads and that cost recurring remediation rounds: cite an ADR by its **bare ID**, never as a link to its file; an ID is `PREFIX-NUMBER`/`PREFIX-CODE-NUMBER`, never `PREFIX-word`; no `area/word` slashes in prose; dot a suffix only for a real field ID; a YAML contract's `x-grillspec-id` is reference-only. It also records that keying a trace/evidence table on the upstream ID is now legitimate (the fix above).

## 4.7.1

### Fixed — `lint_spec.py` read per-task Verification Records as illegal ID *definitions*
The definition-site scan (`DEF1` = an ID as the first token of a line/cell) matched a Verification Record's leading-ID lines — its `# T-NNN — Verification Record` H1, and (for a feature task) every obligation row keyed on the `AC-`/`API-`/… it verifies — so the record registered as *defining* ids it merely *references*. Result: a duplicate-ID error (#12) plus a defined-outside-owning-area error (#13) on every record, e.g. the freshly `--init`-ed `spec/10-delivery/verification/tasks/T-001.md`.
- **Fix.** Files under `…/verification/` are now exempt from the definition-site scan — they record results *about* ids and never define one, the same reference-only nature as the existing `traceability.md` exemption (which lives in that directory). One exemption at the single `defsites`-population point clears both checks, for the H1 **and** the obligation rows, and validates **existing** on-disk records without regeneration (a title-only change couldn't, without `--force`-overwriting a filled-in record).
- Regression test `verification-record-not-a-defsite` (H1 + an `AC-` obligation row); the `duplicate-id` test still fires, so the real define-once / owning-area checks aren't blunted.

## 4.7.0

### Added — deploy/CI + schema migrations are production too: realness gates that close the "silently skipped deploy" hole
A task could generate code and *quietly omit the deploy script / CI stage / migration* — "deduce the infra isn't ready" — and report done with a green suite, because nothing made the delivery artifacts an accountable obligation. Production-only/no-fakes was enforced for `src/` but not for the artifacts that actually ship it.
- **`check_deploy_real.py`** — a high-precision tripwire against a faked/skipped deploy across the CI/deploy surface: GitHub/GitLab/Circle/Azure/Bitbucket/Drone/Cloud-Build/Jenkins configs, shell deploy scripts, Dockerfiles, and `package.json`/`Makefile` deploy targets. A `# TODO`/placeholder is an ERROR; a disabled (`if: false`) or command-less ("echo-only") deploy is a WARN. Recognition is project-extensible via `.claude/deploy-real-commands.txt`; inline `deploy-real: allow` + `.claude/deploy-real-allow.txt` waive. By design it confirms a real deploy *command* runs, not that it targets the *ratified* env — that's the behavioural check's job (below).
- **`check_migration_real.py`** — the same tripwire for schema/data migrations (files under a migration home): a placeholder is an ERROR; a DDL-less `.sql`, an empty `operations = []`, or a `pass`-only migration is a WARN. An empty *down/rollback* migration is treated as a legitimate no-op. Non-standard homes extend via `.claude/migration-real-dirs.txt`.
- Both ship regression suites; the e2e gate-chain now proves **five** accountability gates compose on one realistic project (a clean task passes all five; each cheat trips exactly the gate that owns it). Both run in the project's code pre-commit + CI (wired by `derive-conventions`).

### Changed — deployment + the full test set are first-class checked obligations; the bar can't be shrunk by omission
- **Per-task Verification Record carries `deploy` + `tests:layers` rows**, and **every standard gate row must now be present** in a `status: done` record (`check_task_record.py`). Omitting a row — the exact "silently dropped artifact" cheat — is an ERROR, not a silent pass. `deploy` evidence is the green e2e/smoke against the deployed env (or `blocked — <env> not provisioned`); `tests:layers` evidences every test level the slice touches.
- **e2e/journey/smoke/NFR-evidence run against a REAL deployed environment** (an ephemeral per-PR preview env by default, or a reserved e2e/staging env named in `test/levels.md`), never a local `docker-compose`/testcontainers stack (that's the *integration* tier mislabelled). A green e2e against the deployed env is therefore the *authoritative* deploy proof; the static tripwires are the backstop for the pre-provision window.
- **The first deploy target is the first env of the ratified promotion path** (per `infra-ops/topology.md`), no longer hardcoded "dev"; `cicd.md` now owns the explicit end-to-end promotion workflow (ordered hops + per-hop gate), and the build skills consume it rather than re-deriving.
- **Propagated across the family** (one stance, every skill): the exec-engine done-gate/DoD/anti-cheat invariants, `conformance-review` (deploy + migration lenses, confirm e2e hit the deployed env), `derive-tasks` (`deploy` dimension), `implement-task`, `derive-infra-ops`, `derive-test-strategy`, `derive-conventions` (project hooks/CI), `migrate-data`, `deploy-release`, the conductor **lite path** (the no-fakes bar never relaxes; only the promotion ceremony scales down), and `audit-spec` (delivery-readiness now requires the promotion path + named e2e target env to exist). Docs (`HOW-IT-WORKS`, `SPEC-CHECKS`) updated.

## 4.6.0

### Added — check 11d: illegal downward *path* references (closing the upstream-only blind spot)
The direction invariant (upstream-only references) was enforced only on ID *tokens* (11b/11c). A forward pointer written as a **file path or markdown link** carried no ID, so it slipped governance entirely — an L2 requirement could cite `infra-ops/prerequisites.md`, or an NFR could say "RPO target owned by infra-ops/test", and nothing flagged it. (How `06-requirements` artifacts ended up pointing down at `09-solution` in practice.)
- **New check 11d.** Resolves a referenced path's first segment to its area layer (numbered stage prefix, or an unambiguous bare leaf like `infra-ops`/`arch`/`api`/`tasks`) and WARNs when it is strictly downstream of the citing file. Skips fenced code; exempts ADR sources (cite drivers by design), `traceability.md`, and spec-root orchestration files — same as the ID checks. `data`/`security`/`ml` (which live at both L2 and L5) only resolve via a numbered-prefix path, never the bare name, to avoid false positives. The message points at the fix: invert the reference (the downstream artifact cites the requirement) and a requirement states its own value rather than deferring it downstream.
- **Audit.** A full per-layer sweep of all skill definitions + the three shared engines confirmed no skill *instructs* this defect: the upstream-only + own-your-value rules already exist and are strongly worded (grill-engine §user-owned-values names RTO/RPO; derive-engine "never invent a value the upstream should have carried"; audit-spec Phase 4 detects un-ratified values). The gap was purely mechanical enforcement of the path/link form, now closed.

## 4.5.1

### Fixed — `lint_spec.py` flagged literal external-vendor strings as spec violations inside code
Two checks scanned every line with no fenced-code/inline-code skip — unlike the undefined/downward-ref checks, which already do (`:297`). An operate-stage runbook documenting real third-party identifiers had no legitimate way to write them.
- **Rule 13b (context-namespaced IDs)** now skips fenced blocks and inline `code` spans. A vendor identifier shaped like `<lead>-<TYPE>-…` (Alpaca's `APCA-API-KEY-ID` header → lead `APCA`, type `API`) is literal content, not a banned `<CTX>-TYPE-NNN` spec ID, when it sits in code. (13b's own INFO-level sibling `CTXID` already skipped fences; this removes that inconsistency too.)
- **Placeholder check (`{{`/`}}`)** now skips fenced blocks and inline `code` spans, so a vendor template (`{{user.public_metadata.role}}` — Clerk session-token claims, Handlebars configs) is documentable verbatim instead of forcing "double-curly braces" prose.
- Both gain regression fixtures (a bare occurrence still fires; the same inside a fence or inline code does not).

## 4.5.0

### Added — build-accountability layer: production-only code, enforced TDD bookends, and a per-task Verification Record
The system prescribed TDD-first and a post-task conformance review, but "done" was self-attested — an agent could ship production code containing fakes/stubs to pass early stages, skip writing tests first, or never run the conformance review, and nothing caught it because the tests went green against the fakes. This release makes the bookends mechanical.
- **Production code is production-only (`exec-engine`).** A stub/mock/in-memory-double/canned-response/`unwired-fallback` in `src/` is **not done**, even when every test is green — test doubles live only under `tests/`. An unconfigured external system is a blocking prerequisite to escalate (`_human-input.md` + `bootstrap.md`), never a licence to fake; an absent dependency must keep the test **red** until it's supplied, never be coded around. New shipped tripwire **`check_no_fakes.py`** (cross-language: a `Fake*/Stub*/Mock*/Dummy*` definition or a mocking-library import in `src/` is an ERROR; placeholder/`unconfigured→fallback` bodies WARN; allowlist for the rare legit case) — the belt to the per-language no-fakes architecture-fitness-function's suspenders (`derive-test-strategy`).
- **The process bookends are part of Done, not optional steps.** Tests-first is enforced by its trace (every `AC-` has a failing-capable, `@covers AC-`-tagged test, verified against the test **source** — not a self-authored matrix); the conformance review is a real independent `VERDICT: PASS` artifact on disk or it didn't happen. `conformance-review`, `autorun`, `implement-task`, and the `exec-engine` done-gate/DoD all gate on both.
- **The per-task Verification Record + `check_task_record.py`.** Each task gets `spec/10-delivery/verification/tasks/T-NNN.md`, an obligation table **generated from its frozen spec references** (`--init`) so the bar can't be authored to mark its own homework. The checker fails a done-claim that left an obligation unmet, dropped one, has no independent verdict, an `AC-` with no tagged test, a fabricated evidence path, or coverage below its bar; `--report` renders a readable, tool-vouched ✅ completion report (the per-task reassurance artifact). In-progress records never block; only an unbacked done-claim does.
- **Held-out acceptance criteria (`autorun`).** An anti-overfitting policy for orchestrated runs: withhold a black-box `AC-` subset from the implementer, verify it independently at the gate; `check_task_record` requires the full frozen set regardless, so held-out criteria can't be dropped. N/A for a solo run (the human is the independent check).

### Added — ops: a bulletproof, phased, per-platform setup runbook + deploy verification
`bootstrap.md` was one underspecified line ("a checklist"), and nothing mapped configuration across environments — so an operator had instructions but no way to verify their setup, and the classic "missing env var in prod" outage had no guard.
- **The environment×configuration matrix (`derive-infra-ops` → `environments.md`)** — every key/secret · purpose · per-environment {value-source · where-stored · owner} · the cross-environment relationship (which envs share a value vs. stand alone). **`prerequisites.md`** is now an operationally-complete per-platform provisioning guide targeting each platform's current console, tagged by phase (initial/pre-launch/later) and audience (ops-admin/sys-admin/developer).
- **`bootstrap.md` is now an executable runbook** composed from those + `runtime-contract.md`: phased (A initial → B production/pre-launch → C day-2), with an env-var worksheet (capture→store→author-per-env) and the canonical startup order (provision → migrate → seed → flags → deploy → preflight → smoke). `deploy-release` fills Phases B/C.
- **`check_config_drift.py`** reconciles the env vars the code reads against the declared matrix — an undeclared read is an ERROR (the operator can't provision it). Conventions now mandate a **`preflight`/`doctor`** command + `/healthz`·`/readyz` endpoints so an operator can *verify* an environment meets the code's needs before serving traffic.
- **Production-Readiness Review gate (`deploy-release` → `production-readiness.md`)** — the first prod promotion passes a consolidated, verified-not-just-planned checklist (security review · rollback rehearsed · backups restore-proven · SLOs receiving data · preflight green · config-drift clean · cost guardrails).
- **Regression + e2e coverage.** Each new tool has a regression suite; `test_e2e_gates.py` proves the three gates compose on one realistic project (clean passes all; each cheat trips exactly its gate). All wired into CI; `selfcheck` keeps the new tool's `TYPES` in sync; docs (`HOW-IT-WORKS.md`, `SPEC-CHECKS.md`) updated.

#### Regenerating an existing project
No task/spec re-derivation. Update the plugin, re-vendor `tools/` into `.claude/tools/`, then re-run the three downstream DERIVE skills whose output changed: **`derive-conventions`** (→ `@covers`, no-fakes + config-drift hooks, single verify target, preflight/health, `runtime-contract.md`, regenerated `CLAUDE.md`), **`derive-infra-ops`** (→ `environments.md`, enriched `prerequisites.md`), **`derive-test-strategy`** (→ the no-fakes fitness function). Everything upstream (discovery → requirements → functional → architecture/data/api/security) is untouched. Verification Records appear for new tasks via `--init`; already-merged tasks are opt-in.

## 4.4.0

### Added — user-owned values must be ratified, not silently filled (+ environment/git ratify-points, human-prereq task dimension)
The system's rule that a user-owned value is "proposed-as-default-then-ratified" lived in `decision-classes.md` but wasn't enforced at the engine level, so grill/derive skills filled the cell with a number to avoid a blank — silently baking in the user's NFR targets, retention, pricing, SLAs, environments, thresholds, etc. (A cross-skill audit found ~25 such spots.)
- **Engine-level ratify rule.** `grill-engine.md` and `derive-engine.md` now carry an explicit rule: for any user-owned VALUE (targets/thresholds · commitments · risk/scope calls — full list enumerated), propose a profiled default but **mark it an unratified `ratify`/`unconfirmed` default and surface it for confirm/override** (ask inline when interviewing; park in `_human-input.md` when unattended). Proposing ≠ deciding; an un-ratified load-bearing value is an assumption, not a requirement. Every grill/derive skill inherits this.
- **Environment set + git workflow are explicit ratify-points** — `derive-infra-ops` no longer silently bakes the dev/stage/prod triple (propose it + the promotion path, ratify count/purpose); `derive-conventions` no longer hard-asserts trunk-based (propose it, ratify the branching model). Parallel to the existing cloud/region ratify-point.
- **New `human-prereq` task dimension** (`derive-tasks`) — every slice declares the human actions it can't proceed without (account/credential/enabled-API/OAuth/DNS/secret), as step-by-step actions referencing `prerequisites.md` by name+location (never the value), front-loaded to `_human-input.md` before dispatch so the build never stalls mid-slice.
- **Detailed human-input instructions** — `prerequisites.md` and the `_human-input.md` queue now require per-item step-by-step provisioning actions (what to create, where to inject — never the secret value), actionable by a non-expert.
- **Audit enforces it** — `audit-spec` Phase 4 now flags an un-ratified load-bearing user-owned value (`blocking` on a critical-path one) and an unmet `human-prereq`.
- **Always recommend, for fast-agree.** Every ratify-point must arrive with a concrete recommended value + one-line why, framed as a scannable `<value> — <why> · agree?/override` batch — never a blank or open question. The human confirms fast, doesn't author.
- **Production go-gates.** `deploy-release` no longer "never blocks a release": a PROD promotion is a human go/no-go (recommended default: auto dev→stage, human go for stage→prod); the metric gate still owns canary *health*. `migrate-data` adds the same for a non-destructive prod cutover, mirroring its irreversible-deletion gate.
- **Fixed the auto-merge contradiction.** `afk: eligible` (agent self-merges) collided with the conventions' ≥2-person-review / branch-protection mandate. `eligible` now auto-merges only where the review policy permits solo-merge; otherwise the agent opens a green PR and parks the merge as a HITL gate (a new closed-list HITL trigger). `derive-tasks` + `exec-engine` aligned.
- **Explicit per-skill ratify-points** (higher-signal than the generic engine rule, each carrying a recommended default): NFR target numbers (`grill-quality`), prices + value-metric + customer SLA (`grill-monetization`), the Core/Supporting/Generic subdomain split (`grill-ddd`), authorization *allow* rules + accepted-risk (`grill-security-reqs`), the IdP commitment (`derive-security-architecture`), residency-consumes-confirmed-footprint + retention (`grill-data-reqs`), coverage % + mutation score bars (`derive-test-strategy`).

## 4.3.0

### Added — universal upstream-only for ALL id-shapes (registered or not), + 6 newly-registered types
The illegal-downward-reference check walked `IDTOK`, which only tokenizes registered `TYPES` prefixes — so a token shaped like a spec id with an *unregistered* prefix was invisible and escaped the upstream-only invariant entirely. That is how a downstream `BR-` (boundary rule, an L6 delivery-conventions construct) cited *upward* from requirements/architecture slipped governance. The fix decouples direction-safety from registration.
- **New check `11c` — definition-anchored universal direction.** Any id-shape (ALL-CAPS 2–5 char prefix + `-…`) that is *defined* somewhere takes its layer from the most-upstream file it's defined in; a reference from a strictly-lower layer is a downward violation (WARN). Only *defined* shapes get a layer, so a standard cited in prose (`RFC-7231`, `WCAG-2.1`) is ignored, and a free *local* id stays free — only a downward use warns. Registration is now about *extra* governance (coverage · define-once · owning-area), never about direction safety. This supersedes the unreleased 4.2.x "register-or-deidify" blanket warn, which would have nagged every free local label.
- **Registered 6 element types** the skills already produce but left untyped: `FAC-`/`REPO-`/`SVC-` (factories · repositories · domain services, L1 ddd), `IF-` (boundary interfaces, L0 system-context), `MOD-` (architecture modules, L5), `CA-` (capability/scope areas, L0 product). Added to `TYPES` (mirrored across `impact`/`spec_status`/`check_contracts`/`check_freshness`), `ID_LAYER`, `PREFIX_OWNER`; declared in their producing skills and `dependencies.json`. They now get the full ERROR-level direction + define-once + owning-area treatment.
- **`ACT-` (actors) intentionally left to the universal rule, not registered.** Actors are legitimately rostered in *both* `grill-system-context` (the C4 boundary roster, upstream) and `grill-ddd` (discovered during event-storming) — a real dual roster. Registration's define-once would flag that as a duplicate, and forcing a single owner breaks one skill's role. The universal rule enforces upstream-only on `ACT-` while *tolerating* the dual roster (it anchors to the most-upstream definition), which fits the actor model better than registration would.
- Added regression tests `unregistered-id-downward`, `unregistered-id-local-ok`, `registered-newtype-direction`.

## 4.2.9

### Fixed — `lint_spec.py` event-coverage missed `POL-` trigger columns with no `whenever` keyword
4.2.8 credited events on a reaction line only when it carried a `whenever`/`reacts-to` keyword. A policy written as a table row whose `trigger`/`when` column simply lists its events — `·`-joined and/or parenthetically annotated (`EVT-510 CohortReleased (operator releases …)`) with no keyword — was not recognized, so those events false-WARNed as having no consumer.
- A row that **defines a `POL-`** (its row-key or an inline `POL-` definition) now credits every event named on it as consumed, keyword or not. `IDTOK` extracts each `EVT-` id whole, so a trailing `(annotation)` or a `·`-joined sibling never hides it.
- Added regression test `event-consumer-policy-trigger-column-no-keyword`.

## 4.2.8

### Fixed — `lint_spec.py` EVT sink/consumer detection only saw the first id per line
A follow-up to 4.2.7's block-scan: `_dpos` recorded one def per line, so a sink marker on a non-first event in an inline `events: A · B · C` list was never scanned, and a `whenever` reaction whose events sat in a `·`-joined cell separate from the keyword credited only the ids REFMARK captured after the keyword. Result: `EVT-208` carried `audit-only` yet still WARNed; events with a real shared `POL-` consumer WARNed.
- The block-scan now records EVERY owner-area id on a line (all `DEF3` matches, not just the first), and on a multi-id `·`-joined line each id is scanned against its OWN segment — so a marker on the 2nd of three events attributes to that event, not the first.
- A `whenever`/`reacts-to` reaction line now credits ALL events named on it (refset-only, no error path), regardless of which cell holds them — so events listed in a `·`-joined cell apart from the keyword are consumed.
- Added regression tests `event-sink-non-first-in-joined-list` and `event-consumer-joined-whenever-cell`.

## 4.2.7

### Fixed — `lint_spec.py` coverage false-positives on non-SEC threat mitigations and non-UC event consumers
Two structural-coverage checks credited only one narrow downstream shape and false-WARNed on legitimate alternatives.
- **`THR-` coverage** required a back-referencing `SEC-` control. A threat mitigated by a *non-SEC* control — an `ADR-` structural layer, an `OBL-`/`DATA-` compliance control — or explicitly **accepted-risk**, carries that on the threat's own row (a forward cite that never lands in the reference set), so it false-WARNed. The check now also credits a `THR-` whose definition block forward-cites a control (`SEC-`/`ADR-`/`OBL-`, or a `DATA-` near a mitigation cue) or is marked accepted-risk. A genuinely unmitigated threat still WARNs.
- **`EVT-` consumer** missed two real consumers: a cross-context `POL-` reaction phrased `whenever EVT-x then CMD-y` (the DDD policy convention — `whenever`/`reacts-to`/`consumed-by`/`consumes` are now reference markers, so a reaction in any context, including a deferred one, credits its event), and an intentional **terminal sink** (an `audit-only` / `operator-console-internal` event deliberately absent from the published asyncapi catalog), now recognized as complete rather than orphaned. A true orphan event still WARNs.
- Added regression tests `threat-coverage-nonsec-controls` and `event-consumer-policy-and-sinks`.

## 4.2.6

### Fixed — `lint_spec.py` state-machine checker mis-parsed a compound `from`/`to` cell
A transition row whose `from` (or `to`) cell listed several states as `A / B` — shorthand for multiple states sharing the row's trigger/guard — was read as one state named `running / awaiting-retry`. That phantom never matched the real `running`/`awaiting-retry` states defined in other rows, so both were falsely flagged unreachable and/or dead-end.
- The checker now splits a `from`/`to` cell on ` / ` (spaces required, so kebab names like `awaiting-retry` and `n/a` are untouched), normalizes each part, and expands the row into the cartesian product of source×target transitions. All existing marker logic (`(initial)`/`(terminal)`, nondeterminism) is preserved. Added a regression test (`state-machine-compound-from-cell`).
`decision-classes.md` protected user-owned *values* (SLAs, retention, jurisdictions) as ratify-not-invent but never named user-owned *vocabulary* — so the universal "default hard toward deciding" had no counterweight for naming, leaving UL definition to a stance rather than a rule. A bare-idea or expert-user start could therefore coin a generic-but-wrong domain term and move on without surfacing it, producing the wrong-but-consistent model the audit's Phase 3 calls the costliest failure.
- Added an **edge call**: a domain term (entity · command · event · role · state) the domain already has a word for is an ASK — proposed for confirmation, never silently christened; a label coined for a genuinely-new concept is allowed but **marked coined** (`inferred`, or a `HOT-` if contested) so the expert can supersede it. Harvest an expert's jargon from provided input and confirm rather than override with a synonym.
- Tightened `grill-ddd` step 4 ("build the ubiquitous language") to make "agree the terms" explicitly propose-and-confirm, with coined terms flagged.

## 4.2.4

### Added — `check_freshness.py`: an advisory artifact-staleness guard (grilled AND derived)
`guard_derived.py` proves a derived file wasn't hand-edited but cannot prove it was re-derived after upstream moved, and it says nothing about a *grilled* artifact going stale when an upstream definition it cites changes. New `check_freshness.py` closes that gap as the complement of the derived-guard: where `guard_derived` is hash-of-self, this is hash-of-upstream-inputs.
- It records each artifact's cited-upstream **definition-block** hashes into `.claude/freshness.lock`, and at check time lists any artifact — in either zone — whose cited definition has drifted since the artifact was last reconciled. Granularity is the cited ID's definition block, so an unrelated edit elsewhere never false-flags.
- **Advisory by design** (default exit 0; `--strict` to gate). The system prevents stale work by propagation, not by a status flag — this only hands the auditor the precise candidate set, it never blocks a commit.
- Wired in: `audit-spec` Phase 0 runs it and Phase 2's staleness check (renamed derived-staleness → **artifact-staleness**) consumes the candidate list; the conductor records `freshness.lock` beside `derived.lock` after reconciling any area; `selfcheck.py` guards its TYPES vocabulary against `lint_spec.py`; `operator-map.md` documents it as the spec-side analogue of the `impact.py --since` propagation net.

### Added — `audit-spec` Phase 0 now runs `check_contracts.py` when API contracts exist
The audit's mechanical baseline invoked `lint_spec.py` / `spec_status.py` / `guard_derived.py` / `impact.py` but not the contract↔ID binder, so a spec with `openapi.yaml`/`asyncapi.yaml` got no deterministic check that its contracts point at real IDs — the audit would only catch a contract defect if it happened to read the file during the judgment pass.
- Phase 0 now also runs `check_contracts.py` when `spec/09-solution/api` exists: every grillspec id a contract references (`x-grillspec-id` · `x-serves` · `SEC-` scopes · `x-data`) must resolve to a real definition (ERROR → `blocking`); every REST op must carry its traceability hooks + a mutation security scope + an error response (WARN → `important` candidate). It no-ops cleanly without PyYAML or the api folder, so it is always safe to attempt.

## 4.2.3

### Changed — `audit-spec` reports fixes as dependency-ordered chains, not authored/derived buckets
A single audit finding often spans both zones: a defect *located* in an authored artifact can be *root-caused* upstream and *propagate* into a re-derive (a wrong `06-requirements` item whose real cause is `ddd`, fixed by editing ddd → re-deriving `05-functional-spec` → re-grilling the requirement). Splitting the session summary into flat "authored zone / derived zone" lists hid this and read as a contradiction (consuming a derived artifact never makes the consumer derived; fix-zone is set by who *writes* the file, propagation by the reference graph).
- The Output section now mandates the session summary print each finding as a dependency-ordered fix-chain (`symptom → upstream edit → re-derive → re-grill`), sequenced so every edit precedes the re-derivations that consume it.
- The "Top fixes" report row is aligned to the same chain format, so the report table and the live summary no longer disagree. Detection logic is unchanged — this is a presentation fix.

## 4.2.2

### Fixed — `check_contracts.py` false positives against a complete spec
The contract↔ID binder diverged from `lint_spec.py`'s tokenizer, so a lint-clean spec produced spurious errors.
- **Inline `<ID> <Name>` definitions were not harvested.** The defined-id set only recognized leading-cell / `id:` forms; it missed grill-ddd's prescribed inline enumerations (`commands: CMD-101 Ingest · CMD-103 …`) and the event-flow `EVT- ⟵ CMD-` form that `lint_spec.py` accepts. Added lint_spec's DEF3 pattern to the harvest, so every `CMD-`/`EVT-`/`RM-` a contract references now resolves.
- **The ID tokenizer captured trailing prose punctuation.** `IDCORE` ended `[A-Za-z0-9._-]*`, so a description like `Realizes RM-601.` tokenized as `RM-601.` and read as undefined. Aligned `IDCORE` to `lint_spec.py`'s form (mandatory trailing alnum) — `DATA-Customer.id` is still captured whole; a sentence-ending dot is not.
- **Document-level OpenAPI `security` inheritance was ignored.** The mutation-needs-authz WARN read only the operation's own `security`; per OpenAPI a root-level `security` applies unless the operation overrides it. The check now uses the effective requirement (op-level if present, else document-level), so a globally-secured contract no longer false-flags every mutation, while an explicit op-level `security: []` override still warns.

## 4.2.1

### Fixed — ID-tokenizer correctness
- **`impact.py` / `spec_status.py` ID boundary.** Both tokenized IDs with a left boundary of `(?<![A-Za-z0-9])`, omitting the `-` that `lint_spec.py`/`check_contracts.py` use. A namespaced or hyphen-prefixed token (e.g. `SUR-AGG-250`) therefore leaked a phantom `AGG-250` into the change-impact graph and the status rollup. Aligned both to `(?<![A-Za-z0-9-])`, and aligned `spec_status.py`'s ID tail to `lint_spec.py`'s `IDCORE` so dotted IDs (`DATA-Customer.id`) are no longer truncated.

### Added — drift guards for the duplicated lookup tables
- `selfcheck.py` now diffs `impact.py` `layer()` against `lint_spec.py` `file_layer()` (the second hand-copied path→layer table — the first, `TYPES`, was already guarded) and errors on drift, so impact ordering can't silently diverge from the linter.
- `gen_depgraph.py` `validate()` now errors when a `dependencies.json` stage has no `STAGE_LABEL`, turning a latent `KeyError` in `render()` into a clean validation failure.

### Changed — whole-project consistency sweep
- Corrected stale skill/area counts (root `marketplace.json` 43→45 workers; `README.md` 44/43→46/45).
- `operator-map.md` standard flow updated to the 4.0.0 layer model: foundation lists `constraints`/`system-context`, `design-system` (L3) and `ux` (L4) are their own steps before architecture-readiness, and `entitlements`/`ml-reqs` join the requirements set. Lite-path `context`→`constraints` in `operator-map.md` and `conductor-playbook.md`.
- `repo-layout.md` per-area `kind` description corrected (it named a nonexistent `reference` value); `dependencies.json` `_comment` aligned.
- Unified all 45 worker descriptions to "Loads the shared … **engine**" (matching the `*-engine.md` filenames; the tagline was split "core"/"engine").
- `audit-spec` de-skill-named for self-containment (names activities/areas, not sibling skills); added the standard `**Stable IDs**` line to `grill-compliance` (`OBL-`), `grill-ml-reqs` (`ML-`), and `grill-growth` (`EXP-`).

## 4.2.0

### Added — structured-fact enforcement, contract checking, and a whole-spec audit skill
The linter and tooling now mechanically enforce the canonical-form structures the engine already prescribed, the API/event contracts are bound to the spec ID graph, and a new judgment skill audits the whole spec.

- **`lint_spec.py` — new sound checks.** State-machine integrity (unreachable / dead-end / nondeterministic transitions over a `from·trigger·to·guard` table), authorization completeness (every `CMD-` has a rule; no blank decision cell — scoped to `06-requirements/security`), typed-scalar-fact consistency (a `retention`/`residency`/`class`/`SLA`/`price` stated twice must agree; every `DATA-` carries class/retention/residency), **task-graph acyclicity** (the `depends-on` DAG — ERROR), `THR-→SEC-` coverage, task→upstream traceability, NFR `enforced-by`, module `role:`, and ADR `status:`. New checks are WARN (slot-not-value, partial specs stay legal) except the DAG cycle and the existing unresolved-gap ERRORs.
- **`check_contracts.py` (new) + `spectral-grillspec.yaml` (new).** The `openapi.yaml`/`asyncapi.yaml` contracts are checked in two layers: Spectral (`spectral:oas` + house rules: RFC 9457 errors, per-operation authz, the `x-grillspec-id`/`x-serves` traceability extensions) for structure/style, and `check_contracts.py` for the cross-layer ID resolution no off-the-shelf tool can do (every `x-serves`/`SEC-`/`DATA-` a contract references must resolve to a real spec element). Wired into the spec-governance pre-commit hook; `lint_spec.py` now credits contract YAML toward `EVT-`/`API-` coverage.
- **`audit-spec` (new skill).** The judgment layer above the linter — consistency (contradictions, scope adherence, decision coherence) and domain/usage completeness (what's *missing*, not just broken), with a code-gen-readiness verdict. Two depths (`consistency` / `full`); writes its report to the project root, not into `spec/`. Wired into the conductor menu and the operator-map verification surfaces.
- **Conventions.** `grill-engine.md` invariant #9 (canonical-form facts are structured and stated once); the producing skills (`grill-ddd`, `grill-data-reqs`, `grill-security-reqs`, `grill-quality`, `derive-architecture`, `derive-api-contracts`) now prescribe the exact parseable shapes.
- **Tooling integrity.** `test_lint_spec.py` (new regression suite, run in CI); `selfcheck.py` keeps the `TYPES` prefix vocabulary in sync across `lint_spec.py`, `check_contracts.py`, `impact.py`, and `spec_status.py`. Fixed drift in `impact.py` (missing layers + 8 ID prefixes) and `spec_status.py` (8 missing prefixes). `SPEC-CHECKS.md` (new) documents the full enforced surface.

### Fixed
Stale `requirements/functional/` paths (canonical is the top-level `functional-spec/`), stale stage numbers and skill counts across the docs, and two worker-skill self-containment slips.

## 4.1.0

### Added — workspace is the only source of truth (no git history, no out-of-folder reads)
All three shared engines now carry an explicit **source-of-truth fence**, closing the gap where the conductor would improvise reasoning like "the prior files were removed but may be recoverable from git as a re-grillable draft." Grilling, derivation, and execution now operate on the **current working tree exactly as it exists now** — and nothing else.

- **`grill-engine.md`** (all `grill-*` + conductor), **`derive-engine.md`** (all `derive-*`), **`exec-engine.md`** (`implement-task`, `deploy-release`, `migrate-data`, `operate-incident`, `diagnose`, `conformance-review`, `autorun`, `generate-*`, `prototype`, `run-tests`): never mine **git history** (commits, `git log`/`git show`, stashes, branches, reflog) as a baseline or content source. A removed file is **gone, not a recoverable draft**; "it used to work" is settled by the current code; **missing prior work is a gap to surface/escalate, never something to reconstruct**.
- **Never read or write outside the project folder** — no parent dirs, home dir, sibling repos, or absolute paths beyond the workspace root — unless the user **explicitly hands over** that path/doc/file.
- **Legitimate git uses preserved:** `git diff` for incremental change-set detection (derive), branch/commit mechanics and `git bisect` for regression localisation (exec/`diagnose`). The fence governs the *baseline*, not git as a tool.
- **`conductor-playbook.md`** brownfield entry mode reinforced: "existing" = the current working tree only; missing prior work is a **tracked gap to re-grill**, not a draft to recover.

## 4.0.0

### Changed — design-system and ux are extracted into their own top-level layers (BREAKING: spec folder renumber)
`design-system` and `ux` were subfolders of `06-requirements/`. They are **experience design**, not constraint-requirements — the design system is the visual + interaction contract; ux journeys synthesise it with the requirements. They are now **two distinct reference-layers of their own**, between requirements and the solution:

| was | now | reference layer |
|---|---|---|
| `06-requirements/design-system/` | **`07-design-system/`** | L3 |
| `06-requirements/ux/` | **`08-ux/`** | L4 |
| `07-solution/*` | `09-solution/*` | L5 |
| `08-delivery/*` | `10-delivery/*` | L6 |
| `09-commercial/*` | `11-commercial/*` | L2 (post-launch sink) |
| `10-operate` | `12-operate` | L6 |

- **Distinct layers, not just folders.** `lint_spec.py` (`file_layer`/`ID_LAYER`) now places design-system at **L3** and ux at **L4**, so the **upstream-only rule enforces the direction**: a requirement can't reference the design system, and the design system can't reference ux. `DS-` ids are L3; `API-`/`SLO-` are L5; `T-` is L6.
- **Architecture-readiness gate** now requires `design-system` + `ux` done (they feed the solution) and sits *after* ux.
- **Stages** renumbered to match: design-system = stage 3, ux = stage 4, solution = 5, delivery-prep = 6, execution = 7, operate = 8, commercial (post-launch) = 9.
- Updated `repo-layout.md` (tree · tier diagrams · the L-chain · derived/authored zone lists), the conductor stage map + gates, `dependencies.json` (the `stages` list + each area's `stage`), `lint_spec.py` (`LEAF_DIRS`·`AREA_DIR`·`PREFIX_OWNER`·`file_layer`·`ID_LAYER`·the readiness-gate set), `guard_derived.py`/`impact.py`/`gen_docsite.py` paths, and every skill/doc/example that cites a numbered folder.
- **Naming:** the `design-system` spec area (`07-design-system/` — the `DS-` contract) is distinct from the non-spec `design-system/` **asset zone** it points at (raw tokens/assets code consumes); grill-design-system's output line now says so explicitly, since the old `06-requirements/design-system/` path no longer disambiguates them.
- **`derive-impl-design` relocated `09-solution/impl/` → `10-delivery/impl-design/`, deleting the last lint exemption.** It's a `derive-*` artifact (it *originates* module-internal design — pure spec), but it **consumes the task it elaborates**, so sitting in solution (L5, upstream of tasks at L6) made it reference downstream and forced a special-case exemption in the downward-reference check. Moved to the delivery band (**L6, same layer as tasks**) where the `T-` reference is same-layer and legal; its `stage` is now `7-execution` (where it runs JIT). **The exemption is removed, not patched** — the artifact now sits at its true dependency position. (The UI prototype stays a non-spec render in its own zone — `derive-*` originates spec, `generate-*` renders it; that line is what splits them.) Updated `lint_spec.py`, `dependencies.json`, `guard_derived.py`, `gen_docsite.py`, `repo-layout.md`, the conductor, `conductor-playbook.md`, `generate-docs`, and the skill's own output path.

## 3.1.8

### Changed — the UI prototype is a task-finalization artifact, not a coding-loop step (and it's opt-in)
3.1.7 placed `generate-ui-prototype` **inside** the execution loop, right before `implement-task`. That created an unresolvable fork: a JIT prototype can't be both *reviewable* (the human wants to tweak the screen) and *AFK-compatible* (an autonomous run can't break to show every screen). Two corrections:
- **Moved to task finalization.** The prototype is now produced + reviewed/tweaked + **frozen into the task** when the task is finalized — the attended, batched design-review window that sits **before** the build run. `autorun` then builds against frozen, approved prototypes and never has to stop for a screen. A design surprise that only surfaces mid-build is the normal GAP path: `autorun` parks that one slice (HITL trigger → `_human-input.md`) and continues on the rest. Updated the conductor execution loop, the "Task readiness" section, the ANY-STAGE line, and the key-edges line.
- **Made it opt-in (answers "is a prototype obligatory for every UI task?" — no).** A prototype earns its place only when the slice's `ux` dimension carries **slice-specific composition** (a new screen/flow, non-obvious states). A slice the **IA + design system already fully determine** (existing components, obvious composition — a copy change, a field on an existing form) marks `ux` `N/A — reuses DS-… on the existing screen` and skips it. Same opt-in logic as `derive-impl-design` (design-first slices only). Reframed `generate-ui-prototype` (description, a new "When it runs (and when it doesn't)" section, Process step 4 = freeze-into-task).
- **Documented the autorun-JIT fallback.** A UI slice that reaches the autorun queue *without* a frozen prototype has one generated just-in-time and builds against it unattended (the build reference + after-the-fact record, minus the review-first window). To force a review, withhold the slice from the queue — that *is* the gate; no separate flag exists or is needed (so "if any" no longer reads as "a prototype must exist before any run").
- **`exec-engine`: a missing design-system element mid-build is a GAP to the design system, never bespoke-styled.** Made explicit (parallel to the behavior-gap rule) that a component/variant/token a UI slice needs but the design system lacks is a `GAP … — design-system — UNRESOLVED`, resolved by extending the design system (which propagates) — not hand-styled in code. Already enforced by the conventions fitness rule; now stated so it's discoverable upfront, not caught after the fact.

## 3.1.6

### Changed — `grill-design-system`: explicit base-vs-refinement, and the spec is a thin contract over the asset (not a copy)
For the workflow of *importing a design export* (e.g. from a design tool) and refining it:
- **Method "provided" mode now states the base+refine split explicitly:** the export is the **base** — it lands in the non-spec `design-system/` zone (lifted as-is or normalised to DTCG), kept authoritative where given, and is the asset **code consumes**; grilling (verify + gap-fill) happens **on top of it**.
- **New rule resolving the "doesn't the spec conflict with the export we code against?" tension:** the **asset is the source of truth code consumes; `design-system.md` is a thin contract *over* it, never a copy.** The spec holds only the `DS-` id catalog + variant/state/ARIA contracts + a11y verification + a `provided|generated` mark, and **points at** the asset — it must not re-list the raw tokens/components in prose (that duplicates the asset and drifts). The `DS-` ids are the spec-referenceable glue (a ux journey cites `DS-Card`; a task builds against `DS-Button`) that resolves to the asset substrate; on an asset change you **re-verify**, so the two can't disagree. (`provided|generated` is a *source-authority* mark, not edit history.)

## 3.1.5

### Fixed
- **Four foundation skills were missing their `Consumes:` line.** `grill-product-vision`, `grill-customer-discovery`, `grill-market`, and `grill-goals` each have a declared input in `dependencies.json` (`problem-validation` / `product-vision`) but stated none in their SKILL.md, unlike every peer. Added the line to each (start-here primary input). Verified: every skill with a manifest input now declares it; the two true roots (`grill-problem-validation`, `grill-constraints`) correctly have none. (Did *not* chase verbatim sync between the SKILL prose, `dependencies.json`, and the dependency table — `consumes` is advisory and the reference graph is the propagation truth, so forcing three-way alignment would be false precision and perpetual maintenance.)

## 3.1.4

### Changed — broad-upstream context is for synthesis; construction (coding) is scoped
A research pass (software-engineering practice, LLM long-context behaviour, cognitive-load theory) showed the 3.1.0 "consider every upstream layer" rule was right for **synthesis** tasks but wrong for **construction**:
- **Synthesis** (architecture, test-strategy, task-decomposition, the grilling/derivation areas) genuinely integrates many upstream concerns (Bass/Clements/Kazman ADD inputs; Rozanski & Woods; all-requirement traceability). The broad-context rule stays for these.
- **Construction** (`implement-task` coding slices) needs a **scoped** input — its acceptance criteria + the domain elements it realises + the boundary contracts/schema + the architecture boundaries it must respect + conventions — **not** the whole spec. Evidence: vertical-slicing / "just barely good enough" practice (market/GTM/business-model is Lean over-processing waste to an implementer); LLM long-context degradation ("Lost in the Middle", Liu TACL 2024; context rot, Chroma 2025; topically-adjacent distractors are the most harmful — Cuconasu SIGIR 2024, Shi ICML 2023); cognitive load (Team Topologies, Sweller).
- The nuance the research flagged: *drawing* a slice's edges is itself a synthesis act, so "scoped" applies to **executing** a slice, not to deciding it — the task-breakdown stays broad.

Corrected the over-strong 3.1.0 `exec-engine` framing ("every upstream layer is available context") to **scoped-to-the-task + pull-on-demand**, and clarified in the conductor and `repo-layout.md` that the broad-context rule is for synthesis areas, not the execution loop. (The grill/derive engine rules are unchanged — broad context is correct there.)

## 3.1.3

### Fixed — the upstream-only invariant is now enforced over ALL id tokens, not just marked references
- **A downward id in plain prose is now flagged.** The illegal-downward-reference check ran only inside `note_ref`, which is reached only by the reference-detector (after a refmark word / arrow). So a downward id with no marker — `ENTL-217` cited as a phasing/gating note in an L1 `glossary.md`, an L0 discovery bet naming `NFR-030` — evaded the check entirely: neither undefined- nor downward-checked. The check is now a **comprehensive pass over every `ID-` token** in a file (mirroring the duplicate/owning-dir checks), so the invariant holds regardless of position.
- **High precision, not a heuristic:** a definition or same-layer mention has `id_layer == file_layer` (never `>`), so it never fires — every hit is a real downward occurrence. Deduped per (file, id).
- **Exemptions** mirror the existing reference rules: ADR source files (cite drivers downward by design), `traceability.md` (the cross-layer trace spine), the spec-root orchestration dashboards (`_readiness.md`/`_human-input.md`, which span all layers), and the JIT impl area (`07-solution/impl/` — `derive-impl-design` names the task it elaborates, the one acknowledged layer wrinkle). Fenced code + the scope header are skipped; an id whose area is absent (partial spec) is suppressed like the undefined check.

This is distinct from the rejected "type-aware coverage" idea: a downward reference is an *unambiguous* violation of a core invariant (not a maybe-gap), so enforcing it everywhere catches real violations rather than manufacturing false positives.

## 3.1.2

### Fixed — read-models now have a structural-coverage backstop
- **An orphaned domain read-model (`RM-`) that no use-case projects is now flagged.** `COV_HINT`/`DOWN_TYPE` covered the command side (`CMD-`/`EVT- → UC-`) but omitted `RM-` entirely, so a user-facing read-model with no view use-case passed lint silently (an under-projected functional spec). Added `RM → UC` coverage (WARN, with an N/A escape for internal projections; the existing "downstream layer empty → suppress" guard still applies, so it's silent until use-cases exist).
- **Added a `derive-functional` method/rule for the *query* side:** project a **view use-case** per user-facing read-model (not just a command use-case per command/flow); a read surface no use-case surfaces is an under-projected spec, or explicitly `N/A` for an internal projection.
- **Added `surfaces` / `renders` / `displays` to the reference markers** (`REFMARK`) — the natural verbs a view use-case uses to reference its read-model. Without this the new `RM-` coverage would have false-WARNed on legitimately-surfaced read-models (caught in testing).

Deliberately **not** done: the report's suggested "type-aware coverage" (an `X→Y` edge satisfied only by a `Y`-type reference). It would change coverage semantics for *every* type and surface a wave of new WARNs (e.g. a `CMD-` referenced by a `SEC-` rule but not yet a `UC-`) — the exact false-coverage-WARN churn removed across 1.3.2 / 1.4.2 / 2.0.1. The under-projection it targets is better guarded by the method rule above than by a noisy mechanical check.

## 3.1.1

### Fixed
- **`derive-architecture` no longer names its sibling skills.** The 3.1.0 cross-cutting-concerns note referenced "the specialised `*-architecture` skills," which broke skill independence (a worker skill must reference upstream/downstream *artifacts*, never other skills — only the conductor knows the orchestration). Reworded to state the skill's own scope self-containedly: the core pass commits the architecturally-significant cross-cutting *strategy* (data topology · trust model · ML data-dependencies), and finer per-concern detail is simply "out of this artifact's scope" — naming no one. (The specialised architecture areas remain separate skills that consume *the architecture artifact*, not the skill; merging them was considered and rejected — it would produce one unfocused mega-skill and break standalone usability for no gain.)

## 3.1.0

### Changed — dependencies are ORDER + availability, not a fixed edge-list
A research pass (DDD, software-architecture, requirements-engineering, design-systems, ML-systems literature) showed the per-area `consumes` edges are individually contested and error-prone — so the system stops relying on getting them "right":

- **Every skill now considers all upstream layers, not just its named inputs.** Added to all three shared engines (`grill`/`derive`/`exec`): everything in earlier layers (+ any same-stage output whose derive-order is fixed before it) is **available context**; the listed inputs are the **advisory "start-here" primary** sources, not an exhaustive or gating set. Skills are told to **cite the IDs they actually use**, because change-propagation comes from the real reference graph, not a declared list.
- **The conductor now hands a skill all upstream artifacts** (with `consumes` flagged as "start here"), instead of "exactly" the declared edges.
- **`dependencies.json` `consumes` is reframed as advisory** (a `_comment` documents it); the authoritative "what depends on what" is `tools/impact.py` walking the actual stable-ID references. `repo-layout.md` documents the model: **order is authoritative, the edge-list isn't.**

### Fixed — three research-backed dependency corrections
- **Removed `quality → functional`** — Bass/Clements/Kazman: *functionality and quality attributes are orthogonal*; a quality-attribute scenario's artifact is the **system / an architectural element, never a use-case**. (Reverts an over-eager edit; a measurable instance may still bind to a domain operation for test traceability — that's a view, not a dependency.)
- **Added `derive-architecture → ddd`** — the bounded contexts drive the service/module decomposition; the domain is a primary architecture input (Evans/Vernon/Newman/Richardson), not transitive-via-functional. Plus a skill note to **co-design irreversible cross-cutting concerns (security trust boundaries, data topology, ML data-dependencies) in the core architecture pass** — they're one-way doors, not safe to defer to the specialised `*-architecture` skills (OWASP A04, Sculley "CACE").
- **Added `derive-tasks → api-contracts`** (the cross-boundary contract a slice builds against — walking-skeleton / API-first); the detailed data **schema** is explicitly *not* a task input (emergent during implementation, not BDUF).

Deliberately **not** added as hard edges (the new all-upstream model + the reference graph cover them, and the sources favour routing regulation through a single obligations hub rather than per-area constraint edges): `ml-reqs → ddd/constraints`, `data-reqs/security-reqs → constraints`. `ux → design-system` kept (a soft pattern-reference, now advisory).

## 3.0.0

### Changed — BREAKING: stage numbers now track the dependency chain; requirements vs. derived spec separated; commercial split to post-launch
The spec tree is renumbered so **stage numbers follow the dependency order**, and the grilled/derived boundary and the build-vs-business boundary are made structural:

- **`05-req-functional/` → `05-functional-spec/`** — it's a *derived spec* (UC/AC projected from the domain), not a "requirement." "Requirement" now means **grilled, human-input** areas only.
- **`05-req-nonfunctional/<area>/` → `06-requirements/<area>/`** — "non-functional" retired. Functional-spec (`05`) sits *before* requirements (`06`) because `quality`, `ux`, `ml`, and `entitlements` consume it (a quality ASR is keyed to a `UC-` flow) — the order is forced, not cosmetic.
- **New area `06-requirements/entitlements/`** (`grill-entitlements`, prefix `ENTL-`) — the **access-tier / feature-gating** model, split out of monetization. It's the architecturally-relevant slice (architecture now consumes `entitlements`, not `monetization`); tiers are defined by capability, referencing `UC-` features upstream.
- **`monetization` re-scoped to pricing only** — it now *prices* the `ENTL-` tiers (model · pricing · plans · unit-economics); the entitlement model moved to its own area.
- **The go-to-market *motion*** (PLG vs sales-led) is owned by `product-vision` (`motion.md`); `go-to-market` is now launch/channels/partnerships only. `security`/`ux`/`monetization` consume the motion from vision.
- **Commercial cluster moved to post-launch**: `06-commercial`/`07-gtm`/`08-growth` → **`09-commercial/{monetization, go-to-market, growth}`** — three pure sinks (nothing upstream depends on them; verified against the dependency graph). The pre-arch "stage 2½ / parallel gtm-growth" is gone.
- **Solution/delivery renumbered**: `09-solution/` → **`07-solution/`**, `10-delivery/` → **`08-delivery/`**, and `10-delivery/operations/` → **`10-operate/`** (its own stage).
- **Within-stage order stays a graph, not numbers**: `repo-layout.md` now renders the requirements **tier diagram** (parallel siblings) rather than fabricating sequence via sub-numbers; the conductor reads `dependencies.json` for the true partial order.
- **New `method` field on every area in `dependencies.json`** (`grill`/`derive`/`exec` = the skill family) so the manifest stops conflating it with `kind` (the data-flow posture) — the grilled requirement areas no longer read as "derive."

Updated across `lint_spec.py` (`LEAF_DIRS`, `AREA_DIR`, `PREFIX_OWNER`, `TYPES`+`ENTL`, `ID_LAYER`, `file_layer`, gate/adjective scopes), `guard_derived.py`, `impact.py`, `gen_docsite.py`, `gen_depgraph.py`, `dependencies.json`, `repo-layout.md`, the conductor stage map, and the re-scoped skills (`grill-monetization`, `grill-quality`; new `grill-entitlements`). `product-vision`/`go-to-market` already scoped the motion correctly.

- **Migration for an existing spec** (paths only — IDs, content, and references are unaffected; the linter now **rejects** the old paths):
  - `spec/05-req-functional/*` → `spec/05-functional-spec/`
  - `spec/05-req-nonfunctional/<area>/` → `spec/06-requirements/<area>/`
  - `spec/06-commercial/*` → `spec/09-commercial/monetization/` · `spec/07-gtm/*` → `spec/09-commercial/go-to-market/` · `spec/08-growth/*` → `spec/09-commercial/growth/`
  - `spec/09-solution/` → `spec/07-solution/` · `spec/10-delivery/` → `spec/08-delivery/` · `spec/10-delivery/operations/` → `spec/10-operate/`
  - new: split any plan→feature *entitlement* content out of monetization into `spec/06-requirements/entitlements/` (`ENTL-` ids); the GTM *motion* belongs in `02-product/vision/motion.md`.

## 2.0.1

### Fixed
- **The linter is now robust to an intentionally-partial spec** (derived/downstream areas deleted to review the grilled core). A reference whose **owning area is entirely absent** (no files present) is an artifact of that missing area, not a real dangling/illegal reference — so `undefined ID` and `illegal downward reference` are now **suppressed** for those tokens, mirroring the existing coverage-WARN "downstream layer empty" suppression. The set of absent areas is computed from the present file set (`ABSENT_TYPES`), and the suppression is surfaced once as an INFO (`N reference(s) to areas not present … were not error-checked`) so it's never silent. A typo *inside a present area* still errors (its directory has files); a **full** spec has no absent areas, so its behaviour is unchanged.
- Note on the report: diffing the linter across the cited versions shows **no change to the structure / area / owning-area / layer error logic** in that range (only the range-shorthand strip and the advisory INFO checks were added), and a clean grilled-core reproduces to **0 errors** here — so the reported "file outside structure" / "defined outside owning area" floods could not be reproduced and don't originate in that logic. The fix targets the one reproducible gap: cross-area references into absent areas. If those structural errors persist on a real spec, they're most likely a path-layout mismatch (e.g. an old-layout spec linted by a 2.0.0 build) — share the error sample and the spec tree and it can be pinned exactly.

## 2.0.0

### Changed — BREAKING: requirements split into two stage-5 folders
- **`05-requirements/` is replaced by `05-req-functional/` + `05-req-nonfunctional/`** so the grill/derive boundary is visible in the tree itself: `05-req-functional/` is the one **derived** requirements area (use-cases + acceptance, projected from the domain model), and `05-req-nonfunctional/` holds the **elicited** areas (quality, data, integration, security, ux, design-system, compliance, ml). Both keep the `05-` stage number — nothing downstream renumbers. This makes "how far does my input go" legible at a glance: everything authored is grilled *except* `05-req-functional/`. Updated across `lint_spec.py` (`LEAF_DIRS`, `AREA_DIR`, `PREFIX_OWNER`, `file_layer`, the readiness-gate check, the adjective-scope check), `guard_derived.py`, `impact.py`, `gen_docsite.py`, `dependencies.json`, `repo-layout.md`, the conductor stage map, and the prototype/operator references. Skills are unchanged (no renames).
- **Migration for an existing spec:** move `spec/05-requirements/functional/*` → `spec/05-req-functional/` and each `spec/05-requirements/<area>/` → `spec/05-req-nonfunctional/<area>/` (quality · data · integration · security · ux · design-system · compliance · ml). IDs, content, and references are unaffected — only the paths move. The linter now **rejects** the old `05-requirements/` paths as outside the structure, so this relocation is required when upgrading.

## 1.4.9

### Fixed
- **A modification updates existing text in place, instead of dropping a separate paragraph beside it.** Even when an addition was placed in the right area (not the end), a change that *modified* an already-stated fact was sometimes added as an extra adjacent paragraph/note — leaving the original plus an addendum where there should be one updated statement. The structural rule (1.4.6) only covered parallel *sections*; it's now pushed down to every granularity in `grill-engine` and `derive-engine`: when a change modifies an existing statement, **rewrite that sentence, field, or row in place** so it reads as the single current truth — never leave the original and append a qualifier beside it (an `"X. (Update: now Y)"` or a second paragraph restating X). Only genuinely new information becomes new content; a modification edits what's there. The conductor's consistency sweep now also flags a separate paragraph/note/row left beside content a change should have updated in place.

## 1.4.8

### Fixed
- **Made explicit that an addition's place is wherever it belongs — not the end by default.** 1.4.6 already said "integrate each change where it belongs" and "never bolt additions onto the end," but the *not-always-at-the-end* point was only implied. Now stated outright in `grill-engine` and `derive-engine`: an addition's place is wherever it belongs in the structure (frequently mid-document — beside its related content, in the right table, under the right heading), and the order in which things were added never determines position.

## 1.4.7

### Fixed
- **Emphasis no longer marks "this is an addition."** Re-runs were sometimes bolding new content simply *because* it was new, so additions stood out from original content by their formatting — another way the artifact betrayed its own edit history. Extended the engines' emphasis discipline: **bold/italic follow the document's convention for their meaning** (a defined term, a field label, an ID) and are never used to flag that something is new or changed; a reader can't tell an addition from original content by its formatting. The conductor's consistency sweep now also flags emphasis used to mark an addition. Completes the structural-history work in 1.4.6 (additions integrated, not appended) — together they mean an edited artifact reads, in wording, structure, and formatting alike, as if written from scratch in one pass.

## 1.4.6

### Fixed
- **Changes are now woven into an artifact's structure, not appended.** A re-run that incorporated a change was producing append-only documents — bolting new headings/sections onto the end (e.g. two new sections on a value-object artifact) instead of integrating the change where it belongs and re-organising the rest, leaving a part-sectioned/part-flat result a reader could date. Root cause: the derive-engine re-run rule (*"touch only what the change affects … never regenerate from scratch"*) was written to protect IDs/decisions but was being executed as "append and don't touch existing structure." Reframed across the shared engines: **`minimal delta` governs *semantics* (preserve every stable ID, accepted ADR, decision, and still-true fact — never churn or drop them), not *structure*.** The artifact must read as if the whole document were written from scratch, today, in one pass: integrate each change where it belongs, re-author the affected sections, never bolt additions onto the end, never spawn a parallel section for content that belongs in an existing one, never leave a document half-restructured. This is the structural counterpart to the timeless-wording rule (1.4.3) — same principle (the spec carries no trace of its own history), applied to layout. The conductor's consistency sweep now also flags append-only / incoherent structure an edit left behind, routing it to the owning area. Engine-instruction change; no deterministic lint (structural coherence isn't regex-detectable — it's enforced by the engines and the conductor's semantic pass).

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
