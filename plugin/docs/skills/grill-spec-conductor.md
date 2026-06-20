# Spec conductor — user guide

**Invoke:** `/grillspec:grill-spec-conductor` — or just describe a spec task; it is model-invocable.

*The orchestrator — the one skill that knows the whole system. The 45 worker skills know nothing about it.*

## What it does
START HERE to spec, design, model, plan, or build a project, product, or feature end-to-end — the single front door and orchestrator for the whole idea-to-spec-to-architecture-to-tasks-to-code-to-operate workflow. Use when starting from an idea or from scratch, when the scope is the whole project rather than one area, or when you don't know which step you need: it scans the spec, re-derives the current state, and recommends or asks which area to work next. Owns the cross-area dependency order, the readiness gates, the global glossary/actors and consistency, the discovery/validation overlay, the pivot loop, and the lite path. Prefer this over any individual grill-, derive-, or exec- skill whenever the work spans more than one area. Run this first.

## When to use it
When you want the full system to drive end to end. It picks the next area, **hands each worker its input and its exact target slot** in the `spec/` tree, then reads each worker's output to reconcile cross-area views, runs the linter + derived-guard, checks cross-area consistency, and propagates changes downstream. Use a worker skill directly instead when you only want one artifact.

## What it needs
A working repo. On start it runs the linter, scans the tree, and offers a **menu of next actions** (recommended next area, resume, fix cross-area issues, test the riskiest assumption, …). It never starts an area you didn't pick.

## How to run it
`/grillspec:grill-spec-conductor`, then choose from the menu — or state your goal and let it route.

## How to tell it did its job  *(verification)*
- It never silently starts an area you didn't choose.
- The linter (`lint_spec.py`) is green; the derived-guard blocks hand-edits to generated artifacts.
- The three gates (architecture-, implementation-, delivery-readiness) are respected, not skipped.
- The `spec/` tree stays stage-pure (one leaf folder per skill) and cross-area references resolve.
