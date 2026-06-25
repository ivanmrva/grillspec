---
name: derive-conventions
description: >-
  Derive the coding agent's standards and runway from the architecture — style, boundary rules as fitness checks, workflow, build/run/test/lint commands, Definition of Done — and generate the root CLAUDE.md. Use when the architecture exists and you need the coding-agent setup. Loads the shared derive engine.
disable-model-invocation: true
argument-hint: a recorded spec or design docs
---

# derive-conventions

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md` first and follow it.** This skill applies that method to **Coding conventions & agent setup** — the instruction-set Claude Code follows to produce code, plus its entry point.

## Method
1. confirm language/framework (from the architecture) → naming/style/error-handling
2. layering & dependency (boundary) rules → test approach
3. engineering workflow (branch-per-task · MR · hooks · CI gates · review)
4. the exact commands → the Definition of Done
5. the CODE pre-commit hooks (incl. a fast SAST pass + a dependency-audit / lockfile-integrity step) + a commit-msg hook validating Conventional Commits + the build-provenance / artifact-signing convention + design-token pipeline governance → generate root `CLAUDE.md`

## Rules
- standards set; dependency/boundary rules explicit and expressed as **enforceable fitness rules**; **no unpinned deps, lockfile committed** is one such rule (audited in-hook)
- frontend/design-system conventions are fitness rules too: semantic/component tokens only (never primitives/raw hex/px), build only design-system components (their variants · sizes · states) per the implementation mapping, copy follows the voice guide; **design-token pipeline governance** — one token source-of-truth · a named transform tool · a token-pair **contrast** a11y check on every semantic foreground/background pairing
- workflow defined (trunk-based · branch per task, no direct commits to main · one MR/PR per task · Conventional Commits enforced by a commit-msg hook) — but the **branching model / git workflow is a ratify-point, not a silent merit pick**: propose trunk-based + branch-per-task as the default and **surface it for the human to confirm or override** (an org may mandate GitFlow, long-lived release branches, a different review-gate / approver count, or a protected-branch policy the spec can't derive). Record the ratified workflow in `workflow.md`; an un-ratified default is an assumption to flag
- **build provenance** — target a stated SLSA build level · artifacts signed · ≥2-person review / branch protection on the release path
- build/test/lint commands runnable; DoD includes 'merged via green CI'
- **CODE governance only** — the pre-commit hooks govern `src/`+`tests/` only (format · lint · type · secret-scan · fast unit · **the no-fakes tripwire (`check_no_fakes.py`)** · the mechanical conformance subset: boundary/dependency fitness functions + contract checks, on the changed scope). The *spec/docs* are governed by a **separate** framework-level enforcer (`lint_spec.py` + `guard_derived.py` over `spec/`, + the doc-site); scope the hooks by path even when co-located. The *checks* are not optional; the *release* decision stays the team's
- **one gate, defined once — pre-commit and CI invoke the same target** (a `verify` script / Make target / task runner entry), never two hand-kept lists that drift; the **done-gate enumeration in the exec engine is the canonical set** that target implements. "Green locally" then means exactly "green in CI" — an agent can't pass a weaker local subset and lean on CI
- **no fakes in production is enforced two ways** — the shipped cross-language tripwire `check_no_fakes.py` (a Fake*/Stub*/Mock*/Dummy* definition or a mocking-library import under `src/` is an ERROR; an `unconfigured→fallback`/placeholder body is a WARN; `.claude/no-fakes-allow.txt` waives the rare legit case) **and** a per-language **architecture fitness function** (the import-graph rule — no test double reachable from a production entrypoint) the test strategy derives; the tripwire fires even when the fitness function was never written
- **every behavior test is tagged `@covers AC-NNN`** (a decorator/annotation/comment/name carrying the AC id it drives) — this is a fitness rule: it puts the AC id literally in the test source, so coverage is verified against the tree (by `check_task_record.py`), not a hand-authored matrix that could claim a test that doesn't exist
- **config drift is gated** — `check_config_drift.py` reconciles the env vars the **code reads** against the **declared** `infra-ops/environments.md` matrix; a key the code reads but the matrix doesn't declare is an ERROR (the operator can't provision it → first-run outage). Config is read **only** from the environment (never hard-coded, never a checked-in real value); a `.env.example` lists every key with a placeholder, never a secret
- **the app exposes a `preflight` (a.k.a. `doctor`) command and health/readiness endpoints** — fitness rules both. `preflight` verifies the *running environment* before serving: every required env var present and non-empty · each backing dependency (DB/broker/cache/third-party) reachable and authenticating · migrations applied · returns non-zero with a precise "missing X / can't reach Y". Health (`/healthz` liveness) + readiness (`/readyz` — dependencies ok) endpoints exist so the platform and the deploy smoke-check can gate traffic. This is the operator's "did my setup actually work?" check, the deploy analogue of the per-task report
- CLAUDE.md generated

## Output
Written under `delivery/conventions/`:

| File | Captures | Format |
|---|---|---|
| `coding-standards.md` | language · style · naming · error-handling (as enforceable fitness rules) | typed rule sections |
| `frontend-conventions.md` | design-system usage: semantic/component tokens only (no primitives/raw values) · DS components · voice — as fitness rules · design-token pipeline governance (source-of-truth · transform tool · token-pair contrast a11y check) | typed rule sections |
| `boundary-rules.md` | layering & dependency allow/deny list (arch boundaries as fitness rules) · no-unpinned-deps / lockfile-committed | explicit allow/deny list |
| `workflow.md` | branching (trunk-based · branch per task) · one MR/PR per task · Conventional Commits · build provenance (target SLSA build level · signed artifacts · ≥2-person review / branch protection) · Definition of Done + merge policy | prose |
| `pre-commit-hooks.md` | the CODE hooks (src/+tests/ only): format · lint · type · secret-scan · fast SAST · dependency-audit / lockfile-integrity · fast unit · **no-fakes tripwire (`check_no_fakes.py`)** · **config-drift (`check_config_drift.py`)** · mechanical conformance subset; + a commit-msg hook validating Conventional Commits — all invoked through the **one** `verify` target CI also calls | commands as code blocks |
| `runtime-contract.md` | what the built artifact needs to run: required env vars (→ `environments.md`) · backing services · the `preflight`/`doctor` command · health (`/healthz`) + readiness (`/readyz`) endpoints · ports · the migrate→seed→flags startup order | typed: runtime requirement sections |

Also emits root `CLAUDE.md` — the agent's entry point: spec map · conventions · workflow · task index · how to work a task · DoD; a tight pointer file
ADRs → `adr/ADR-CONV-NNN.md`
*(DERIVED & regenerate-only)*
Consumes: the architecture — its stack choice, layering, and boundaries; and the test strategy's two tiers.

## Excludes
the task list · the code & the actual hook/CI config files

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md`
- Worked example: `examples.md`
