# diagnose — worked example

Illustrative. A "sometimes wrong" bug: invoice totals are occasionally off by one cent.

**Feedback loop.** A property loop generates 10 000 random line-item sets and asserts `sum(lines) == invoice.total`. It fails on about 3% of runs, so the bug is reproducible. Shrinking the failing input gives two lines: `[0.10, 0.20]` should total `0.30` and totals `0.29`.

**Hypotheses**, ranked before testing any:

| # | Hypothesis | Prediction |
|---|---|---|
| 1 | totals are accumulated as binary floats | switching the accumulator to integer cents removes the failure |
| 2 | rounding mode differs between line and total | totals diverge only on `.5` boundaries, not on `0.10 + 0.20` |
| 3 | wrong decimal scale for some currencies | a zero-decimal currency (JPY) fails too |

**Test.** `git bisect run` with the two-line repro narrows the range to one commit, "switch Money to double for speed". That confirms hypothesis 1; the repro is not on a `.5` boundary and JPY passes, which rules out 2 and 3.

**Fix.** A regression test at the totals seam, tagged `@covers AC-052a` (an invoice total equals the sum of its lines), asserts `[0.10, 0.20] → 0.30`. It failed, the accumulator was changed to integer minor units with formatting at the edge, and it passed. The 10 000-run property loop then showed no failures. The temporary `[DEBUG-7c1e]` lines were removed.

**Record.** The cause is structural (nothing stops a float from being used for money) and wrong invoices reached customers, so a record is worth keeping — `12-operate/diagnosis-0091.md`:

| field | value |
|---|---|
| date | 2026-03-04 |
| symptom · repro | invoice totals off by one cent on ~3% of invoices · `[0.10, 0.20] → 0.29` |
| root-cause | money summed as `double`; `0.10` has no exact binary representation |
| fix | integer minor-unit accumulator, formatted at the edge |
| regression-test | `tests/unit/invoice.total.spec.ts` |
| prevention | a fitness function banning float types in the money module; raised as a task |
