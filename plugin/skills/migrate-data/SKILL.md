---
name: migrate-data
description: >-
  Write and run a schema or data migration that touches existing data — forward and rollback, idempotent, online-safe, verified before production. Use for a backfill, a transform, a large-table change, a store move or a production load. Loads the shared exec engine.
disable-model-invocation: true
argument-hint: a schema or data change to migrate
---

# migrate-data

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill evolves a schema or its data without losing data and without stopping the system. Migration code lives in the project's source tree, in the migration home its framework uses.

## When this skill applies
Use it when a `DATA-` or `AGG-` change touches existing data or cannot be one safe additive statement:

- a backfill or transform of live data;
- a change to a large or hot table that must not block;
- a move from one store to another;
- a production initial load from a legacy system.

A purely additive change (a new table, a nullable column) needs none of this: it ships as an ordinary forward migration inside the slice that needs it, through the framework the walking skeleton set up, and `check_migration_real.py` confirms the migration does something. The tier of that slice comes from the engine's risk-tier table.

The skill is not tied to a phase. It runs mid-build for a slice with a hard data change and after launch for a production migration. The migration framework and the first development schema belong to the walking-skeleton task.

## Process
1. **Design it forward and back, in expand → contract steps.** Add the new shape, backfill, write to both, switch reads, and only then remove the old shape. Each step is idempotent, so a re-run after a partial failure is safe, and the deployed code tolerates both shapes for as long as both exist. The contract step ships in a later change than the expand step, because old code may still be running when the expand lands.
2. **Keep it online for a large or hot table.** One blocking statement on such a table is an outage. Backfill in bounded batches with a throttle that pauses on replica lag or load, and change the schema through a non-blocking path: the engine's online DDL, or a shadow-table copy with a cutover. Record the batch size and throttle used.
3. **Verify before production, and again after.** Run against a copy first. Afterwards compare row counts, check referential integrity and spot-check values. For high-value data add a reconciliation of source against migrated rows — a checksum or shadow compare — since counts can match while contents differ.
4. **Get the owner's go where the skill cannot give it.** See the next section.

## Decisions that belong to the data owner
Two moments are the owner's to approve, because they cannot be undone by re-running anything:

| Moment | What is needed |
|---|---|
| destroying data for good (a drop with data, a transform that cannot be reversed) | the data owner ratifies it before the contract step runs. A backup makes the data recoverable; it does not make the deletion authorized. |
| the production cutover (the read switch, or "run it against production now"), even when nothing is destroyed | an explicit owner go, or a cutover policy the owner ratified once. Verification is required first and is not the approval. |

The default to propose for ratification: run automatically in development and staging, ask before the production cutover. Ask through `spec/_human-input.md` as the engine describes, and continue with work that does not depend on the answer.

A migration is not finished while it has a destructive step with no rollback, has not been verified, or has lost data; report it as failed and say what state the data is in.

## Output
| File | Captures | Format |
|---|---|---|
| the migration home in the source tree | the forward and rollback migrations, and the backfill job | code |
| `12-operate/migration-<DATA- or AGG- id>.md` | a short dated record: the change · the forward and rollback plan · the online strategy with batch size and throttle · the verification and its numbers · who approved the cutover · the result and any step still to come | `field \| value` table |
| `adr/ADR-MIG-NNN.md` | a costly-to-reverse migration decision | ADR |

The record is for the operator who later asks what was done to this data and whether the old shape is gone, so keep it to what they need.

Reads: the changed `DATA-` and `AGG-` elements, the data architecture's migration approach where the project has one (`09-solution/data/`), and the current schema and data volumes.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
