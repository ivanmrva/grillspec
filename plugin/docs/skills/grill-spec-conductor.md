# Spec conductor — user guide

**Invoke:** `/grillspec:grill-spec-conductor` in Claude Code or `$grillspec:grill-spec-conductor` in Codex — or just describe a spec task; it is model-invocable.

*The orchestrator — the one skill that knows the whole system. The 46 worker skills know nothing about it.*

## What it does
START HERE to spec, design, plan, or build a project or feature end-to-end — the front door and orchestrator for the whole idea-to-spec-to-code-to-operate workflow. It scans the spec, re-derives the current state, and routes to the next area; owns the dependency order, readiness gates, and cross-area consistency. Prefer it over any single grill-/derive-/exec- skill whenever work spans more than one area.

## When to use it
When you want the full system to drive end to end. It picks the next area, **hands each worker its input and its exact target slot** in the `spec/` tree, then reads each worker's output to reconcile cross-area views, runs the linter + derived-guard, checks cross-area consistency, and propagates changes downstream. Use a worker skill directly instead when you only want one artifact.

## What it needs
A working repo. On start it runs the linter, scans the tree, and offers a **menu of next actions** (recommended next area, resume, fix cross-area issues, test the riskiest assumption, …). It never starts an area you didn't pick.

## How to run it
Use `/grillspec:grill-spec-conductor` in Claude Code or `$grillspec:grill-spec-conductor` in Codex, then choose from the menu — or state your goal and let it route.

## How to tell it did its job  *(verification)*
- It never silently starts an area you didn't choose.
- The linter (`lint_spec.py`) is green; the derived-guard blocks hand-edits to generated artifacts.
- The three gates (architecture-, implementation-, delivery-readiness) are respected, not skipped.
- The `spec/` tree stays stage-pure (one leaf folder per skill) and cross-area references resolve.
