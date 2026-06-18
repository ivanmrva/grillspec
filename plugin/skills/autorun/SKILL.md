---
name: autorun
description: >-
  Autonomous AFK driver for the coding phase — drives the per-task implement → done-gate → conformance loop across the task DAG in parallel, self-correcting code to green, merging on green, unlocking dependents, parking true HITL needs. Use when the spec is implementation-final and you want the coding phase driven AFK across the whole DAG. Loads the shared exec core.
disable-model-invocation: true
argument-hint: the task wave to run autonomously
---

# autorun

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill: **autonomous execution of the task DAG (AFK)** — implement → done-gate → conformance, in parallel, until each task's gate is fully green.

## Process
1. **Select the ready wave.** From `08-delivery/tasks/build-order.md`, take every task that is **AFK-eligible** (`afk: eligible` — no HITL trigger, no unresolved gap) **and** whose `depends:` are all merged.
2. **Run the wave in parallel.** Prefer **dynamic workflows** (Opus 4.8) for the whole wave; otherwise one subagent (or `claude -p`) per task. **Each task runs the full done-gate loop** — implement → run the whole gate → self-correct the *code* → repeat until green — honoring the **anti-cheat invariants** (fix code not goalposts · spec is upstream truth · green ≠ done · never disable a gate).
3. **Merge, propagate, recompute.** On a green gate that passes the conformance review — **run in a fresh / independent context, not the self-correcting loop's own verdict** — merge → run propagation (`impact.py`) → **run the wave-level integration gate** (the system/Tier-B suite after this wave's merges, before launching the next) → recompute the ready wave (dependents now unlocked) → launch the next wave. If the integration gate turns main red, **park the wave** and stop launching. Repeat until no AFK-eligible, dependency-ready task remains.

## Rules
- **Merge on green only** — a task merges only when its gate is fully green and the conformance review returns `VERDICT: PASS`; the PR's CI is the backstop, not the bar.
- **Independent verdict (hard pre-merge invariant)** — the conformance review that gates a merge **runs in a fresh / independent context**, never the implementing self-correcting loop's own verdict (a loop can't certify itself). Consider holding out a small **AC subset** not shown to the implementing agent, checked only at this gate.
- **Wave-level integration gate** — after each wave's merges, run the system/Tier-B suite before launching the next wave; if main goes red, **park the wave** (stop launching dependents) and report, rather than building on a red main.
- **Don't thrash — park** — a task that hits an anti-cheat wall, a genuine HITL need, the loop's no-converge cap, **or its per-task token/iteration ceiling** → mark it `blocked` with the **precise blocker** (and, for a UX/decision block, a **proposed default for the human to ratify**), and continue with the rest of the wave. The token/iteration ceiling is an explicit park trigger, not a reason to weaken the gate.
- **Parallelism safety** — never parallelize tasks that touch the same files/module (merge-conflict risk) — serialize those; subagents can't share state mid-run. Keep each task one focused slice.
- **Cost** — parallel subagents/headless runs draw the separate Agent-SDK/CI token pool — size the wave to budget; Opus for this orchestration, Sonnet for the per-task subagents.
- **Stop & report** — when the DAG is drained, report **merged** (`T-` ids) · **blocked** (reasons, awaiting human input) · **remaining** (HITL/deferred). Never mark a task done on red; never merge a non-green gate. Code lives in the source tree, never in `spec/`.

## Output
Written under `<working-root>/` (drives the per-task implement → test → conformance loop; merges code on green — code lives in the source tree):

| File / target | Captures | Format |
|---|---|---|
| `<working-root>/autorun-log.md` | the run record: merged (T- ids) · blocked (reason + awaiting-human input · proposed default to ratify) · remaining (HITL/deferred) | — |

(no spec changes)
Consumes: an **implementation-final** spec — tasks derived, `lint_spec` clean, **no task carrying an `UNRESOLVED` gap**. If not, stop and route to the owning upstream area first (don't implement against an ambiguous spec).

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
