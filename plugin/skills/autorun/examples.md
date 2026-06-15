# autorun — worked example

Driving the coding phase AFK across the task DAG: select the ready wave, run it in parallel, each task runs its full done-gate loop, merge on green, propagate, recompute. The spec is implementation-final (tasks derived, lint clean, no task carrying an unresolved gap) — the precondition to even start.

**Wave 2** ready: `depends:` all merged, each `afk: eligible`. T-014 and T-016 touch different modules (Scheduling vs Billing) → safe to parallelize; T-018 also touches Scheduling/job → **serialized after T-014** (same files = merge-conflict risk).

Each task self-corrects its *code* to green (never the goalposts; never disables a gate). On a green gate the merge is gated by a conformance review **run in a fresh, independent context** — a loop can't certify itself — against a small held-out AC subset the implementing agent never saw.

## Output — `autorun-log.md`

```
WAVE 2  (2026-06-15)
  merged:
    T-014 reschedule-job   gate green → conformance VERDICT: PASS (independent ctx) → merged
    T-016 refund-payment    gate green → conformance VERDICT: PASS (independent ctx) → merged
  parked:
    T-018 notify-on-reschedule
      reason: HITL — UX decision: should a customer already SMS-confirmed be re-notified
              on a slot move, or silently updated? No invariant decides it.
      proposed default (for human to ratify): re-notify only when new slot moves the
              appointment day; otherwise silent update. Blocked, not guessed.
  post-wave integration gate (Tier-B, after merges): journey + fitness fns + contract
      suite GREEN on main → safe to launch Wave 3.
  next wave recomputed: T-020, T-021 now unlocked (depended on T-014/T-016).
```

If the integration gate had turned main red, the wave is **parked** and no dependents launch — never build on a red main. Drain-time report: **merged** T-014, T-016 · **blocked** T-018 (awaiting the ratified default) · **remaining** Wave 3 (T-020, T-021).
