---
name: derive-data-architecture
description: >-
  Decide how the system stores data — store technology, consistency, concurrency control, tenancy isolation, retention enforcement, PII treatment — and at the regulated profile also design the schema, read models and migration. Use when the data requirements and domain model exist.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# derive-data-architecture

**Load `references/derive-engine.md` first and follow it.** This skill applies that method to the **data architecture**: how the system stores, isolates, retains and migrates its data.

## Depth by profile
How much is written follows the project's profile:

| Profile | Mode | Written |
|---|---|---|
| `lite` | N/A | nothing here — the store and tenancy decisions are rows in `arch/solution-strategy.md`, the rest is in the conventions |
| `standard` | decision mode | `storage.md` |
| `regulated` | full mode | `storage.md` plus `schema.md`, `read-models.md`, `migration.md` |

Decisions live in the spec; the description lives in the artifact that enforces it — here the schema and its migrations — and once code exists that artifact is the source of truth for the description. Decision mode therefore records only what the code cannot explain and is costly to reverse (which store, how consistent, how isolated, how data is retained and protected); full mode also writes the table-by-table design, because at `regulated` the document is itself a deliverable that auditors and other teams read.

## Method
Start from the access patterns: the reads and writes the use-cases and read models need. They decide the store, its consistency level and, in full mode, the indexes. A design that starts from the tables serves queries nobody runs.

## Decision record
`storage.md` is written in both modes and carries:
- per store: technology · consistency level · concurrency control · tenancy isolation;
- where the product has them: partitioning/sharding · an event store · cache coherence (strategy · invalidation trigger · staleness bound);
- per `DATA-` class: the retention-enforcement mechanism and the field-level PII treatment (encryption/tokenisation);
- the migration approach, in one line.

## Rules
- Each store declares its consistency level (strong · bounded-staleness · eventual). The latency-versus-consistency trade-off is an ADR, because it is the choice a reader cannot recover from the code.
- A design with more than one store engine records a polyglot-persistence ADR that maps each access pattern to the engine that fits it.
- Retention is a mechanism (TTL, partition drop, archival job) that realises a `DATA-` retention trigger. The period itself comes from the data requirements; one that is missing there is a gap to record, not a value to choose here.
- The tenancy isolation model (row · schema · database) is a ratify-point when the data requirements leave it open.

## Output
Written under `solution/data/`. The rows marked `full` are written only at `regulated`; in decision mode their content is not raised.

| File | Mode | Captures | Format |
|---|---|---|---|
| `storage.md` | decision | the decision record above | table, one row per store · table keyed on the `DATA-` class for retention and PII · one line for migration |
| `schema.md` | full | logical → physical schema per aggregate or data class · indexes designed for the access patterns · referential integrity (foreign keys within an aggregate, none across; a cross-aggregate link is by id) | tables / DDL sketch, not code |
| `read-models.md` | full | where CQRS is used, each projection: source events · rebuild strategy · staleness window. It may instead be a literal `## Read models` section of `schema.md`, so consumers still have one place to look; without CQRS it is omitted | per projection: source events · rebuild · staleness |
| `migration.md` | full | the zero-downtime procedure (expand → backfill → dual-write/shadow-read → verify → contract) and the per-field detail of the retention and PII mechanisms `storage.md` decides | migration steps · retention jobs · PII fields |

ADRs → `adr/ADR-DATA-NNN.md`
Consumes: the data requirements (including the `DATA-` retention triggers, residency and tenancy) · the domain model's aggregates and invariants · the use-cases' read/write access patterns.

## Excludes
application code · in decision mode, the table and index design (the schema and migrations in code state it)

## Resources
- `references/derive-engine.md`
- Worked example: `examples.md`
