# What the spec tools enforce

A reader's map of every automated check over a grillspec `spec/`. The **tools are the source of truth**
(`lint_spec.py`, `check_contracts.py`, `spectral-grillspec.yaml`); this groups them by intent so an author
knows what's required and why. Severities: **ERROR** blocks a commit (the governance pre-commit hook),
**WARN** is an advisory candidate, **INFO** is a heuristic the conductor/author judges.

The dividing line everywhere: a check is **ERROR only when it is sound** (no false positives possible);
anything that needs a guess is **WARN/INFO**, and anything about *meaning* is left to the `audit-spec`
judgment skill, not a check.

## `lint_spec.py` — runs every session and on commit (stdlib, over `spec/**.md`)

| Group | Enforces | Severity |
|---|---|---|
| **Structure & closed world** | files only at allowed paths · every file has a `scope/excludes/format` header · no placeholder/stale tokens · no dangling local links · ADR filename `ADR-<AREA>-NNN.md` | ERROR |
| **Stable-ID spine** | every referenced ID resolves · defined exactly once · defined only in its owning area (stage purity) · bare type-prefix only (no `<CTX>-AGG-1`) · **references are upstream-only** (no layer points down) | ERROR |
| **Child→parent keying** | every `AC-` keys to a real `UC-`; every `ASR-` to a real `NFR-` | ERROR |
| **Derived→driver backref** | a derived id cites its driver, co-located on its own definition row/block: `JRN-`→`UC-` (or `N/A — why`), `SLO-`→`NFR-` (strict — an SLO operationalises an NFR by definition), `ML-`→`UC-` (or `N/A — why`); an impl-design `<module>.md` names its `MOD-` + `T-` | ERROR (impl-design WARN) |
| **Structural coverage** (gap surface) | every `CMD-`→`UC-`→`AC-`→`T-` · `EVT-` has a consumer · `OBL-`→control · **`THR-`→`SEC-`** · **`INV-`→`AC-`** (an invariant is asserted by an AC, or enforced structurally — by construction / a `DATA-` constraint) · `NFR-`→`ASR-`/`SLO-` · `API-`→consumer · **`ENTL-`→a task's security dimension** (an unreferenced entitlement gate ships untested) · **`IF-`→an integration-reqs seam/task** (a boundary whose qualities were never elicited) · **`CA-`→`UC-`** (declared scope that never landed) · **`HOT-`→an owner** (a flagged risk left unaddressed) · **`SCR-`→a journey/task/prototype** (dead information architecture) · **`AEV-`→a task's obs cell** (a defined analytics event nothing instruments) | WARN |
| **State machines** (ddd) | a `from·trigger·to·guard` table has no **unreachable** state, no **dead-end** (non-terminal with no exit), no **nondeterministic** transition (same from+trigger, no guard) | WARN |
| **Authorization** | every command has a rule (default-deny) · no blank decision cell — in either the command×actor matrix or the `SEC-` long-form | WARN |
| **Typed scalar facts** | a `retention`/`residency`/`class`/`SLA`/`price` stated twice must **agree** · every `DATA-` carries class/retention/residency (a value or `deferred until …`) | WARN |
| **Tasks & build** | no `T-` ships with an `UNRESOLVED` gap (ERROR) · the `depends-on` graph is a **DAG** — no cycle (ERROR) · every `T-` cites ≥1 upstream spec ID (WARN) · **every in-scope `AC-` is owned by exactly one `T-`** (the AC is the unit of acceptance — one Verification Record + `@covers` test; WARN) · every `afk:blocked` task is queued in `_human-input.md` (WARN) · an `afk: eligible` task must be **backed**: no un-provisioned `human-prereq` (WARN — verified against the `_provisioning.md` register) and, for a non-`N/A` `ux`, a **review-cleared prototype** (`frozen`/`reviewed`/`waived`; ERROR) | ERROR / WARN |
| **The ux-cell contract** | a non-`N/A` `ux` cell cites its `JRN-` journey by id (ERROR — the record's ux obligation row is generated from it) and names the interaction states the slice realises in list form (`states: empty · loading · …`; WARN) · a slice with a non-`N/A` `ux` may not leave `a11y` N/A or absent (ERROR) and its `a11y` cell must pin something checkable — a keyboard/focus path or WCAG SC (WARN) · a `ux: N/A — reuses DS-…` claim anchors to the `SCR-` screen it edits (WARN — the reuse escape stays auditable) · a `placement` naming a UI surface (ui/frontend/screen/page/component/.tsx…) while `ux` is N/A/absent is a suspected mis-classified UI slice (WARN) | ERROR / WARN |
| **NFR / module** | every `NFR-` names an `enforced-by` mechanism (test/gate/lint/infra/SLO/review) · every module in the architecture map declares a `role:` | WARN |
| **ADR hygiene** | every ADR declares a recognized `status:` · no live reference to a superseded/deprecated ADR | WARN |
| **House style (advisory)** | no development-trace language (`new`/`previously`/`this round`) · no skill/tool-name leak into project docs · no unquantified quality adjective without a bar · ID in a non-leading table cell | INFO |

## `check_contracts.py` — the API/event contracts ↔ spec ID graph (PyYAML; on commit when `api/` exists)

| Enforces | Severity |
|---|---|
| every grillspec id a contract **references** (`x-serves`, `SEC-` scopes, `x-data`, channel ids) resolves to a real definition in `spec/**.md` | ERROR |
| every REST operation carries `x-grillspec-id: API-`, `x-serves: [UC-/CMD-]`, a `security` scope on mutations, and a 4xx/5xx/default error response | WARN |

## `spectral-grillspec.yaml` — contract structure & style (Spectral, in `code-ci.yml`)

`extends: spectral:oas` (well-formedness, responses, `operationId`, `$ref` integrity, unused components) plus
the house rules: `x-grillspec-id`/`x-serves` present, RFC 9457 `application/problem+json` errors, per-mutation
security. Run: `npx @stoplight/spectral-cli lint spec/09-solution/api/*.yaml --ruleset tools/spectral-grillspec.yaml`.

## Not mechanical — the `audit-spec` judgment skill

What no sound check can decide, by design: contradictions stated in prose · an ID conceptually mis-typed within
an allowed prefix · scope adherence · whether a mitigation actually mitigates · **domain completeness** (a whole
branch nobody modelled) · whether the model's *shape* fits the business. These are the `audit-spec` skill's job
(`--depth consistency` for the judgment-but-decidable layer, `--depth full` adds the domain pass).

## Beyond the spec — the build-accountability checks

Distinct from these spec-structure tools, a second set governs that **generated code is built as the spec demands** (documented in `HOW-IT-WORKS.md`): `check_task_record.py` (the per-task Verification Record — every obligation evidenced and **every standard gate row carried**, incl. `deploy` + `tests:layers` + the rendered-surface rows `ux:states`/`a11y`/`ux:rendered` + `obs`, independent verdict on disk, every behavior/tests-cell `AC-` backed by a literal `@covers` tag in a failing-capable test source, the `ux`/`obs` obligations minted from the task's own cells (`JRN-`/`SCR-`/`SLO-`/`EXP-`/`AEV-`), **no false `N/A`** — a gate row can't claim `N/A — headless` while the task's own `ux`/`obs` cell is non-N/A — plus for a UI slice: every ux-cell state backed by a literal `@state:<name>` tag in a failing-capable test source (the state sibling of `@covers`), no pathless `PASS` on the rendered-surface/obs rows, a `prototype-review` row positively reading `frozen`/`reviewed`/`waived`, and every PASS'd `nfr` obligation row citing a measured value against a bar — not "looks good"), `check_no_fakes.py` (no test doubles in `src/`), `check_deploy_real.py` (no faked/skipped deploy in the CI/deploy artifacts — GitHub/GitLab/Circle/Azure/Bitbucket/Drone/Cloud-Build/Jenkins configs, shell scripts, Dockerfiles, and `package.json`/`Makefile` deploy targets), `check_migration_real.py` (no faked/empty schema migration), `check_config_drift.py` (code-read env vars ⊆ the declared `environments.md` matrix), `check_mock_budget.py` (no test that mocks beyond its tier's `mock-ceiling`), `check_test_tiers.py` (every declared tier has a suite; the distribution is reported), `check_e2e_target.py` (no "e2e" that runs on a local stack), and `check_no_skips.py` (no skipped/xfail'd/`.only`-narrowed test, no CI test step that swallows a red). They run in the code pre-commit + `code-ci.yml`, not the spec governance pipeline. A further sibling, `check_operate_records.py`, reconciles the append-only `12-operate/` ledger against the spec it enacted (the layer nothing else covers). These code-side tools are read at aggregate scope by the **`audit-build`** skill — the independent, whole-build attestation that the per-task gates were genuinely run (the code-plane mirror of `audit-spec`). Its verdict has an **opt-in release gate**, `check_release_attestation.py`: a fresh `build-audit-report.md` must read `ATTESTED` before release (make it a required check to enforce; it ships available, not wired-on). One sibling runs **earlier still** — `gate_exec.py`, the project-local PreToolUse exec-gate, enforces the per-task build *order* at **tool-call time** (a `src/**` edit is blocked until a failing test was recorded for the active task; a `status: done` flip is blocked until `check_task_record.py` passes; an edit that introduces a skip/xfail/`.only` into a test or a mock-import/`Fake*` double into `src/` is denied at the keystroke, task-independent — so it also covers setup work before any task branch) — the one thing a commit-time check structurally can't see. The exec engine arms it at session entry (step zero, idempotent), so it is live from the first line ever written, not from when governance lands.

## Keeping the checks honest

Every check carries a regression suite — each check has a fixture that must fire and a clean fixture that must
not: `tools/test_lint_spec.py` (spec tools), and `test_check_task_record.py` · `test_check_no_fakes.py` ·
`test_check_deploy_real.py` · `test_check_migration_real.py` · `test_check_config_drift.py` ·
`test_check_mock_budget.py` · `test_check_test_tiers.py` · `test_check_e2e_target.py` · `test_check_no_skips.py` ·
`test_check_operate_records.py` · `test_check_release_attestation.py` for the accountability tools, plus `test_e2e_gates.py` which proves the
core accountability gates compose on one realistic project (a clean task passes; each cheat trips exactly
the gate that owns it).
`selfcheck.py` keeps the `TYPES` prefix vocabulary in sync across `lint_spec.py`, `check_contracts.py`,
`impact.py`, `spec_status.py`, `check_freshness.py`, and `check_task_record.py`, and against what the skills
declare. All run in CI (`.github/workflows/plugin-check.yml`).
