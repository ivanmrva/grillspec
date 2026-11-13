---
name: grill-data-reqs
description: >-
  Elicit how each class of data is governed, which the domain model does not say: classification,
  retention and deletion trigger, residency, tenancy and ownership. Use when you need data
  governance decisions, not storage design.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo
---

# grill-data-reqs

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **Data requirements** — data governance, not storage design.

## Depth by profile
| Profile | What the interview captures |
|---|---|
| `lite` | not a separate area. |
| `standard` | per data class: classification, retention with its deletion trigger, residency, and tenancy. Personal and special-category classes add their consent lifecycle. Any other field is written only where a decision depends on it. |
| `regulated` | every field listed under Output, for every class. |

## Rules
- Group the persisted objects into data classes by how they are governed (personal · user-private · operational · derived/recomputable · reference · audit · training/feedback/label), then walk each class. ML feature and label sets are a class of their own.
- Tag every sensitive class from {PII · special-category · PHI · PCI cardholder-data · financial · secret/credential}. A special-category class needs a stated lawful basis and extra safeguards before it is allowed at all.
- Personal and special classes carry a consent lifecycle: lawful basis · consent granularity · withdrawal mechanism · re-consent trigger.
- Retention is a TTL plus a deletion trigger ("deleted on <obligation>", "kept ≥ N years because <domain reason>", "regenerable → N days"). State the trigger precisely enough to test, because the task that builds the deletion path exercises it; otherwise the retention is a promise nothing implements.
- Tenancy names the isolation boundary (per user · per tenant · shared) and ownership names who answers for the class.
- Residency (where the data is physically stored) is separate from sovereignty (whose law governs it and who can lawfully compel access). Take the operating footprint from the compliance area where it is confirmed there. A footprint or retention value that is a fresh call is the user's to ratify.
- Lineage names the origin, the derivation and the downstream consumers, using the `AGG-` or `DATA-` id wherever one is modelled, so a deletion cascade can be answered from the spec.
- Volume and growth are an order of magnitude and a rate, with a coarse access-pattern hint (read- or write-heavy, queried by what) for the data-architecture design.
- Integrity states immutability and durability (append-only · no-loss). Of the data-quality dimensions (accuracy · validity · completeness · integrity · uniqueness · timeliness · consistency · currency), record only those a use depends on.

## Output
**IDs:** `DATA-` data class.
Written under `requirements/data/`:

| File | Captures | Format |
|---|---|---|
| `data-classes.md` | every governed data class | a table with one row per class, then a short section per class that has more to say |

The table columns are `DATA-` id · category · `classification` · `retention` · `residency` · tenancy · ownership. The headers `classification`, `retention` and `residency` are written exactly so, with one typed value per cell (a value, or `deferred until <trigger>`), because the consistency check reads them from the row. A value restated elsewhere, such as a retention an obligation repeats, must match: one canonical value per class.

A class's section is headed by its `DATA-` id and holds what does not fit a cell: consent lifecycle · sovereignty · lineage · volume, growth and access pattern · integrity · data-quality dimensions.

ADRs → `adr/ADR-DREQ-NNN.md`
Consumes: the domain aggregates, grouped into governed data classes, and the domain model's latent retention posture, pinned here to a number and a trigger.

## Excludes
the logical data model (= the domain aggregates) · schema/storage/partitioning/indexing/cipher

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
