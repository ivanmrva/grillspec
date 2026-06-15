# prototype — worked example

One open question, settled by running code instead of arguing.

> **Claude:** Before we commit the architecture: can we price a 50-leg shipping route **under 200ms** at p95? That's the assumption that kills the design if it's wrong — so spike the riskiest one first. This is a **feasibility** question (will it perform), not usability or desirability.
> Branch chosen by the question: a tiny interactive terminal app that pushes the routing rule through the hard cases (50 legs, worst-case fan-out), state surfaced after every run. One command: `python prototypes/route-pricing-latency/run.py`. No persistence, no tests — throwaway.
> Ran the worst case 1 000×: p95 **148ms**, p99 212ms with a memoized leg-cost table; naive recompute was 1.4s. **Answer: feasible** with memoization; the cache shape is load-bearing.

Recorded, then the code deleted (only the answer persists):

- **Question:** feasibility — price a 50-leg route < 200ms p95?
- **Answer:** yes, p95 148ms with a memoized leg-cost cache (naive = 1.4s, fails).
- **Routed to:** the load-bearing latency verdict → an **ADR** (`adr/ADR-PROTO-014.md`); the memoization decision encoded as a reducer snippet inlined into the implementing task's manifest. A bet-status update goes back to the owning area.

(had it been usability, the verdict would route to the UX requirements instead; had it been desirability, it'd be tested with N target users and fed back to discovery. The prototype itself is never shipped.)
