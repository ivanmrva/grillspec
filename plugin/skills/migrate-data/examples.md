# migrate-data — worked example

An online expand-contract migration for `DATA-Order`: split a free-text `address` column into structured fields, no downtime.

> **Claude:** Deployed code must tolerate **both** shapes mid-rollout, so I'll expand first, never drop in the same release.
> **Expand** — add nullable `address_line1/city/postcode` + dual-write trigger (forward); rollback = drop the new columns (reversible, guarded).
> **Backfill** — 4.2M rows, chunked at **batch 5 000**, throttle **pause on replica-lag > 1s**; ran via shadow-table copy + cutover (non-blocking).
> **Verify** — on a prod copy first: counts match (4 204 118 = 4 204 118), FK integrity clean. High-value, so a **checksum shadow-compare** of `md5(address)` vs `md5(concat(line1,city,postcode))` over all rows: 0 mismatches.
> Switch reads → new columns. **Contract** (next release): drop `address` + trigger.

Recorded — `10-operate/migration-DATA-Order.md`:

| field | value |
|---|---|
| change | `DATA-Order.address` → structured `line1/city/postcode` |
| forward + rollback | expand (add cols + dual-write) ↔ drop new cols |
| online strategy | shadow-table + cutover · **batch 5 000** · throttle on replica-lag>1s |
| verification | counts equal · FK clean · **checksum shadow-compare 0 mismatches** |
| result | reads switched · contract step queued for next release |

(migration CODE lives in the project source tree at `src/migrations/`, never `spec/`. The contract step is a separate landed change so no schema drops while old code may still run.)
