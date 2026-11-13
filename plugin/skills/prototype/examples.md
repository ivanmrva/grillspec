# prototype — worked example

Illustrative. One open question, settled by running code.

**Question.** Before the architecture is committed: can a 50-leg shipping route be priced in under 200 ms at p95? If not, the design does not hold, so this is the assumption to test first. It is a feasibility question.

**Spike.** A small terminal app under `prototypes/route-pricing-latency/` that pushes the pricing rule through the worst case (50 legs, maximum fan-out) and prints timings after every run. One command: `python prototypes/route-pricing-latency/run.py`. No persistence, no tests.

**Result.** Over 1 000 worst-case runs, a naive recompute takes 1.4 s. With a memoized leg-cost table, p95 is 148 ms and p99 is 212 ms.

**Answer.** Feasible, and only with memoization: the cache shape is load-bearing.

**Where it went.**

| Answer | Recorded in |
|---|---|
| the latency verdict and the memoization decision | `adr/ADR-PROTO-014.md` |
| the leg-cost cache shape | the design note of the task that implements route pricing |

The spike was then deleted. Had the question been about usability, the verdict would have gone to the UX requirements; had it been about desirability, it would have been tested with target users and fed back to discovery.
