---
name: autorun
description: >-
  Unattended driver for the coding phase — works the build order one task at a time (or in parallel waves under pr delivery), drives each task to a green gate, lands it, and parks what needs a human. Loads the shared exec engine.
disable-model-invocation: true
argument-hint: the task wave to run autonomously
---

# autorun

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill drives the build order while nobody is watching: pick the tasks that are ready, build each to green, land it, and leave a clear queue of what only a human can clear. Each task is built the way `implement-task` describes; the engine's "Working unattended" section governs how far to push and when to stop.

## Before starting
The run needs a build-ready spec: briefs derived, `lint_spec.py` clean, and no `UNRESOLVED` gap on a task it is about to build. If that does not hold, route the gap to the spec area that owns it first; building against an ambiguous spec produces code that has to be redone.

If `spec-audit-report.md` exists at the project root and its verdict reads `NOT-READY`, do not start. The spec's own audit says the run would build on guesses, so re-audit until it reads ready, or have the human override explicitly.

## Process
1. **Select what is ready.** Read `10-delivery/tasks/build-order.md` and the status table (`python3 ${CLAUDE_PLUGIN_ROOT}/tools/check_task.py spec`). A task is ready when its `phase` row reads `afk: eligible`, every task it `depends` on is done, and it is not done or blocked itself. Two things are checked up front, because finding them mid-slice wastes a run:
   - a `human-prereq` whose credential is not `provisioned` in `spec/_provisioning.md` → mark the task `blocked — <the missing credential>`;
   - a UI slice whose `prototype-review` row is not `frozen`, `reviewed` or `waived — <why>` → mark it `blocked — visual/UX review pending`. An unattended run should not build a screen no human has seen. The practical cadence is to review the prototypes for all queued UI slices in one attended sitting before the run.
2. **Run the tasks the way the project's `delivery` setting allows** (the engine's Delivery table).
   - `trunk`: one task after another on the default branch, in build order. Each push deploys, so push a locally green task (or a small batch of related ones) and see its smoke check pass before building what depends on it.
   - `pr`: the ready tasks may run as a parallel wave, one branch or worktree per task, each with its own pull request. Tasks that touch the same files or module run one after another, since parallel workers cannot see each other's changes. Use the host's managed parallel workflow where it has one; otherwise one subagent or headless process (`claude -p`, `codex exec`) per task.
3. **Land a task when it meets the bar** (below). After it lands, if the task changed the spec, run `python3 ${CLAUDE_PLUGIN_ROOT}/tools/impact.py --since <the ref before the task>` to see which later briefs the change reaches.
4. **Confirm the default branch is healthy before building on it.** After a wave merges (`pr`) or a push deploys (`trunk`), run the system suite the project runs at that point and read the deploy's smoke check. If either is red, stop launching tasks and report; work stacked on a red default branch has to be untangled later.
5. **Recompute the ready set and repeat** until no eligible task with satisfied dependencies remains.

## The landing bar
A task lands when all of these hold:

| Bar | Checked by |
|---|---|
| the project's gate is green | the gate command from its conventions, plus any tier it leaves out that the slice touches |
| the done-claim holds against the tree | `python3 ${CLAUDE_PLUGIN_ROOT}/tools/check_task.py spec --task T-NNN` |
| `critical` only: an independent review passed | the brief's `review` row reads `PASS`, set by the reviewer |

Under `pr`, merge on a green pull request where the project's review policy lets an agent merge; where the policy reserves the merge for a human, leave the pull request open and list it in the report. Under `trunk`, push, and treat the smoke check as the confirmation.

## Rules
- **Review in a fresh context where the tier requires it.** A `critical` task gets one `conformance-review` from a subagent or separate session that did not write the code, for at most two rounds; a disagreement that survives them goes to the human. `routine` and `feature` tasks are covered by the gate, `check_task.py` and the implementer's own diff review. A reviewer per task would multiply the cost of the run without adding a check the tier asked for.
- **Hold out acceptance criteria on reviewed tasks.** An agent that sees every criterion can build exactly to the visible tests and no further. For a task that will get a fresh-context review, withhold one or two criteria (black-box, observable ones that need no knowledge of the internal design) by passing the implementer the brief's text with those lines left out. The reviewer, holding the full brief, tests them against the built slice. A held-out criterion that fails goes back to the implementer, revealed, because it has to be fixed. `check_task.py` reads the full brief, so a held-out criterion still needs its `@covers` test before the task is done. This applies only where there is a separate implementer and reviewer.
- **Keep the credential register current.** When a provisioning task lands, or a human clears a credential ask, set that row in `spec/_provisioning.md` to `provisioned` with its evidence. The next ready set is computed from the register, so provisioned state is recorded there rather than inferred from which tasks passed.
- **Park instead of thrashing.** A task that needs a human decision, stops converging, or reaches its per-task token or iteration ceiling is escalated as the engine describes: the blocker, a recommended default for the human to ratify, and what they must do, in `spec/_human-input.md`; `status` set to `blocked — <why>`; then on to the next task. A ceiling is a reason to park the task, not to loosen its gate.
- **Size the run to the budget.** Parallel workers may draw on a separate host or CI quota. A strong reasoning model suits orchestration; a capable faster one suits a bounded per-task worker.

## Output
The run leaves code on the default branch (or open pull requests), the briefs' `status` rows, and the escalation queue. It keeps no log of its own: `check_task.py spec` prints the current state of every task from the tree.

When no ready task remains, report to the user as the engine's Reporting section says:

| Group | Content |
|---|---|
| landed | task ids with a few words each, and how each was confirmed (smoke check, merged pull request) |
| blocked | task id · the blocker · the recommended default · what the human must do |
| waiting on a human merge | open pull requests the review policy reserves, under `pr` |
| remaining | tasks not eligible for an unattended run, or deferred |

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
