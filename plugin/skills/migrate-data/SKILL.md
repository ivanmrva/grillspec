---
name: migrate-data
description: >-
  Generate and run the schema/data migration a DATA-/AGG- change requires — forward + rollback, idempotent, online-safe, verified. Mandatory whenever the data model changes. Loads the shared exec core.
disable-model-invocation: true
argument-hint: a schema or data change to migrate
---

# migrate-data

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill: **migrate data (schema/data evolution)** — forward + rollback, idempotent, online-safe, verified.

## Process
1. **Produce forward + rollback, online-safe.** Make it **idempotent** using **expand-contract** (add the new shape → backfill → dual-write/read → switch reads → contract; no destructive step without a guarded, reversible path), and sequence it so the deployed code tolerates **both** schemas mid-rollout.
2. **Large-table / online strategy.** For a big table or hot path, don't run one blocking statement: **chunk + throttle** the backfill (bounded batches, pause on replica-lag/load) and take an **online-schema-change path** (shadow-table copy + cutover, or the engine's non-blocking DDL). Record the **batch size + throttle** used.
3. **Verify before prod.** Run against a copy first; **validate after** — row counts, referential integrity, spot-checks. For high-value data, add a **reconciliation method** — a **checksum / shadow-compare** of source vs migrated rows — not just counts + spot-checks. Migration code lives in the **project source tree** (e.g. `src/migrations/`), never `spec/`.

## Rules
- **Trigger / scope** — fires when a `DATA-`/`AGG-` change **touches existing data or can't be a single safe additive DDL**: a backfill/transform of live data · an online-safe change to a large/hot table · a store-to-store move · a **production initial load** from a legacy source. A **trivial additive** change (a new table · a nullable column) instead **rides inside its feature slice** — the slice ships its own forward migration via the framework the walking-skeleton stood up; the conformance review still **requires that migration to exist**.
- **A stage-agnostic capability, not a phase** — runs **mid-build** for a complex data slice and **day-2** for a production data migration. The **migration framework + the initial dev schema** belong to the **walking-skeleton** task; only a **production** initial load/seed from an existing system is itself a migrate-data job.
- **intended irreversible data destruction is owner-ratified, not auto-run** — when a change deletes data for good (a drop-with-data, a non-reversible transform), the **data owner ratifies it before the contract step runs**; a backup makes it recoverable, not authorized
- **Never pass on:** a destructive migration with no rollback · an unverified migration · data loss.
- Code lives in the source tree, never in `spec/`.

## Output
Written under `10-delivery/operations/`:

| File / target | Captures | Format |
|---|---|---|
| `10-delivery/operations/migration-<DATA\|AGG-id>.md` | migration record: the change · forward + rollback plan · online strategy (batch size + throttle) · verification (counts + integrity; checksum/shadow-compare for high-value data) · result | — |

(migration CODE → project source tree, never spec/)
(+ ADRs → `adr/ADR-MIG-NNN.md`)
Consumes: the changed `DATA-`/`AGG-` IDs + `09-solution/data/` (the data architecture, incl. its migration approach) + the current schema/state.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
