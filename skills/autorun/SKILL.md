---
name: autorun
description: >-
  Autonomous AFK driver for the coding phase — runs the per-task implement → done-gate → conformance loop across the task DAG in parallel, self-correcting to green, merging on green, parking true HITL blockers. Loads the shared exec engine.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# autorun

**Load `references/exec-engine.md` first and follow it.** This skill: **autonomous execution of the task DAG (AFK)** — implement → done-gate → conformance, in parallel, until each task's gate is fully green.

## Process
1. **Select the ready wave.** From `10-delivery/tasks/build-order.md`, take every task that is **AFK-eligible** (`afk: eligible` — no HITL trigger, no unresolved gap) **and** whose `depends:` are all merged. **If a `spec-audit-report.md` exists at the project root and its verdict reads `NOT-READY`, do not dispatch** — the spec's own audit says the wave would build against guesses; re-audit (or run the fix loop) until `CODE-GEN READY`, or have the human explicitly override. **Cross-check the credential register (`_provisioning.md`) FIRST, before dispatching** — a task whose `human-prereq` names a credential that is `pending` (or absent from the register) is **not actually ready**: park it upfront with the precise missing credential, rather than dispatching it to discover the block mid-slice and burn a run. (`lint_spec.py` flags this `afk:eligible` + un-provisioned contradiction statically; autorun is the runtime gate.) **Also cross-check the prototype-review gate:** a task with a non-`N/A` `ux` dimension whose prototype is **not frozen (human-reviewed)** and which carries no explicit `prototype-review: waived — <why>` is **not ready** — park it `blocked — visual/UX review pending` rather than letting a JIT-generated, never-seen screen build unattended. (Cadence: freeze every ux-heavy slice queued for the wave in one attended sitting, then dispatch.)
2. **Run the wave in parallel.** Prefer the active host's managed parallel workflow for the whole wave; otherwise use one subagent or headless process (`claude -p` or `codex exec`) per task. Each task runs the full done-gate loop — implement → run the whole gate → self-correct the *code* → repeat until green — honoring the engine's anti-cheat invariants.
3. **Merge, propagate, recompute.** On a task meeting the merge bar (below): merge → run propagation (`impact.py`) → **run the wave-level integration gate** (the system/Tier-B suite after this wave's merges, before launching the next) → recompute the ready wave (dependents now unlocked) → launch the next wave. If the integration gate turns main red, **park the wave** and stop launching. Repeat until no AFK-eligible, dependency-ready task remains.

## Rules
- **The merge bar** — a task merges only when its gate is fully green, the conformance review ran **in a fresh / independent context** (never the implementing loop's own verdict — a loop can't certify itself) with its `VERDICT: PASS` physically on disk under `spec/10-delivery/verification/`, and its Verification Record is green (`python3 scripts/check_task_record.py spec --task T-NNN` exits clean). The artifacts are the proof the bookends ran — "I reviewed it" without them does not count. A task with a back-filled test (an `AC-` without a passing traceability row), a missing/`FAIL` verdict, or an unmet/dropped obligation is **parked, not merged**.
- **The tool-call-time exec-gate enforces every task in the wave, independently** — `gate_exec.py` (red-before-green · no hollow done-claim) is keyed off each task's **`task/T-NNN` branch** and parallel-safe; run each parallel task in **its own branch/worktree**, so the committed hook adapters + `.grillspec/tools/` travel with it. (If you dispatch a task *without* a `task/T-NNN` branch, the implementing agent must `gate_exec.py --start T-NNN` for the gate to engage.)
- **Held-out acceptance criteria (anti-overfitting — the strongest lever)** — to stop an agent implementing *exactly to the visible tests and no further*, **withhold a small subset of each task's `AC-`** from the implementing agent. The mechanism, which you (the orchestrator) own because only you see the full task:
  1. partition the task's `AC-` into **shown** (the bulk) and **held-out** (1–2, or ~20% — pick **black-box, observably-testable** criteria, never ones needing the implementer's internal design);
  2. dispatch the task package **and** its `--init` Verification Record with the held-out `AC-` **stripped** — the implementer TDDs only what it can see;
  3. at the gate, the **independent reviewer** (full task in hand) authors fresh acceptance tests for the held-out `AC-` — or runs the Tier-B system acceptance tests that already cover them — against the built slice;
  4. a held-out `AC-` that **fails** is overfitting/incompleteness → back to implementation (the `AC-` is now revealed, because it must be fixed); all pass → strong evidence the slice generalizes beyond the visible tests.
  The backstop is automatic: `check_task_record.py` regenerates the obligation set from the **frozen full task**, so the held-out `AC-` are required at the gate no matter what the implementer's stripped record showed — they surface as ordinary obligation rows the reviewer must evidence. **Scope:** this is an **AFK/orchestrated-mode** policy (it needs a separate dispatcher and verifier); it's inherently **N/A for a solo `implement-task` run**, where the human reviewer is the independent check. Record the held-out set + their independent result in the Verification Record (a `held-out:` line) so the withholding is itself auditable.
- **Wave-level integration gate** — after each wave's merges, run the system/Tier-B suite before launching the next wave; if main goes red, **park the wave** (stop launching dependents) and report, rather than building on a red main.
- **Keep the credential register live** — when a provisioning-owner task merges (or a human clears a credential ask in `_human-input.md`), flip that credential's row in `_provisioning.md` to `state: provisioned` (+ evidence: where/when), which unlocks the tasks that consume it for the next wave. The register is the single live truth of what's provisioned — never infer provisioned-state from which tasks happened to pass.
- **Don't thrash — park** — a task that hits an anti-cheat wall, a genuine HITL need, the loop's no-converge cap, **or its per-task token/iteration ceiling** → mark it `blocked` with the **precise blocker** (and, for a UX/decision block, a **proposed default for the human to ratify**), and continue with the rest of the wave. The token/iteration ceiling is an explicit park trigger, not a reason to weaken the gate.
- **Parallelism safety** — never parallelize tasks that touch the same files/module (merge-conflict risk) — serialize those; subagents can't share state mid-run. Keep each task one focused slice.
- **Cost** — parallel subagents/headless runs may use a separate host or CI quota — size the wave to the selected host's budget; use the strongest reasoning model for orchestration and a capable faster model for bounded per-task workers.
- **Stop & report** — when the DAG is drained, report **merged** (`T-` ids) · **blocked** (reasons, awaiting human input) · **remaining** (HITL/deferred). Never mark a task done on red; never merge a non-green gate. Code lives in the source tree, never in `spec/`.

## Output
Written under `<working-root>/` (drives the per-task implement → test → conformance loop; merges code on green — code lives in the source tree):

| File / target | Captures | Format |
|---|---|---|
| `<working-root>/autorun-log.md` | the run record: merged (T- ids) · blocked (reason + awaiting-human input · proposed default to ratify) · remaining (HITL/deferred); for each merged task, the **tool-vouched completion report** (`check_task_record.py spec --report T-NNN`) so the whole AFK run is auditable after the fact | — |

(no spec changes)
Consumes: an **implementation-final** spec — tasks derived, `lint_spec` clean, **no task carrying an `UNRESOLVED` gap**. If not, stop and route to the owning upstream area first (don't implement against an ambiguous spec).

## Resources
- `references/exec-engine.md`
- Worked example: `examples.md`
