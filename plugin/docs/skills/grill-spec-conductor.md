# Spec conductor — user guide

**Invoke:** `/grillspec:grill-spec-conductor` in Claude Code or `$grillspec:grill-spec-conductor` in Codex — or just describe a spec task; it is model-invocable.

*The orchestrator — the one skill that knows the whole system. The 43 worker skills know nothing about it.*

## What it does
START HERE to spec, design, plan, or build a project or feature end to end. The front door and orchestrator: it reads the spec, works out the current state, recommends the smallest next step, and runs the chosen area. Use it whenever work spans more than one area.

## When to use it
When you want the full system to drive end to end. It picks the next area, **hands each worker its input and its exact target slot** in the `spec/` tree, then reads each worker's output to reconcile cross-area views, runs the linter, checks cross-area consistency, and propagates a change to what depends on it. Use a worker skill directly instead when you only want one artifact.

## What it needs
A working repo. On the first session it asks for the project's profile and delivery mode and recommends the smallest profile that fits. On start it runs the linter, scans the tree, and offers a **menu of next actions** (recommended next area, resume, fix cross-area issues, test the riskiest assumption, …). It never starts an area you didn't pick.

## How to run it
Use `/grillspec:grill-spec-conductor` in Claude Code or `$grillspec:grill-spec-conductor` in Codex, then choose from the menu — or state your goal and let it route.

## How to tell it did its job  *(verification)*
- It never silently starts an area you didn't choose.
- The linter (`lint_spec.py`) is green, including the profile and timeless checks.
- It recommends the smallest next step and offers optional areas only when asked.
- The readiness gates (architecture, implementation, delivery) are respected and count only in-profile areas.
- The `spec/` tree stays one leaf folder per skill and cross-area references resolve.
