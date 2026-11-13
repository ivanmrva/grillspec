# derive-data-architecture — worked example

Illustrative: it shows the shape, not required content.

Upstream: "place order" reads orders by customer, newest first; `AGG-Order` (Order → OrderLine); `DATA-006` keeps orders 7 years, then archives; `DATA-009` marks the delivery address as PII.

## Decision mode (`standard`) — `storage.md`

| Store | Technology | Consistency | Concurrency control | Tenancy isolation |
|---|---|---|---|---|
| orders | PostgreSQL | strong | optimistic, `version` column | row-level, `tenant_id` on every table |

| Data class | Retention mechanism | PII treatment |
|---|---|---|
| DATA-006 orders | monthly partitions; archive to cold storage, then drop the partition at 7 years | — |
| DATA-009 delivery address | follows its order | column-level encryption |

Migration approach: expand, backfill, then contract, each in its own release.

`ADR-DATA-002` records strong over bounded-staleness: an order total must never read torn, and the few-millisecond cost on the write path is acceptable.

## Full mode (`regulated`) adds

`schema.md`, a DDL sketch that serves the read pattern:
```
TABLE order      (order_id PK, customer_id, status, total_cents, placed_at, version INT)
INDEX ix_order_customer ON order(customer_id, placed_at DESC)
```
Foreign keys stay inside `AGG-Order`; the link to the customer is by id. `migration.md` spells out the steps and the archival job.
