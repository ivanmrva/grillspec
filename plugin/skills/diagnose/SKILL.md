---
name: diagnose
description: >-
  Diagnose a hard bug or performance regression with a disciplined loop — a fast deterministic pass/fail signal, ranked falsifiable hypotheses, one variable at a time, a fix with a regression test. Use when a quick patch has not found the cause. Loads the shared exec engine.
disable-model-invocation: true
argument-hint: a bug or performance regression to diagnose
---

# diagnose

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill finds the cause of a hard bug or regression through an instrumented loop instead of a guess-and-patch. The fix itself is a `routine` change in the engine's terms: a failing test first, tagged `@covers` the acceptance criterion the bug violated, then the fix, then the gate.

## Process
The steps depend on each other, so take them in order.

1. **Build a feedback loop.** This step is most of the skill: a fast, deterministic pass/fail signal for the bug that you can run yourself. Everything after it only consumes that signal. Options, roughly from cheapest to most involved:
   - a failing test at the right seam;
   - a request against a dev server, or a CLI run with a fixture diffed against known-good output;
   - a headless-browser script, or a replay of a captured trace;
   - a property or fuzz loop for a "sometimes wrong" result;
   - a bisection harness (`git bisect run`) or a differential run of old against new;
   - a human running a command for you, when nothing else reaches the failure.

   Then make the loop smaller and sharper. Shrink the failing input and the suspect commit range to the smallest case that still fails; a small deterministic repro is worth more than a faithful large one. For a flaky bug, raise the failure rate (loop it, run in parallel, add load, inject delays) until it fails often enough to work with. For a bug that appears only in production, drive the signal from traces and events filtered to the failing requests until the failing path is visible.

   If no loop can be built, stop and say what you tried. Hypotheses without a signal to test them are guesses.
2. **Reproduce.** Run the loop and confirm it shows the failure the user reported, with the exact symptom, and not a neighbouring one.
3. **Hypothesise.** Write three to five ranked, falsifiable hypotheses before testing any, each with its prediction ("if X is the cause, changing Y makes it disappear"). Show the list to the user when one is present, since they can often re-rank it at a glance; in an unattended run, proceed.
4. **Instrument.** One probe per prediction, one variable changed at a time. A debugger or REPL usually tells more than log lines. Give every temporary log line one unique prefix (`[DEBUG-a4f2]`) so removing them is a single search. For a performance problem, measure first — a baseline plus a profiler or query plan — and then bisect; timing logs mislead.
5. **Fix, with a regression test.** Write the test before the fix when a correct seam exists: one that exercises the real bug pattern where it occurs. Watch it fail, apply the fix, watch it pass, then run the step-1 loop on the original scenario. If no correct seam exists, that is itself the finding — the structure prevents the bug from being locked down — so report it instead of forcing a test onto the wrong seam.
6. **Clean up and close.** The original repro no longer fails, the regression test passes (or the missing seam is reported), every `[DEBUG-…]` line and throwaway harness is gone, and the commit message states the cause that was confirmed. Then ask what would have prevented the bug. If the answer is structural — no test seam, tangled callers, hidden coupling — name it specifically as a design-health candidate for the next conformance review, or as a task of its own.

## Output
The fix and its regression test go into the project's source and test trees.

A diagnosis record is written only when someone will read it later: the bug caused or followed a production incident, it is likely to recur, or the cause is structural. An ordinary bug is fully recorded by its regression test and commit message.

| File | Captures | Format |
|---|---|---|
| `12-operate/diagnosis-<id>.md` | the symptom and minimal repro · the hypotheses and which one held · `root-cause:` · `fix:` (or `absent-seam:` with why the bug could not be locked down) · `regression-test:` path · what would have prevented it | a short `field \| value` table, dated |
| `adr/ADR-DIAG-NNN.md` | a costly-to-reverse decision the diagnosis forced | ADR |

Reads: the report of the bug, the code and spec passages it concerns.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
