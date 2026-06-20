---
name: grill-data-reqs
description: >-
  Elicit the non-structural data requirements the logical model doesn't carry — classification, ownership, retention, residency, volume, integrity. Use when you need data governance, not storage design. Loads the shared grill engine.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo
---

# grill-data-reqs

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **Data requirements** — data governance, not storage design.

## Rules
- **group persisted objects into data-classes by how they're governed** (personal · user-private · operational · derived/recomputable · reference · audit · training/feedback/label — ML feature/label sets governed as their own class), then walk each class
- every sensitive class **tagged from {PII · special-category · PHI · PCI cardholder-data · financial · secret/credential}**; a special-category class passes an explicit gate (heightened lawful basis + extra safeguards) before it's allowed at all
- personal/special classes carry a **consent lifecycle**: lawful basis · consent granularity · withdrawal mechanism · re-consent trigger
- **retention = a TTL + a deletion trigger**, never 'a while' ('deleted on \<obligation\>', 'kept ≥N yrs because \<domain reason\>', 'regenerable → N days')
- **residency (where data is physically stored) is split from sovereignty (whose law governs / who can lawfully compel access)** — both set per class
- **lineage/provenance per class** — origin system · derivation · downstream consumers — so a deletion cascade is answerable (delete here, what else must follow)
- volume & growth stated per class (order-of-magnitude + rate) **+ a coarse access-pattern hint** (read/write-heavy · queried-by-what) for the data-architecture design
- integrity stated (immutable/append-only · no-loss/durability); **pick the value-bearing subset of the data-quality dimensions** (accuracy · validity · completeness · integrity · uniqueness · timeliness · consistency · currency) — only those a use depends on
- **`classification`, `retention`, and `residency` are their OWN columns** (headers named exactly that), one typed value per cell — every `DATA-` row carries all three (a value, or `deferred until <trigger>`); a value restated elsewhere (e.g. a retention an obligation re-asserts) must match — one canonical value per class

## Output
**Stable IDs** (bare type prefix, ID = the leading table column / row key): `DATA-` data class.
Written under `requirements/data/`:

| File | Captures | Format |
|---|---|---|
| `data-classes.md` | one row per data category: id DATA-NNN · category · classification tags {PII · special-category · PHI · PCI cardholder-data · financial · secret/credential} · ownership · consent lifecycle (lawful basis · granularity · withdrawal · re-consent trigger) for personal/special · retention (TTL + deletion trigger) · residency · sovereignty · lineage/provenance (origin · derivation · downstream consumers) · volume/growth · access-pattern hint · integrity · data-quality dimensions (value-bearing subset) | — |

ADRs → `adr/ADR-DREQ-NNN.md`
Consumes: the domain aggregates — grouped into governed data-classes, and the domain model's latent retention posture, pinned to a number + trigger.

## Excludes
the logical data model (= the domain aggregates) · schema/storage/partitioning/indexing/cipher

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
