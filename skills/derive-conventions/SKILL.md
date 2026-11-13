---
name: derive-conventions
description: >-
  Derive the coding agent's standards and runway from the architecture — style, boundary rules as
  enforceable checks, the delivery workflow, the one gate command, the definition of done — and write
  the root AGENTS.md agent guide with its import-only CLAUDE.md adapter.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# derive-conventions

**Load `references/derive-engine.md` first and follow it.** This skill applies that method to **coding conventions and agent setup** — what a coding agent needs to know that the code cannot tell it, and the gate that holds the code to it.

## What good conventions look like
Conventions exist so that an agent with no memory of earlier sessions builds the next slice the way the last one was built. Two properties make them work:

- **A rule is a check, or it is short.** A rule that can be checked mechanically — an import boundary, a banned construct, a naming grammar, config that must be declared — becomes part of the project's gate, and the document only names it. A rule that cannot be checked is stated once, with its reason, because a rule nobody enforces and nobody remembers the reason for is ignored or over-applied.
- **Gates grow from evidence.** Start with the small core that every project needs, and add a gate when a defect shows one was missing. A catalogue of gates written up front costs time on every change and mostly guards against failures that never happen.

## Method
1. From the architecture, confirm the language and framework, then set naming, style and error handling — only where the project deviates from the stack's idiom or where two reasonable engineers would differ.
2. Turn the architecture's boundaries into the dependency rules the gate enforces: which module may import which, and what crosses a context boundary.
3. Set the workflow from the project's delivery mode (`python3 scripts/project_config.py`): `trunk` or `pr`, as the exec engine's Delivery table describes. The delivery mode and any branch-protection or approver policy belong to the user; when they are not yet set, propose `trunk` for a solo pre-production project and `pr` otherwise, and surface it as a ratify-point.
4. Define the one gate command and the exact commands behind it.
5. Write the definition of done, then the agent guide.

## Rules
- **One gate, defined once.** A single target (`verify` or the stack's equivalent) runs format, lint, types, the fast tests, and the project's checks; the pre-commit hook and CI call that same target, so green locally means green in CI. In `trunk` delivery CI does not re-run it; in `pr` delivery CI runs it on the pull request together with the slower tiers.
- **The core gate set.** Every project starts with: the architecture's import boundaries as a dependency rule; no fake in the shipping tree (`check_no_fakes.py`); no skipped or shrunk test (`check_no_skips.py`); every behaviour test tagged with what it proves and every tag naming a live spec ID (`check_orphan_tests.py`); the config the code reads is declared (`check_config_drift.py`, when the project has an environments matrix); a pinned lockfile. A deployable project adds `check_deploy_real.py` and `check_migration_real.py`; a project with a tier contract in `test/levels.md` adds `check_mock_budget.py`, `check_test_tiers.py` and `check_e2e_target.py`. A UI project adds tokens-only styling. Record any further gate with the defect that motivated it in one line; without one, leave it out.
- **Coverage and mutation bars come from the tier contract** and are enforced by the test runner's own configuration, scoped to changed code where the stack supports it, so a small untested change cannot hide in a whole-tree percentage.
- **`@covers` is how behaviour is traced.** A behaviour test carries `@covers AC-…` (and a UI state test `@state:<name>`) in a recognisable test file; `check_task.py` reads those tags to decide whether a task's done-claim holds. Say where the tag goes in this stack (a comment, an annotation, the test name).
- **Config comes from the environment.** No hard-coded value and no real secret in the repo; an example file lists every key with a placeholder.
- **Runtime contract.** The app has a `preflight` command that checks the running environment (required variables present, each dependency reachable, migrations applied) and exits non-zero with a precise reason, plus liveness and readiness endpoints the platform and the post-deploy smoke check use.
- **Project state is host-neutral.** Everything Grillspec owns outside `spec/` lives under `.grillspec/` (settings, vendored tools, gate configuration, waivers); `.claude/settings.json` and `.codex/hooks.json` hold only the hook adapter. A monorepo that roots its code under a wrapper directory sets `GRILLSPEC_TEST_ROOTS` once so the test-facing checks see it.
- **The agent guide is short.** `AGENTS.md` is read at the start of every session, so every line costs attention each time. It holds what an agent needs before touching code: what the product is in two sentences, where code and spec live, the commands, the delivery mode, the change lifecycle, the handful of rules no gate enforces (each with its reason), and where tasks are defined. The change lifecycle is what makes a request typed into chat ("add X", "fix Y") follow the project's method instead of going around it: size the change by risk tier; align with the spec before touching code (find the criteria and rules that govern it, write new behaviour into the owning area first, and stop to ask when the request contradicts the spec); brief it; build it test-first with tagged tests; prove it with the gate and land it per the delivery mode — naming the skill that carries each step. The guide points into the spec and the conventions instead of restating them, carries no history, and stays under about fifteen hundred words. Generate `CLAUDE.md` with exactly `@AGENTS.md` plus a trailing newline, so every host reads the same guide.
- **Spec governance is separate.** The gate above governs code and delivery artifacts. The spec is checked by `lint_spec.py` through the project-local pre-commit hook (`spec_governance_hook.sh`); scope each by path when they share a repository.

## Depth by profile
| Profile | Write |
|---|---|
| `lite` | `coding-standards.md`, `boundary-rules.md`, `workflow.md` (with the commands and the definition of done), and the agent guide. The few test and environment decisions the profile has no separate area for go into `workflow.md`. |
| `standard` · `regulated` | all six files below |

## Output
Written under `delivery/conventions/`:

| File | Captures | Format |
|---|---|---|
| `coding-standards.md` | language · style · naming · error handling — the deviations from the stack's idiom, each as a checkable rule where possible | short rule sections |
| `boundary-rules.md` | the allow/deny list for imports between layers and contexts, and the gate that enforces each | allow/deny table |
| `frontend-conventions.md` | design-system usage (semantic and component tokens only · design-system components · the voice guide) and the token pipeline (one source · the transform tool · the contrast check) — UI projects only | short rule sections |
| `workflow.md` | the delivery mode and what it means here · commit conventions · the gate command and the commands behind it · the definition of done | prose + commands as code blocks |
| `pre-commit-hooks.md` | the hook set, each invoking the one gate target; the commit-message check | commands as code blocks |
| `runtime-contract.md` | what the built artifact needs to run: required variables (pointing at the environments matrix) · backing services · `preflight` · health and readiness endpoints · startup order | typed sections |

Also writes root `AGENTS.md` (the agent guide described above) and root `CLAUDE.md` with exactly `@AGENTS.md`.
ADRs → `adr/ADR-CONV-NNN.md`
Consumes: the architecture — its stack, layering and boundaries; the tier contract where the project has one; the project's delivery mode.

## Excludes
the task list · the code and the actual hook/CI configuration files

## Resources
- `references/derive-engine.md`
- Worked example: `examples.md`
