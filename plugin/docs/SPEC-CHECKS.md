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
| **Structural coverage** (gap surface) | every `CMD-`→`UC-`→`AC-`→`T-` · `EVT-` has a consumer · `OBL-`→control · **`THR-`→`SEC-`** · `NFR-`→`ASR-`/`SLO-` · `API-`→consumer | WARN |
| **State machines** (ddd) | a `from·trigger·to·guard` table has no **unreachable** state, no **dead-end** (non-terminal with no exit), no **nondeterministic** transition (same from+trigger, no guard) | WARN |
| **Authorization** | every command has a rule (default-deny) · no blank decision cell — in either the command×actor matrix or the `SEC-` long-form | WARN |
| **Typed scalar facts** | a `retention`/`residency`/`class`/`SLA`/`price` stated twice must **agree** · every `DATA-` carries class/retention/residency (a value or `deferred until …`) | WARN |
| **Tasks & build** | no `T-` ships with an `UNRESOLVED` gap (ERROR) · the `depends-on` graph is a **DAG** — no cycle (ERROR) · every `T-` cites ≥1 upstream spec ID (WARN) · every `afk:blocked` task is queued in `_human-input.md` (WARN) | ERROR / WARN |
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

Distinct from these spec-structure tools, a second set governs that **generated code is built as the spec demands** (documented in `HOW-IT-WORKS.md`): `check_task_record.py` (the per-task Verification Record — every obligation evidenced and **every standard gate row carried**, incl. `deploy` + `tests:layers`, independent verdict on disk, tests-first via `@covers` tags), `check_no_fakes.py` (no test doubles in `src/`), `check_deploy_real.py` (no faked/skipped deploy in the CI/deploy artifacts — GitHub/GitLab/Circle/Azure/Bitbucket/Drone/Cloud-Build/Jenkins configs, shell scripts, Dockerfiles, and `package.json`/`Makefile` deploy targets), `check_migration_real.py` (no faked/empty schema migration), and `check_config_drift.py` (code-read env vars ⊆ the declared `environments.md` matrix). They run in the code pre-commit + `code-ci.yml`, not the spec governance pipeline.

## Keeping the checks honest

Every check carries a regression suite — each check has a fixture that must fire and a clean fixture that must
not: `tools/test_lint_spec.py` (spec tools), and `test_check_task_record.py` · `test_check_no_fakes.py` ·
`test_check_deploy_real.py` · `test_check_migration_real.py` · `test_check_config_drift.py` for the accountability
tools, plus `test_e2e_gates.py` which proves the five compose on one realistic project (a clean task passes all
five; each cheat trips exactly the gate that owns it).
`selfcheck.py` keeps the `TYPES` prefix vocabulary in sync across `lint_spec.py`, `check_contracts.py`,
`impact.py`, `spec_status.py`, `check_freshness.py`, and `check_task_record.py`, and against what the skills
declare. All run in CI (`.github/workflows/plugin-check.yml`).
