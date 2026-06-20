# audit-spec — worked example

A mid-build spec for a subscription billing product. The user runs `audit-spec` (default `--depth full`).

## Phase 0 — mechanical baseline
```
lint_spec.py   → 0 errors, 6 warnings (3 coverage, 2 ADR-status, 1 dense-prose)
spec_status.py → 41 UC / 38 with AC (93%) · 0 unresolved task GAPs · 2 afk:blocked
guard_derived  → clean (no derived zone hand-edited)
```
The 0 ERRORs means structure is sound — so the audit is now entirely about meaning. The 6 WARNs become
`important` candidates to confirm, not findings to restate.

## Phase 1 — consistency judgment (a real contradiction the linter cannot see)
Both files resolve every ID; neither dangles. But:
- `06-requirements/data/retention.md` — `DATA-014 Invoice` → retention **7 years**.
- `06-requirements/compliance/obligations.md` — `OBL-003` (the same invoice data) → "purge after **24 months**".

→ `blocking · consistency · DATA-014 vs OBL-003 · contradictory retention (7y vs 24mo) for the same data ·
route: reconcile in the authored requirements (data + compliance), then re-derive data-architecture.`

Also flagged: a "performance NFR" `NFR-022` that is really an obligation (it restates a regulatory SLA) →
`important: type-correctness — should be an OBL-, supersede don't rename.`

## Phase 3 — domain completeness (a MISSING branch nothing mechanical could find)
Blind re-derivation of the billing domain lists the dunning lifecycle: trial → active → **past-due** →
**grace** → **suspended** → **cancelled** → **reactivated**. The ddd models `Subscription` with only
active / cancelled. Diff:

→ `important · domain-coverage · 04-domain/ddd · Subscription has no past-due/grace/suspended/reactivated
states — the entire failed-payment dunning branch is unmodeled (no UC, no AC, no task can exist for it) ·
route: re-grill ddd (then the functional spec, quality, etc. propagate).`

Edge-generator pass adds: `important · proration on mid-cycle plan change is unspecified (money/partial) —
needs-domain-validation against the billing rules.`

## Verdict (written to `spec-audit-report.md` at project root)
```
CODE-GEN READINESS: NOT-READY  (2 blocking, 5 important)
  architecture-readiness gate: NOT MET — DATA-014/OBL-003 contradiction is upstream of the solution
Top fixes (dependency order):
  1. reconcile DATA-014 vs OBL-003 retention            (authored: data + compliance)
  2. model the dunning lifecycle on Subscription        (re-grill ddd → propagate)
  3. specify mid-cycle proration                        (re-grill quality/ddd; or a throwaway spike)
```
The same spec in `--depth consistency` would have stopped at finding #1 and reported
`CONSISTENT (domain not assessed)` — it may not issue a readiness verdict, precisely so a clean
consistency pass is never mistaken for "the right thing is specified."
