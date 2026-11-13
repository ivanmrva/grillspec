# migrate-data — worked example

Illustrative. `DATA-Order` splits a free-text `address` column into structured fields, on a 4.2 million-row table, with no downtime.

**Plan.** The deployed code must work with both shapes while the rollout is in progress, so the old column is not dropped in the same release.

| Step | Forward | Rollback |
|---|---|---|
| expand | add nullable `address_line1`, `city`, `postcode`; write to both shapes | drop the three columns |
| backfill | batches of 5 000 rows, paused while replica lag exceeds 1 s | none needed; the old column is untouched |
| switch reads | read the new columns | read the old column again |
| contract (next release) | drop `address` and the dual write | not reversible — needs the data owner's approval |

**Verification, on a copy of production first.** Row counts match (4 204 118 on both sides) and foreign keys are intact. Because order addresses are high-value, every row was also reconciled: a checksum of the old `address` against the concatenated new fields, with no mismatches.

**Approval.** The data owner approved the production cutover after seeing the verification numbers. The contract step is queued as its own change and will be put to the owner separately, since it deletes the old column for good.

Record — `12-operate/migration-DATA-Order.md`:

| field | value |
|---|---|
| date | 2026-05-11 |
| change | `DATA-Order.address` → `address_line1` · `city` · `postcode` |
| forward · rollback | expand and dual-write · drop the new columns |
| online strategy | batches of 5 000, throttled on replica lag over 1 s |
| verification | counts equal · foreign keys intact · checksum reconcile, 0 mismatches |
| cutover approved by | the data owner |
| result | reads switched to the new columns; contract step pending in the next release |
