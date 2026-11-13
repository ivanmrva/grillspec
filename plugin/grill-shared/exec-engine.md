# exec-engine — shared core for build/verify skills (NOT an interview)

The shared method behind every exec profile. The profile's `SKILL.md` is the entrypoint and names what varies (the task, scope, what it touches); this engine is the judgment that is the same for all of them: how much process a change owes, the test-first cadence, what "done" means, and when to stop and ask.

Your output is code and short reports in the project source tree. Code lives in the repo, never in `spec/`. The spec states what the product must do; when you find it wrong or silent, the fix goes into the spec area that owns it, in the same change as the code, so the two never disagree. On a re-run you resume from the current state of the code and tests, not from memory.

**Shared rules:** load `${CLAUDE_PLUGIN_ROOT}/grill-shared/house-rules.md` (the workspace as source of truth · timeless artifacts · writing for the reader · ID mechanics · plugin-feedback routing) and `${CLAUDE_PLUGIN_ROOT}/grill-shared/decision-classes.md` (what you decide vs. escalate: decide what engineering merit settles, ask only for a fact the user, org or platform holds).

## Project settings

Two settings in `.grillspec/project.json` scale everything below. Read them with `python3 ${CLAUDE_PLUGIN_ROOT}/tools/project_config.py`.

| Setting | Values | What it changes here |
|---|---|---|
| `profile` | `lite` · `standard` · `regulated` | how much spec exists to build against. Build to what is there; a missing area is not a gap to fill unless the task needs a decision only that area would hold. |
| `delivery` | `trunk` · `pr` | where work lands and where verification runs (see Delivery below). |

## Step zero — arm the edit hook

At the start of an exec session, when this method's toolset is available, run `python3 ${CLAUDE_PLUGIN_ROOT}/tools/install_exec_gates.py` (idempotent). It vendors the project-local tools under `.grillspec/tools/` — the edit hook (`gate_exec.py`), the task and test-driver checks (`check_task.py`, `check_orphan_tests.py`), and the spec pre-commit hook with the checks it runs (`spec_governance_hook.sh`, `lint_spec.py`, `check_contracts.py`) — and wires one PreToolUse hook into `.claude/settings.json` and `.codex/hooks.json`. The project is then governed in any session, with or without this toolset installed. The hook denies an edit that introduces a skipped test or a fake in the production tree, at the moment it is written; that is cheaper than finding it after code has been built on top of it. In Codex, review and trust the project hook through `/hooks`. Without the toolset the rules below still apply; say plainly which checks you could not run.

## Risk tier — how much process a change owes

Process is paid for by risk, not charged uniformly. The task brief carries the tier; a change with no brief is `routine` unless it meets a `critical` condition, in which case it gets a brief first.

| Tier | What it is | What it owes |
|---|---|---|
| `routine` | a bug fix, a copy or visual tweak, a refactor, a dependency bump — no new behaviour | a failing test first where behaviour is involved (for a bug, tagged `@covers` the criterion it violated), the fix, the gate. No task file. |
| `feature` | new behaviour inside an existing module or context | the brief, test-first, the gate |
| `critical` | a new aggregate or context · a schema or data migration · authentication, authorization, erasure, billing or another money/legal path · a model/LLM seam · any one-way door | the brief, a short design note before coding (`derive-impl-design`), the gate, and one fresh-context conformance review |

If work turns out riskier than its tier (a `feature` that needs a migration), raise the tier and say so; do not finish it under the lighter one.

## Scoped context

Load the task brief, the code it touches, and the spec passages the brief points at when you need more than the brief quotes. A brief is written to be self-contained: its acceptance criteria carry their text, and its `rules` cell states the cross-cutting obligations that bind the slice. Reading the whole upstream spec for a coding slice costs attention and makes the work worse; the broad view belonged to the step that cut the slice.

When the spec is wrong, contradictory or silent for this slice:
- If two competent engineers would settle it the same way, decide, and write the decision where it belongs (the acceptance criterion, the owning requirement, or an ADR for a costly-to-reverse choice) in the same change.
- If it turns on a fact only the user or organisation holds, record `GAP <what is undecided> — <owning area> — UNRESOLVED` on the brief, ask once with your recommended default, and continue with work that does not depend on the answer.

A request that arrives in chat mid-task is handled the same way: a behaviour change becomes an acceptance criterion in the spec and a test before it becomes code; new scope becomes a new brief; a rename or pure refactor just proceeds.

## Test-first, one behaviour at a time

Build one thin vertical slice at a time, end to end (entrypoint → application → domain → persistence). Within it:

1. Write one small test for the next piece of observable behaviour, taken from an acceptance criterion or an edge you found. Run it and see it fail for the right reason; a test never seen failing proves nothing.
2. Write the smallest real implementation that passes.
3. Refactor only with the suite green.

Then the next behaviour. Writing all the tests and then all the code produces tests that assert imagined behaviour, so keep the cycle short. Tests assert behaviour through the public interface, not internals. Tag each behaviour test with what it proves: `@covers AC-…` for an acceptance criterion, `@state:<name>` for a UI interaction state. Those tags are how done is checked (below) and how a later change finds the tests to re-run.

Tests span the layers the slice touches, per the project's tier contract (`09-solution/test/levels.md` where the project has one, otherwise its conventions): unit for domain logic; integration for the adapters and persistence the slice adds, against a real local dependency; contract for a seam it exposes or consumes; e2e only for a user-observable path that needs the deployed system, kept few. A cross-cutting rule named in the brief (an authorization rule, a retention trigger, an entitlement limit, a quality target, an emitted signal) is proven by a test in the slice that ships it — the deny path, the over-limit path, the measured number — because a rule with no test is the one that silently never gets built.

## Production code is real from the first line

The shipping tree carries only production behaviour. A stub, an in-memory double, a canned response, or an "if the real thing isn't wired, return something plausible" branch makes every test pass against a system that does nothing, and the fake outlives the excuse for it. Test doubles live under the test tree and are injected through the production constructor.

When a dependency is not available, let the test stay red: that is the accurate signal. Either drive the real dependency through a local container in the test layer, or, when it truly cannot run yet, record the provisioning step in `spec/_human-input.md` (and the credential in `spec/_provisioning.md`), mark the task `blocked`, and move on. A red suite over a real implementation is a good outcome to report; a green suite over a fake is the failure.

The same holds for what ships around the code: the deploy pipeline really deploys, a schema change really migrates, and a UI screen is built to its prototype, its named states and the design system's tokens rather than as a rough draft to polish later. `check_deploy_real.py` and `check_migration_real.py` are the static backstops.

## Done

A task is done when its behaviour is proven and the project's gate is green. Concretely:

| What | Checked by |
|---|---|
| format · lint · types · build clean; the test tiers the slice touches pass; coverage and mutation bars met | the project's one gate command (from its conventions) |
| architecture boundaries and the project's other fitness functions hold | the same gate |
| every acceptance criterion in the brief has a `@covers` test; every named UI state has a `@state:` test; no unresolved gap; dependencies done | `python3 ${CLAUDE_PLUGIN_ROOT}/tools/check_task.py spec --task T-NNN` |
| no test without a spec driver; no skipped test; no fake in the shipping tree | `check_orphan_tests.py` · `check_no_skips.py` · `check_no_fakes.py` (or the project's own ports of them) |
| a slice that adds a deployable surface or a schema change ships a real deploy / migration | `check_deploy_real.py` · `check_migration_real.py`, and the smoke check after deploy |
| `critical` only: the design note exists and a fresh-context review returned `PASS` | the brief's `design` and `review` rows, read by `check_task.py` |

Then set the brief's `status` row to `done`. Nothing else is recorded: status, coverage of criteria and the criterion-to-test trace are computed from the tree on demand (`check_task.py`, `--json`, `--trace`), so there is no ledger to keep in step with the code.

**The review is independent or it is not a review.** For a `critical` task the conformance review runs in a fresh context (a subagent or a separate session) that did not write the code. Its findings come back to you as a short report; you fix them and it looks again, at most twice — a third disagreement goes to the human with both positions. The reviewer, not the implementer, sets `review | PASS` on the brief. For `routine` and `feature` work, review your own diff against the brief before claiming done: behaviour matches the criteria, boundaries intact, tests assert behaviour, nothing beyond the brief.

## Working unattended

Drive the gate to green yourself rather than handing back a half-finished task: run the whole gate, find the root cause of each failure, fix the code, run it again. Ordinary obstacles — a flaky command, a timeout, an empty result — are things to work through. Stop and escalate when the failure set has not shrunk for two rounds, when a human decision is genuinely needed (a visual or product call, a legal sign-off, a credential), or when the clean design cannot satisfy the criterion without crossing a boundary. Escalating means: append to `spec/_human-input.md` the task, the precise blocker, your recommended resolution, and exactly what the human must do; mark the brief `blocked — <why>`; continue with other eligible tasks.

A few shortcuts make a gate pass without making the software right, and each one is the actual failure even when it buys a green run:
- weakening or deleting a test, lowering a threshold, or adding a skip, so the gate stops seeing the defect — a test changes only when the behaviour it describes changed;
- a fake in the shipping tree, or an e2e that steers around the path that is not ready;
- crossing a module or layer boundary, or duplicating logic, to get a test green — if the clean design cannot do it, that is a design finding to raise;
- disabling a hook, a fitness function or a gate.

## Delivery

| | `trunk` | `pr` |
|---|---|---|
| Where work lands | on the default branch; related slices may share one push | a short-lived branch per task and one pull request |
| Verification | local, once: the tests the change touches while iterating, the project's gate before a push | the same local gate, then the full CI gate on the pull request |
| CI | deploys the default branch and smokes it; every other job runs on dispatch | runs the full gate on the pull request, merges on green, deploys on merge |
| Human window | the escalation queue and the `critical` review | the pull request, where the project's review policy requires one |
| Unattended waves | tasks run one after another | tasks may run in parallel, one branch or worktree each |

In either mode: commit only the task's own changes, in small atomic commits with messages that describe the change; never push to make CI check something a local run can show; after a deploy, the smoke check against the deployed environment is the authoritative signal that it shipped.

## Reporting

Write for a reader who has not seen your tool calls or the files you opened. Lead with what was done and what state it is in; then what you found that the reader should know, what remains, and what you need from them. Say plainly which checks ran and which did not. Use the task and criterion ids where they help the reader find things, with a few words saying what each is. A table suits a list of like items (criteria and their status, failures and their cause); connected reasoning reads better as a short paragraph.
