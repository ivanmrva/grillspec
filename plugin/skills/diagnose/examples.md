# diagnose — worked example

A "sometimes wrong" bug: invoice totals occasionally off by one cent.

> **Claude:** Built a fast deterministic signal first — a property loop generating 10 000 random line-item sets, asserting `sum(lines) == invoice.total`. Fails ~3% of runs → reproducible. **Minimized** the failing input to two lines: `[0.10, 0.20]` → expected `0.30`, got `0.29`.

**Three ranked, falsifiable hypotheses** (shown before testing any):
1. *Float accumulation* — totals summed as IEEE-754 floats. → If true, switching the accumulator to integer cents makes it vanish.
2. *Rounding-mode mismatch* — half-even vs half-up at line vs total. → If true, totals diverge only on `.5` boundaries (not `.10/.20`).
3. *Currency-scale off-by-one* — wrong decimal places per currency. → If true, JPY (0-decimal) also fails.

> **Bisect** narrowed the suspect range to one commit: `git bisect run` flagged `a91f3` "switch Money to double for speed" — confirms **H1**, rules out H2/H3. **Fix:** accumulate in integer minor units, format at the edge. Regression test written **at the totals seam first**: `[0.10,0.20]→0.30` → watched it fail → applied fix → watched it pass → re-ran the 10 000× property loop, 0 failures.

Recorded — `12-operate/diagnosis-0091.md`:

| field | value |
|---|---|
| repro | property loop 10 000× (~3% fail), minimized to `[0.10,0.20]→0.29` |
| hypotheses | H1 float-accum (✓ via bisect to `a91f3`) · H2 rounding-mode · H3 currency-scale |
| root cause | money summed as `double`; binary float can't represent `0.10` |
| fix + regression | integer-cents accumulator · seam test `[0.10,0.20]→0.30` |
| prevention → conformance review | ban float for money — add a lint/ASR; flagged for the design-health lens |

(the fix + regression test land in the project source tree, never `spec/`; all `[DEBUG-…]` probes grepped out.)
