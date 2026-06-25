---
name: autorun
description: >-
  Autonomous AFK driver for the coding phase — drives the per-task implement → done-gate → conformance loop across the task DAG in parallel, self-correcting code to green, merging on green, unlocking dependents, parking true HITL needs. Use when the spec is implementation-final and you want the coding phase driven AFK across the whole DAG. Loads the shared exec engine.
disable-model-invocation: true
argument-hint: the task wave to run autonomously
---

# autorun

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill: **autonomous execution of the task DAG (AFK)** — implement → done-gate → conformance, in parallel, until each task's gate is fully green.

## Process
1. **Select the ready wave.** From `10-delivery/tasks/build-order.md`, take every task that is **AFK-eligible** (`afk: eligible` — no HITL trigger, no unresolved gap) **and** whose `depends:` are all merged.
2. **Run the wave in parallel.** Prefer **dynamic workflows** (Opus 4.8) for the whole wave; otherwise one subagent (or `claude -p`) per task. **Each task runs the full done-gate loop** — implement → run the whole gate → self-correct the *code* → repeat until green — honoring the **anti-cheat invariants** (fix code not goalposts · spec is upstream truth · green ≠ done · never disable a gate).
3. **Merge, propagate, recompute.** On a green gate that passes the conformance review — **run in a fresh / independent context, not the self-correcting loop's own verdict** — merge → run propagation (`impact.py`) → **run the wave-level integration gate** (the system/Tier-B suite after this wave's merges, before launching the next) → recompute the ready wave (dependents now unlocked) → launch the next wave. If the integration gate turns main red, **park the wave** and stop launching. Repeat until no AFK-eligible, dependency-ready task remains.

## Rules
- **Merge on green only** — a task merges only when its gate is fully green, **a recorded conformance-review `VERDICT: PASS` for this `T-` physically exists under `spec/10-delivery/verification/`**, **and its Verification Record is green** (`python3 ${CLAUDE_PLUGIN_ROOT}/tools/check_task_record.py spec --task T-NNN` exits clean — `status: done`, every referenced obligation evidenced). The artifacts are the proof the bookends ran — "I reviewed it" / "it's done" without the recorded verdict and a green record does not count; the PR's CI is the backstop, not the bar. A task whose tests were back-filled after the code (an `AC-` with no passing traceability row), whose conformance artifact is missing/`FAIL`, or whose record has an unmet/dropped obligation is **parked, not merged**.
- **Independent verdict (hard pre-merge invariant)** — the conformance review that gates a merge **runs in a fresh / independent context**, never the implementing self-correcting loop's own verdict (a loop can't certify itself).
- **Held-out acceptance criteria (anti-overfitting — the strongest lever)** — to stop an agent implementing *exactly to the visible tests and no further*, **withhold a small subset of each task's `AC-`** from the implementing agent. The mechanism, which you (the orchestrator) own because only you see the full task:
  1. partition the task's `AC-` into **shown** (the bulk) and **held-out** (1–2, or ~20% — pick **black-box, observably-testable** criteria, never ones needing the implementer's internal design);
  2. dispatch the task package **and** its `--init` Verification Record with the held-out `AC-` **stripped** — the implementer TDDs only what it can see;
  3. at the gate, the **independent reviewer** (full task in hand) authors fresh acceptance tests for the held-out `AC-` — or runs the Tier-B system acceptance tests that already cover them — against the built slice;
  4. a held-out `AC-` that **fails** is overfitting/incompleteness → back to implementation (the `AC-` is now revealed, because it must be fixed); all pass → strong evidence the slice generalizes beyond the visible tests.
  The backstop is automatic: `check_task_record.py` regenerates the obligation set from the **frozen full task**, so the held-out `AC-` are required at the gate no matter what the implementer's stripped record showed — they surface as ordinary obligation rows the reviewer must evidence. **Scope:** this is an **AFK/orchestrated-mode** policy (it needs a separate dispatcher and verifier); it's inherently **N/A for a solo `implement-task` run**, where the human reviewer is the independent check. Record the held-out set + their independent result in the Verification Record (a `held-out:` line) so the withholding is itself auditable.
- **Wave-level integration gate** — after each wave's merges, run the system/Tier-B suite before launching the next wave; if main goes red, **park the wave** (stop launching dependents) and report, rather than building on a red main.
- **Don't thrash — park** — a task that hits an anti-cheat wall, a genuine HITL need, the loop's no-converge cap, **or its per-task token/iteration ceiling** → mark it `blocked` with the **precise blocker** (and, for a UX/decision block, a **proposed default for the human to ratify**), and continue with the rest of the wave. The token/iteration ceiling is an explicit park trigger, not a reason to weaken the gate.
- **Parallelism safety** — never parallelize tasks that touch the same files/module (merge-conflict risk) — serialize those; subagents can't share state mid-run. Keep each task one focused slice.
- **Cost** — parallel subagents/headless runs draw the separate Agent-SDK/CI token pool — size the wave to budget; Opus for this orchestration, Sonnet for the per-task subagents.
- **Stop & report** — when the DAG is drained, report **merged** (`T-` ids) · **blocked** (reasons, awaiting human input) · **remaining** (HITL/deferred). Never mark a task done on red; never merge a non-green gate. Code lives in the source tree, never in `spec/`.

## Output
Written under `<working-root>/` (drives the per-task implement → test → conformance loop; merges code on green — code lives in the source tree):

| File / target | Captures | Format |
|---|---|---|
| `<working-root>/autorun-log.md` | the run record: merged (T- ids) · blocked (reason + awaiting-human input · proposed default to ratify) · remaining (HITL/deferred); for each merged task, the **tool-vouched completion report** (`check_task_record.py spec --report T-NNN`) so the whole AFK run is auditable after the fact | — |

(no spec changes)
Consumes: an **implementation-final** spec — tasks derived, `lint_spec` clean, **no task carrying an `UNRESOLVED` gap**. If not, stop and route to the owning upstream area first (don't implement against an ambiguous spec).

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
