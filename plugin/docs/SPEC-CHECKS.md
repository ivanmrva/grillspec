# What the tools check

A map of every automated check, grouped by what it protects. The tools are the source of truth; this page tells an author what is required and why.

Three severities are used throughout:

| Severity | Meaning |
|---|---|
| ERROR | a violation; the tool exits non-zero, and the pre-commit hook blocks the commit |
| WARN | a likely problem to confirm or dismiss; it does not block |
| INFO | a candidate the tool cannot decide; the conductor or the author judges it |

A check is an ERROR only where it cannot be wrong. Anything that needs a guess is a WARN or an INFO, and anything about meaning is left to the audits (the last section but one).

## `lint_spec.py` — the spec linter

Run from the project root: `python3 tools/lint_spec.py [spec_dir]`. It reads `spec/**.md` and, for the profile, `.grillspec/project.json`. The conductor runs it at the start of every session, and the pre-commit hook runs it on every commit. The numbers below are the ones in the tool's source; 2, 6 and 7 are unassigned.

### Layout

| # | What must hold | Severity |
|---|---|---|
| 1 | every file sits at an allowed path: an area folder, a per-area `glossary.md` or `actors.md`, the shared `adr/` folder, or a spec-root `_*.md` file | ERROR |
| 2b | an ADR file is named `ADR-<AREA>-NNN.md` | ERROR |
| 3 | every file opens with its `scope · excludes · format` header, and no field is empty | ERROR (WARN for a field left as "…") |
| 4 | no placeholder token (`{{ }}`, TODO, FIXME, TKTK, NNNN) outside code spans | ERROR |
| 5 | every local link resolves | ERROR |
| 35 | the only underscore files at the spec root are `_readiness.md`, `_human-input.md` and `_provisioning.md` | WARN |
| 39 | an audit report at the project root is git-ignored | INFO |
| 44 | when the project root has both, `CLAUDE.md` contains exactly `@AGENTS.md` | ERROR |

### Readiness and prose

| # | What must hold | Severity |
|---|---|---|
| 8 | an area marked done in `_readiness.md` has content, and an area with content is not marked not-started | WARN |
| 9 | the solution layer has content only once the in-profile requirement, design-system and UX areas do | WARN |
| 10 | no dense prose block: consecutive lines of more than 40 words, or one line of more than 80 | WARN |

### IDs and references

The layers, upstream to downstream: foundation (discovery, product, constraints, system context) → domain → functional spec and requirements → design system → UX → solution → delivery. ADR files, a `traceability.md` and the spec-root underscore files may cite any layer.

| # | What must hold | Severity |
|---|---|---|
| 11 | every referenced ID is defined | ERROR |
| 11b | no file mentions an ID that belongs to a layer below it | ERROR |
| 11c | the same direction rule for ID shapes the linter does not register, judged by where they are defined | WARN |
| 11d | no file path or link points into a downstream area | WARN |
| 12 | an ID is defined in one file only | ERROR |
| 13 | an ID is defined in the area that owns its type | ERROR |
| 13b | an ID starts with its bare type prefix: `AGG-250`, not `SUR-AGG-250` | ERROR |
| 13c | an ID is the leading cell of its table row, so it registers as a definition | WARN |
| 16 | a child ID carries its parent's number and the parent exists: `AC-014a` belongs to `UC-014`, `ASR-014` to `NFR-014` | ERROR |
| 16b | on its own definition, a `JRN-` or `ML-` names its `UC-` (or `N/A` with a reason) and an `SLO-` names its `NFR-` | ERROR |
| 16c | a design note under `impl-design/` names the `MOD-` it details and the `T-` it serves | WARN |

A reference into an area that has no content yet is not reported as undefined; the linter prints one INFO line listing those references.

### Coverage (check 14)

Each element must be picked up by something downstream. A missing pickup is a WARN, with three exceptions that are ERRORs: a threat with no control, an obligation with no control once the solution layer has content, and an acceptance criterion with no task once tasks exist. A coverage check stays silent while the downstream type does not exist anywhere yet.

| Element | Must be picked up by |
|---|---|
| `CMD-` command | a use-case |
| `EVT-` event | a consumer (a use-case, a policy reaction, the event contract), or a note that it is an audit-only or internal sink |
| `AGG-` aggregate | a `DATA-` element or a use-case |
| `RM-` read model | a use-case that shows it |
| `UC-` use-case | acceptance criteria or a task |
| `AC-` criterion | a task |
| `INV-` invariant | a criterion that asserts it, or a note that it is enforced by construction or a constraint |
| `THR-` threat | a control, or `accepted-risk` |
| `OBL-` obligation | a control |
| `NFR-` · `ASR-` | an `ASR-` or `SLO-`, or a verifying reference |
| `API-` · `DATA-` · `SLO-` | a consumer or a reference |
| `ENTL-` entitlement | a task or a pricing plan |
| `IF-` boundary interface | an integration requirement or a task |
| `CA-` capability area | a use-case |
| `HOT-` hotspot | a task, an ADR or a design note |
| `SCR-` screen | a journey step, a task or a prototype |
| `EXP-` · `AEV-` | a task that wires or emits it |

### Structured facts

| # | What must hold | Severity |
|---|---|---|
| 21 | a state-machine table in the domain model has no unreachable state, no dead end and no ambiguous transition | WARN |
| 22 | every cell of an authorization table holds a decision, and every command has a rule | ERROR |
| 23 | a typed fact stated twice for one ID agrees (retention, residency, class, SLA, limit, quota, price, tier, delivery guarantee, interaction style, ordering, hard/soft, threshold) | WARN |
| 23 | every `DATA-` element declares a class, a retention or a residency | WARN |
| 25 | every `NFR-` names how it is enforced | WARN |
| 26 | every module in the module map declares a role | WARN |

### ADRs

| # | What must hold | Severity |
|---|---|---|
| 17 | no live reference to a superseded or deprecated ADR | WARN |
| 20 | every ADR declares a recognized status | WARN |
| 27 | an area's ADR numbers have no gap | WARN |
| 28 | a resolved decision in `_human-input.md` cites an ADR that exists | WARN |

### Human input, bets, credentials

| # | What must hold | Severity |
|---|---|---|
| 18 | a task marked `afk: blocked` appears in `_human-input.md` | WARN |
| 36 | no value is still marked `unconfirmed` | WARN; ERROR once tasks exist |
| 37 | in `bets.md`, status and criticality use their closed vocabularies | WARN |
| 38 | a credential marked `provisioned` in `_provisioning.md` carries evidence, and every state is `provisioned` or `pending` | WARN |

### Task briefs

| # | What must hold | Severity |
|---|---|---|
| 15 | no `GAP … UNRESOLVED` line | ERROR |
| 19 | the brief cites at least one upstream ID | WARN |
| 19b | an `AC-` is named by one task only | WARN |
| 24 | the `depends` graph has no cycle | ERROR |
| 29 | an `afk: eligible` task's `human-prereq` names credentials that are `provisioned` | WARN |
| 42 | the brief has a `tier` row reading `routine`, `feature` or `critical`, and a `critical` brief has a `review` row | WARN |
| 43 | each criterion in `behavior` carries its text, not only its ID | WARN |

For a UI slice:

| # | What must hold | Severity |
|---|---|---|
| 30 | an `afk: eligible` task with a `ux` cell has a `prototype-review` cell reading `frozen`, `reviewed` or `waived` | ERROR |
| 31 | the `ux` cell cites its `JRN-`, and lists the states the slice realises (`states: empty · loading · …`) | ERROR for the journey; WARN for the states |
| 32 | a task with a `ux` cell has an `a11y` cell, and that cell names a keyboard or focus path or a WCAG criterion | ERROR if absent; WARN if empty of content |
| 33 | a `ux: N/A — reuses DS-…` claim names the `SCR-` it edits | WARN |
| 34 | a task whose `touches` names a UI surface has a `ux` cell | WARN |

### Lean and timeless

| # | What must hold | Severity |
|---|---|---|
| 40 | no edit-trace stamp: a status or process word beside an ISO date, such as "ratified 2026-07-26" | ERROR |
| 40 | no other ISO date in prose, and no edit-history wording ("previously", "no longer", "renamed from", "newly added", "this round", "as discussed") | WARN |
| 41 | no content in an area outside the project's profile | WARN |
| 41 | below `regulated`, no full-mode solution file (a schema, an OpenAPI or AsyncAPI file, a control register, telemetry or runbook documents, and their siblings) | WARN |

Check 40 skips `12-operate/` (operations records are dated by nature), `_provisioning.md`, code spans and fences. A line that states a real domain date or uses one of the phrases as domain language carries `<!-- timeless: allow <why> -->`. Check 41 runs only when `.grillspec/project.json` sets a profile, and never flags the optional areas (market, customer discovery, monetization, go-to-market, growth).

### Advisory

| # | What it flags | Severity |
|---|---|---|
| 14b | development-trace wording · a skill or tool name inside project documentation · an ID with a context prefix in front of its type | INFO |
| 14c | a quality adjective ("fast", "scalable") on a requirement line that carries no number | INFO |

## `check_contracts.py` — contracts against the ID graph

Applies where `spec/09-solution/api/` holds an OpenAPI or AsyncAPI file. Needs PyYAML; it exits cleanly without it or without contracts.

| What must hold | Severity |
|---|---|
| every ID a contract references (`x-grillspec-id`, `x-serves`, `SEC-` scopes, `x-data`, channel ids) is defined in `spec/**.md` | ERROR |
| every REST operation carries `x-grillspec-id` and `x-serves`, a security scope on a mutation, and an error response | WARN |

`spectral-grillspec.yaml` is the companion ruleset for contract structure and style, run with Spectral: `npx @stoplight/spectral-cli lint spec/09-solution/api/openapi.yaml --ruleset tools/spectral-grillspec.yaml`. It extends `spectral:oas` and adds the house rules: the two traceability extensions, RFC 9457 `application/problem+json` errors, and a security scope per mutation.

## `check_task.py` — is a task that claims done really done?

Nothing about a task's progress is stored except the `status` row of its brief. This tool computes the rest from the tree.

| Call | Prints |
|---|---|
| `check_task.py [spec_dir]` | one row per task: tier, phase, status, criteria covered, UI states covered, review, open items. It then checks every task whose status is `done` |
| `--task T-014` | the same check for one task, as if it claimed done |
| `--json` | the status rows as JSON |
| `--trace` | criterion → task → the test files that cover it |

A done-claim fails when:

- a criterion in the brief has no `@covers AC-…` tag in a test file that declares a runnable test;
- a UI state named in the `ux` cell has no `@state:<name>` tag in such a file;
- a `GAP … UNRESOLVED` line remains in the brief;
- a task it depends on is not done;
- a `critical` task has no `review | PASS` row (the reviewer writes it, not the implementer);
- a design-first task's design note is missing.

Whether the tests pass, and the coverage and mutation bars, belong to the project's own gate. The tool does not read numbers anyone typed.

## The pre-commit hook

`spec_governance_hook.sh` is installed into the project as its git pre-commit hook. It runs only in that repository, and does nothing where there is no `spec/` or the tools are not vendored under `.grillspec/tools/`. It runs four steps and stops at the first failure:

1. `lint_spec.py` — blocks on an ERROR.
2. `check_contracts.py` — blocks when a contract references an undefined ID.
3. `check_task.py` — blocks when a task is marked done and the tree does not back it. A task in progress never blocks.
4. `check_orphan_tests.py` — blocks when a test has no spec driver.

Override in an emergency with `git commit --no-verify`.

## The edit hook

`gate_exec.py --hook` runs before each file edit in Claude Code and Codex. It has one job: deny an edit that introduces

- a skip, expected-failure or `.only` marker in a test file, or
- a mocking-library import or a `Fake*`/`Stub*`/`Mock*`/`Dummy*` definition in the production tree.

It looks only at the lines the edit adds, keeps no state, and knows nothing about tasks. A line carrying `no-skips: allow <reason>` or `no-fakes: allow <reason>` passes. The production tree is `src/` unless `.grillspec/grillspec-gate.json` lists other `production_globs`. If the hook itself fails it allows the edit, and `GRILLSPEC_GATE_OFF=1` turns it off.

`install_exec_gates.py` copies the hook, `check_task.py`, `check_orphan_tests.py` and their shared helper into `.grillspec/tools/` and adds one PreToolUse entry to `.claude/settings.json` and `.codex/hooks.json` (`--host claude` or `--host codex` for one side only).

## The code-facing checkers

Each takes the project root as its first argument and exits cleanly when it has nothing to scan. `--strict`, where a tool has WARNs, turns them into ERRORs; a release audit uses it.

| Tool | ERROR | WARN |
|---|---|---|
| `check_no_fakes.py` | a test double defined in production source, or a mocking library imported there | a placeholder identifier, an unimplemented body, a fallback for an unconfigured dependency |
| `check_no_skips.py` | a skipped, expected-to-fail or focused test; a CI or build step that swallows a test failure | a declared-but-unwritten test, `continue-on-error` on a CI step, `--passWithNoTests` |
| `check_orphan_tests.py` | a test file with no `@covers` or `@state:` tag; a `@covers` ID that is not in the spec; a file in a test tree that declares tests but is not named like a test | — |
| `check_mock_budget.py` | module-level mocking in a tier whose ceiling is `none`; a real dependency mocked in a `boundary-only` tier | — |
| `check_test_tiers.py` | with `--require-all-tiers`, a declared tier with no suite; with `--require`, tests but no tier contract | a declared tier with no suite yet; tests in a tier the contract does not declare |
| `check_e2e_target.py` | a test in a deployed-environment tier that points at localhost, docker-compose or testcontainers | — |
| `check_config_drift.py` | an environment variable the code reads that `environments.md` does not declare | a declared key no code reads |
| `check_deploy_real.py` | a placeholder, a disabled deploy step or an echo-only script in a deploy artifact | a deploy artifact that runs no recognized deploy command |
| `check_migration_real.py` | a placeholder or an explicitly empty migration | a migration with no statement |

The three tier checkers read the tier-contract table in `spec/09-solution/test/levels.md`, and `check_config_drift.py` reads `spec/09-solution/infra-ops/environments.md`; a project without those files (the `lite` profile) gets no findings from them. `check_test_tiers.py` also prints the number of test files per tier.

Every finding can be waived where it is legitimate: an inline comment `<name>: allow <reason>` on the line, or an entry in `.grillspec/<name>-allow.txt`, where `<name>` is `no-fakes`, `no-skips`, `no-orphans`, `mock-budget`, `e2e-target`, `config-drift`, `deploy-real` or `migration-real`. Two tools can be taught project specifics: `.grillspec/deploy-real-commands.txt` names extra deploy commands, and `.grillspec/migration-real-dirs.txt` extra migration folders.

The test-facing tools look under `tests`, `test`, `src`, `app`, `apps`, `lib`, `libs`, `packages` and `e2e`. A project that roots its code elsewhere sets `GRILLSPEC_TEST_ROOTS` (comma-separated directory names) once, or passes `--tests` per call. `check_no_fakes.py` and `check_config_drift.py` scan `src` unless given `--src`.

## What no check decides

Three skills cover what needs judgment:

| Skill | Judges |
|---|---|
| `audit-spec` | the spec: contradictions in prose, an ID of the wrong type, scope, whether a control really mitigates its threat, content with no reader, a whole branch of the domain nobody modelled |
| `conformance-review` | one `critical` task's code against its brief, by a reviewer that did not write it |
| `audit-build` | the whole build before a release: whether tagged tests really assert their criteria, whether later work weakened earlier guarantees, waivers, lowered bars |

## Keeping the checks honest

Every check has a regression suite beside it in `tools/`: a fixture that must fire and a clean one that must not. `test_lint_spec.py` covers the linter and `check_contracts.py`; `test_check_task.py`, `test_gate_exec.py`, `test_project_state.py` and one `test_check_*.py` per code-facing checker cover the rest; `test_e2e_gates.py` shows the checkers composing on one realistic project, where a clean task passes and each cheat trips the check that owns it.

`selfcheck.py` guards the plugin source itself. Among other things it keeps the ID-prefix vocabulary identical across `lint_spec.py`, `check_contracts.py`, `impact.py`, `spec_status.py` and `check_task.py`, the reference keywords and layer table identical between the linter and `impact.py`, and the profile names identical between the linter and `project_config.py`. `.github/workflows/plugin-check.yml` runs it with the regression suites on every push and pull request.
