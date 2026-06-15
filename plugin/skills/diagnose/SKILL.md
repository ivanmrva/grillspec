---
name: diagnose
description: >-
  Disciplined diagnosis loop for hard bugs and performance regressions — build a fast deterministic feedback loop, reproduce, rank falsifiable hypotheses, instrument one variable at a time, fix with a regression test, post-mortem. Use when a hard bug or regression needs root-causing, not a quick patch. Loads the shared exec core.
disable-model-invocation: true
argument-hint: a bug or performance regression to diagnose
---

# diagnose

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill: **diagnose hard bugs & regressions** via a disciplined, instrumented loop — not a quick patch.

## Process
1. **Build a feedback loop (THIS is the skill).** Get a fast, deterministic, agent-runnable **pass/fail signal** for the bug — everything else just consumes it. Try, roughly in order: a failing test at the right seam · curl/HTTP against a dev server · CLI + fixture diffed vs known-good · headless-browser script · replay a captured trace · a throwaway harness · a **property/fuzz loop** for 'sometimes wrong' · a **bisection** harness (`git bisect run`) · a **differential** loop (old vs new) · HITL bash (last resort). **Minimize the repro:** shrink the failing input (delta-debug / cut it down) and the suspect **commit range** to the **smallest case that still fails** — a small deterministic repro is worth more than a faithful big one. For a bug that only reproduces in prod, build a **production observability-driven** path instead: drive the signal from high-cardinality traces/events (filter to the failing requests by id/attributes) until you can see the failing path. Iterate the loop to be faster, sharper, more deterministic. For non-deterministic bugs, **raise the reproduction rate** (loop 100×, parallelise, stress, inject sleeps) until debuggable. If you genuinely can't build one, **stop and say so** — list what you tried; don't hypothesise blind.
2. **Reproduce.** Run the loop; confirm it's the **user's** failure mode (not a nearby one) and you've captured the exact symptom.
3. **Hypothesise.** Generate **3–5 ranked, falsifiable** hypotheses *before* testing any ('if X is the cause, changing Y makes it disappear'). Show the ranked list to the user (they often re-rank instantly); proceed if AFK.
4. **Instrument.** Each probe maps to one prediction; **change one variable at a time**; prefer a debugger/REPL over logs; **tag every debug log with a unique prefix** (`[DEBUG-a4f2]`) so cleanup is one grep. Perf branch: **measure first** (baseline + profiler/query-plan), then bisect — logs are usually wrong for perf.
5. **Fix + regression test.** Write the regression test **before** the fix **iff a correct seam exists** (one that exercises the real bug pattern at the call site). **If no correct seam exists, that IS the finding** — the architecture is preventing lockdown → flag it. Otherwise: failing test → watch fail → fix → watch pass → re-run the Phase-1 loop on the original scenario.
6. **Cleanup + post-mortem.** Original repro gone · regression test passing (or absent-seam documented) · all `[DEBUG-…]` removed (grep) · throwaway harnesses deleted · the correct hypothesis stated in the commit/MR. **Then ask: what would have prevented this?** If architectural (no test seam, tangled callers, hidden coupling) → flag it for the conformance review's design-health lens with specifics (after the fix, not before).

## Rules
- Code lives in the source tree, never in `spec/`.

## Output
Written under `10-delivery/operations/`:

| File / target | Captures | Format |
|---|---|---|
| `10-delivery/operations/diagnosis-<id>.md` | diagnosis record: repro · hypotheses tried · root cause · the fix + regression test · prevention note (→ conformance review) | — |

(the code fix + regression test → project source tree, never spec/)
(+ ADRs → `adr/ADR-DIAG-NNN.md`)
Consumes: the work item this skill operates on, plus the spec IDs / code it references.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
