---
name: derive-conventions
description: >-
  Derive the coding agent's standards and runway from the architecture — style, boundary rules as fitness checks, workflow, build/run/test/lint commands, Definition of Done — and generate matching root AGENTS.md and CLAUDE.md entry points. Use when the architecture exists and you need the coding-agent setup. Loads the shared derive engine.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# derive-conventions

**Load `references/derive-engine.md` first and follow it.** This skill applies that method to **Coding conventions & agent setup** — the instruction set Codex and Claude Code follow to produce code, plus their entry points.

## Method
1. confirm language/framework (from the architecture) → naming/style/error-handling
2. layering & dependency (boundary) rules → test approach
3. engineering workflow (branch-per-task · MR · hooks · CI gates · review)
4. the exact commands → the Definition of Done
5. the CODE pre-commit hooks (incl. a fast SAST pass + a dependency-audit / lockfile-integrity step) + a commit-msg hook validating Conventional Commits + the build-provenance / artifact-signing convention + design-token pipeline governance → generate matching root `AGENTS.md` and `CLAUDE.md`

## Rules
- standards set; dependency/boundary rules explicit and expressed as **enforceable fitness rules**; **no unpinned deps, lockfile committed** is one such rule (audited in-hook)
- frontend/design-system conventions are fitness rules too: semantic/component tokens only (never primitives/raw hex/px), build only design-system components (their variants · sizes · states) per the implementation mapping, copy follows the voice guide; **design-token pipeline governance** — one token source-of-truth · a named transform tool · a token-pair **contrast** a11y check on every semantic foreground/background pairing
- workflow defined (trunk-based · branch per task, no direct commits to main · one MR/PR per task · Conventional Commits enforced by a commit-msg hook) — but the **branching model / git workflow is a ratify-point, not a silent merit pick**: propose trunk-based + branch-per-task as the default and **surface it for the human to confirm or override** (an org may mandate GitFlow, long-lived release branches, a different review-gate / approver count, or a protected-branch policy the spec can't derive). Record the ratified workflow in `workflow.md`; an un-ratified default is an assumption to flag
- **build provenance** — target a stated SLSA build level · artifacts signed · ≥2-person review / branch protection on the release path
- build/test/lint commands runnable; DoD includes 'merged via green CI'
- **CODE governance only** — the pre-commit hooks govern the **code & delivery artifacts** (`src/`+`tests/`, plus the CI/deploy files and schema migrations) (format · lint · type · secret-scan · fast unit · **the no-fakes tripwire (`check_no_fakes.py`)** · **deploy-real + migration-real tripwires** · **the test-tier gates (`check_mock_budget.py` · `check_test_tiers.py` · `check_e2e_target.py`)** · **the no-skips tripwire (`check_no_skips.py`)** · the mechanical conformance subset: boundary/dependency fitness functions + contract checks, on the changed scope). The *spec/docs* are governed by a **separate** spec-governance enforcer (`lint_spec.py` + `guard_derived.py` over `spec/`, + the doc-site); scope the hooks by path even when co-located. The *checks* are not optional; the *release* decision stays the team's
- **one gate, defined once — pre-commit and CI invoke the same target** (a `verify` script / Make target / task runner entry), never two hand-kept lists that drift; the **build loop's done-gate enumeration is the canonical set** that target implements. "Green locally" then means exactly "green in CI" — an agent can't pass a weaker local subset and lean on CI
- **no fakes in production is enforced two ways** — the shipped cross-language tripwire `check_no_fakes.py` (a Fake*/Stub*/Mock*/Dummy* definition or a mocking-library import under `src/` is an ERROR; an `unconfigured→fallback`/placeholder body is a WARN; `.claude/no-fakes-allow.txt` waives the rare legit case) **and** a per-language **architecture fitness function** (the import-graph rule — no test double reachable from a production entrypoint) the test strategy derives; the tripwire fires even when the fitness function was never written
- **every behavior test is tagged `@covers AC-NNN`** (a decorator/annotation/comment/name carrying the AC id it drives) — this is a fitness rule: the literal tag lives in a recognizable, runnable test source, so coverage is verified against the tree (by `check_task_record.py`), not an incidental AC mention or a hand-authored matrix that could claim a test that doesn't exist
- **config drift is gated** — `check_config_drift.py` reconciles the env vars the **code reads** against the **declared** `infra-ops/environments.md` matrix; a key the code reads but the matrix doesn't declare is an ERROR (the operator can't provision it → first-run outage). Config is read **only** from the environment (never hard-coded, never a checked-in real value); a `.env.example` lists every key with a placeholder, never a secret
- **the deploy + migration surface is gated for fakes too** — `check_deploy_real.py` (a `# TODO`/placeholder in a CI/deploy artifact — GitHub/GitLab/etc. config · shell script · Dockerfile · `package.json`/`Makefile` deploy target — is an ERROR; a disabled or command-less deploy is a WARN; `.claude/deploy-real-allow.txt` waives) and `check_migration_real.py` (a placeholder/empty/DDL-less migration; `.claude/migration-real-allow.txt` waives) extend the production-only bar to the deploy scripts/CI/IaC and the schema migrations — the same no-fakes discipline `check_no_fakes.py` brings to `src/`. The authoritative deploy proof remains the e2e/smoke against the real deployed env; these are the cheap static backstop
- **the test suite is gated against the tier contract** — the machine-readable tier contract in `test/levels.md` (per tier: real-deps · may-mock · mock-ceiling · target-env · bars) is enforced mechanically: `check_mock_budget.py` (a mock beyond a tier's ceiling — a double at a `none` tier, or a mocked real dependency at an `boundary-only` integration tier — is an ERROR; `.claude/mock-budget-allow.txt` waives), `check_test_tiers.py` (a declared tier with no suite is a WARN per-commit — the build is incremental, tiers land with their tasks, so a per-commit gate must not go red on a not-yet-due tier — and an ERROR at release under `--require-all-tiers`, which audit-build / the release gate pass; the gates classify tests by tier directory OR filename suffix, so co-located `src/**/*.test.ts` layouts work; the pre-commit invocation omits `--require-all-tiers`), `check_e2e_target.py` (an `e2e`-tier test hard-referencing `localhost`/`docker-compose`/`testcontainers` is an ERROR — integration mislabelled as e2e; `.claude/e2e-target-allow.txt` waives), `check_no_skips.py` (a `skip`/`xfail`/`ignore` marker or a `.only`/`fit` suite-shrinker in a test, or a CI test step that swallows a red — `npm test || true`, `ignoreFailures = true` — is an ERROR; `.claude/no-skips-allow.txt` waives the rare quarantine, always with a reason; audit-build re-runs it `--strict` at release so a declared deferral can't live forever). These make "the tests mock only where allowed, sit at the right tier, and hit the real env for e2e" mechanical, beside the conformance review's semantic judgment
- **the app exposes a `preflight` (a.k.a. `doctor`) command and health/readiness endpoints** — fitness rules both. `preflight` verifies the *running environment* before serving: every required env var present and non-empty · each backing dependency (DB/broker/cache/third-party) reachable and authenticating · migrations applied · returns non-zero with a precise "missing X / can't reach Y". Health (`/healthz` liveness) + readiness (`/readyz` — dependencies ok) endpoints exist so the platform and the deploy smoke-check can gate traffic. This is the operator's "did my setup actually work?" check, the deploy analogue of the per-task report
- `AGENTS.md` and `CLAUDE.md` generated from the same content — and both MUST carry the **final-code-only block** (three rules, verbatim intent): *no fakes outside `tests/`* (no stub/mock/double/canned response in `src/` or the deploy/CI surface) · *no `skip`/`xfail`/`.only` markers, ever* · *a test failing because a dependency isn't ready is the CORRECT state — report the blocker, never code around it*. These are the host entry points present in ordinary sessions — including ad-hoc fixes and subagents that never load a skill — so they are the prose net that covers work outside the exec loop; the tripwires and the exec-gate remain the mechanical enforcement

## Output
Written under `delivery/conventions/`:

| File | Captures | Format |
|---|---|---|
| `coding-standards.md` | language · style · naming · error-handling (as enforceable fitness rules) | typed rule sections |
| `frontend-conventions.md` | design-system usage: semantic/component tokens only (no primitives/raw values) · DS components · voice — as fitness rules · design-token pipeline governance (source-of-truth · transform tool · token-pair contrast a11y check) | typed rule sections |
| `boundary-rules.md` | layering & dependency allow/deny list (arch boundaries as fitness rules) · no-unpinned-deps / lockfile-committed | explicit allow/deny list |
| `workflow.md` | branching (trunk-based · branch per task) · one MR/PR per task · Conventional Commits · build provenance (target SLSA build level · signed artifacts · ≥2-person review / branch protection) · Definition of Done + merge policy | prose |
| `pre-commit-hooks.md` | the CODE hooks (src/+tests/ + the deploy/CI + migration artifacts): format · lint · type · secret-scan · fast SAST · dependency-audit / lockfile-integrity · fast unit · **no-fakes tripwire (`check_no_fakes.py`)** · **deploy-real (`check_deploy_real.py`)** · **migration-real (`check_migration_real.py`)** · **config-drift (`check_config_drift.py`)** · **mock-budget (`check_mock_budget.py`)** · **test-tiers (`check_test_tiers.py`)** · **e2e-target (`check_e2e_target.py`)** · **no-skips (`check_no_skips.py`)** · mechanical conformance subset; + a commit-msg hook validating Conventional Commits — all invoked through the **one** `verify` target CI also calls | commands as code blocks |
| `runtime-contract.md` | what the built artifact needs to run: required env vars (→ `environments.md`) · backing services · the `preflight`/`doctor` command · health (`/healthz`) + readiness (`/readyz`) endpoints · ports · the migrate→seed→flags startup order | typed: runtime requirement sections |

Also emits matching root `AGENTS.md` and `CLAUDE.md` — the Codex and Claude Code entry points: spec map · conventions · workflow · task index · how to work a task · DoD · the final-code-only block (no fakes outside `tests/` · no skip/xfail/.only · red-on-unready-dependency is correct, report it); tight pointer files
ADRs → `adr/ADR-CONV-NNN.md`
*(DERIVED & regenerate-only)*
Consumes: the architecture — its stack choice, layering, and boundaries; and the test strategy's two tiers.

## Excludes
the task list · the code & the actual hook/CI config files

## Resources
- `references/derive-engine.md`
- Worked example: `examples.md`
