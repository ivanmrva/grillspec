# derive-data-architecture — worked example

**Upstream (settled):** UC "place order" needs read `by customer, newest-first`; **AGG-Order** (Order→OrderLine, invariant: total = Σ lines); `DATA-006` keep orders 7 years then archive.

Access patterns first, then schema serves them. DDL-sketch (`schema.md`, not code):
```
TABLE order        (order_id PK, customer_id, status, total_cents, placed_at, version INT)
TABLE order_line   (order_id FK→order, sku, qty, unit_cents,  PK(order_id, sku))
INDEX ix_order_customer ON order(customer_id, placed_at DESC)   -- serves the read pattern
```
FKs **within** AGG-Order (order_line→order) only; no FK to `customer` (another aggregate) — that link is by id, consistency via events.

Storage & consistency (`storage.md`):
- engine: PostgreSQL · **consistency: strong** (single-aggregate writes are transactional)
- concurrency: optimistic via `version` column (compare-and-set on update)
- trade-off recorded as `ADR-DATA-002`: strong over bounded-staleness — order totals must never read torn; the few-ms latency cost is acceptable on the write path.

Retention is a **mechanism**, not a sentence (`migration.md`): monthly job moves `placed_at < now()-7y` to cold object storage, then `DETACH PARTITION` drops the hot partition — realising `DATA-006`. Migration is expand→contract: add `version` nullable → backfill → dual-write → enforce NOT NULL → drop old path.

Recorded: schema+indexes for the read pattern, the strong-consistency choice (`ADR-DATA-002`), optimistic concurrency on AGG-Order, the partition-drop retention realising `DATA-006`.
