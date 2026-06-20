# Operator map — how to drive this system (one page)

## Start here (the 60-second version)
You drive this from Claude Code by talking to the **`grill-spec-conductor`** — it scans state and tells
you the few sensible next moves. You don't memorise the skills; the conductor routes. Loop:
**(1)** open a session → ask the conductor "what's next?"; **(2)** it hands you one area/skill; **(3)**
answer its questions or let it derive; **(4)** it auto-propagates and updates the dashboards; repeat.
Small project? say so — it offers the **lite path**. Just changing one thing? that's **focused-change**.
Want to see an artifact early? just run its skill (gates don't block — see below). Everything you
produce is normal git content; consistency is kept by the linter + propagation.

## The standard flow (greenfield)
`discovery` → `product-vision` → (`market` · `customer-discovery` · `goals` · `context`) → `ddd` (the hub)
→ requirements (`derive-functional` · `quality` · `data-reqs` · `integration-reqs` · `security-reqs` ·
`ux-reqs` · `compliance`) → [`commercial` · `gtm` · `growth` when ready] → **[architecture-readiness]**
→ solution (`derive-architecture` · `-data` · `-api` · `-security` · `-infra-ops` · `-observability` ·
`-test` · `-impl`) → **[implementation-readiness]** → delivery prep (`derive-conventions` →
`derive-tasks`) → **[delivery-readiness]** → per task: `implement-task` → `run-tests` → `conformance-review` (or **`autorun`** for the whole AFK-eligible set, autonomously — see `WORKING.md`)
→ (branch → MR → CI → merge → deploy dev → e2e pipeline) → **(release: your call — consult the readiness checklist)** → operate
(`deploy-release` · `migrate-data` · `operate-incident` → `diagnose`) + maintain (focused changes).
Always available: **`prototype`** (answer one empirical question) · **`generate-docs`** (publish the project site).

## Entry modes (you choose)
- **greenfield** (full walk) · **focused-change** (fast path: enter at the one artifact that changes,
  auto-propagate over the minimal subgraph) · **brownfield-import** (reverse-derive from existing code)
  · **lite path** (tiny product: `discovery` + `product-vision` + `ddd` + a merged `quality`/`context`
  note + minimal `09-solution/arch`; everything else N-A until warranted).

## Gates are readiness signals, not locks
Skills are independently invocable — run any derive/exec skill whenever you want (including early, to
preview output). What you produce is a normal git artifact; if its upstream later changes, the usual
propagation + linter keep it consistent. No special status, no extra steps.

## Which record does a fact belong in? (route here — when unsure, it's an open question)
| The fact | Record |
|---|---|
| a settled choice (+ who set it: user / default) | **the artifact** (+ an ADR in `adr/` for the *why* if load-bearing) |
| not settled yet / blocking | **the artifact** — resolve now, or a **Deferred** point with its trigger |
| a bet that could be wrong (desirability/viability/feasibility) | **inline in the artifact**, with a validation status |
| something that could go wrong, to mitigate | **inline in the artifact** |
| a change that happened (what / when / impact) | **git history** (the changelog) |
| a domain/product term | **`glossary.md`** · an actor/role | **`actors.md`** |
| in-scope content | **the artifact that owns it** (no catch-all file) |
| a HITL ask or human prerequisite (credential · visual ratify · sign-off) | the task's **`blocked`** status / the **bootstrap checklist** |
Five state records, five *distinct questions* — they deliberately don't merge (merging loses the
DVF/validation, provenance, or audit machinery each carries). The load is a *routing* problem, not an
overlap problem: when in doubt it's an **open question**, and the conductor re-routes on its next pass.

## Parallel Claude Code sessions (you, across multiple sessions)
- **One area per session** (the engine enforces one focus). **Prefer a branch per session/area.**
- The shared `adr/` folder is **one file per ADR**, so parallel sessions never collide there; every other artifact is owned by exactly one skill — **re-read before writing** so you build on current content.
- Real conflicts resolve at **git merge**; the **conductor recomputes the true state** on its next run
  after a merge (the records are caches, the repo is the source of truth).

## Two governance domains, kept separate (even when co-located in one repo)
The repo holds two different things; govern them separately (scope hooks by path):

**A. Application / code** (`src/`, `tests/`)
- *Instructions:* `derive-conventions` + `CLAUDE.md` (how Claude writes code).
- *Code pre-commit hooks:* format · lint · type · secret-scan · fast tests · **code fitness functions**
  (boundary/dependency rules) on the changed scope.
- *App CI/CD pipeline (`infra-ops`) = **GitHub Actions***: `.github/workflows/code-ci.yml` on PR
  (format/lint/type · fitness functions · unit/integration/contract tests · secret-scan · CodeQL ·
  optional Layer-2 `conformance-review`) → on merge: dev-deploy → e2e/integration pipeline.

**B. Specification / documentation** (`spec/`, the doc-site) — framework-level, ships with the system
- *Instructions:* the skills/engines.
- *Spec governance (GitHub Actions, ships ready-to-run):* `.github/workflows/spec-governance.yml` runs **`lint_spec.py`** + **`guard_derived.py`** on every PR touching the spec. (Also a pre-commit hook locally.)
- *Derived artifacts are regenerate-only:* everything under `09-solution/`, `05-functional-spec/`, `10-delivery/conventions/`, `10-delivery/tasks/`, and root `CLAUDE.md` changes **only** by re-running its derive-* skill (which records its hash). The guard fails any derived file edited by hand; change the **upstream** and re-derive instead.
- *Publish:* **`generate-docs`** + **`generate-api-reference`** build the doc-site; `.github/workflows/docs-site.yml` deploys it to Pages on push to main.
- *Propagation-miss backup (see below).*

`lint_spec.py` is **not** a coding convention; the doc-site deploy is **not** app infra. Keep them out of
`derive-conventions`/`infra-ops`.

## Stale code is prevented by propagation, not by a status flag
When you change a spec ID (say `AC-101`) that's already built, **propagation flows it to every dependent
(architecture, other UCs, …) and emits a focused-change task to update the code** (`derive-tasks`). That
*pending task* is the enforcement — the change creates the work to fix the code, so nothing built against
the old version ships silently. **Backup only:** CI runs `impact.py --since <last-release>`, lists every
changed ID and its dependents, and flags any dependent code/task that wasn't updated — catching a
propagation *miss*. This is a safety net under spec-governance, secondary to propagation; not a parallel
system.

## Verification map — who checks what, and how it composes (no overlap)
Several surfaces verify the work; they're complementary, not redundant:

| Surface | What it verifies | When | Mechanical? |
|---|---|---|---|
| **`run-tests`** | the slice's own suite is green; every `AC-` exercised | each task | runs |
| **code fitness functions** (pre-commit hook + CI) | boundary/dependency rules, contract shapes | every commit | runs — this **is** conformance-review's mechanical subset, automated |
| **`conformance-review`** | code vs **our spec** (`UC-`/`AC-`/`API-`/`SEC-`/`NFR-` + traceability) **+ design-health** | each task (`changed`) / on demand (`full`) | partly — judgment + the fitness functions above |
| **`audit-spec`** | the **spec itself** — consistency · contradictions · domain/branch completeness · code-gen readiness (the judgment above `lint_spec.py`'s mechanical baseline) | on demand / before a build or release | partly — `lint_spec.py` + `check_contracts.py` baseline + judgment |
| native **`/code-review`** | generic correctness · security · regressions | **ad hoc** (NOT in the pipeline; local CLI, or the hosted GitHub App on Team/Enterprise at ~$15–25/PR) | runs |
| **Tier-B suite** (journey / fitness / NFR) | cross-feature journeys, architectural characteristics, NFR evidence | CI / post-merge pipeline | runs |
| **release-readiness checklist** | everything above is satisfied before *you* ship | when you choose to release | advisory |

Key relationships: **`conformance-review`'s blocking checks ARE the fitness functions the hook/CI run
automatically** — the skill adds what needs judgment (does behaviour match the `AC-`, is the design
deepening). And **`conformance-review` ≠ native `/code-review`**: ours owns spec-conformance +
traceability (the native one has no spec); the native one owns generic bug/security hunting (ours
doesn't), and is **run ad hoc, not wired into CI**. The automated layers all run as **GitHub Actions**
(`.github/workflows/`): `spec-governance.yml` (lint + derived-guard), `code-ci.yml` (Layer 1 + optional
Layer-2 conformance-review), `docs-site.yml` (Pages deploy).
