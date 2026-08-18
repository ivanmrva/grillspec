---
name: derive-data-architecture
description: >-
  Design schema, storage, consistency, partitioning and migration from the data requirements and domain model. Use when the data requirements and domain model exist and you need schema/storage/consistency/migration designed. Loads the shared derive engine.
disable-model-invocation: true
argument-hint: a recorded spec or design docs
---

# derive-data-architecture

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md` first and follow it.** This skill applies that method to **Data architecture** — schema, storage, consistency, partitioning and migration.

## Method
1. **access patterns first** (reads/writes from UCs + read-models), then per aggregate: storage + logical→physical schema + indexes designed to serve them
2. where CQRS is used: **read-model/projection** design (projection source-events · rebuild strategy · staleness/consistency window)
3. consistency (storage-level + per-aggregate concurrency control)
4. partitioning/sharding
5. migration/cutover

## Rules
- each store declares its **consistency level** (strong / bounded-staleness / eventual) + the latency-vs-consistency trade-off as an ADR; multi-store designs record a **polyglot-persistence** ADR (access pattern → engine fit)
- everything else the output rows enumerate (integrity, retention mechanism, tenancy, PII, expand-contract) is designed there, once

## Output
Written under `solution/data/`:

| File | Captures | Format |
|---|---|---|
| `schema.md` | logical→physical schema (tables / DDL-sketch, not code) per aggregate/data-class + indexes designed for the access patterns + referential integrity (FKs within an aggregate, none across) | tables / DDL-sketch · not code |
| `read-models.md` | where CQRS is used: each projection — source-events · rebuild strategy · staleness/consistency window. May merge into `schema.md` ONLY under a literal `## Read models` heading (a findable section, so downstream consumers and the audit have one place to look); absent CQRS, the file is omitted | per-projection: source-events · rebuild · staleness |
| `storage.md` | per store: technology · **consistency level** (strong/bounded-staleness/eventual) · concurrency control · partitioning/sharding · multi-tenancy isolation (row/schema/db) · event store (if event-sourced) · **caching coherence** (strategy · invalidation trigger · staleness bound) | per-store typed: tech · consistency · partitioning · cache coherence |
| `migration.md` | zero-downtime migration — expand→contract **plus backfill + dual-write/shadow-read + verification** + retention enforcement (TTL/partition-drop/archival realising the DATA- triggers) + field-level PII (encryption/tokenisation) | migration steps · retention mechanism · PII fields |

ADRs → `adr/ADR-DATA-NNN.md`
*(DERIVED & regenerate-only — never hand-edited)*
Consumes: the data requirements (incl. `DATA-` retention triggers, residency, tenancy) + the domain model's aggregates/invariants + the use-cases' read/write access patterns.

## Excludes
application code

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md`
- Worked example: `examples.md`
