---
name: grill-quality
description: >-
  Turn vague quality wishes into measurable NFR scenarios, walking a standard quality-attribute tree so no dimension is missed, and tag the architecturally-significant ones (ASRs). Use when you need measurable NFRs with the significant ones flagged. Loads the shared grill engine.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo
---

# grill-quality

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **Quality requirements (NFRs)** — measurable scenarios across a standard quality-attribute tree, with the architecturally-significant ones tagged.

## Rules
- walk a **standard quality-attribute tree** (a seed, not a closed list — current edition) × the domain's surfaces/objects/actors — every relevant characteristic judged (quizzed or skipped-as-moot). The branches:
  - **Performance-efficiency** — performance (p95/throughput **at a stated load profile — concurrency + data volume**), capacity, resource-use
  - **Reliability** — availability + RTO/RPO + SLA, **Faultlessness** (operates without fault under normal use), fault-tolerance, recoverability, maturity
  - **Security *level* only** — ASVS/patch-SLA/scan-cadence (the threat *model* is out of scope)
  - **Safety** (new branch) — operational-constraint · risk-identification · fail-safe · hazard-warning · safe-integration: where a malfunction could harm people, property, or environment
  - **Interaction-Capability** (the renamed usability branch) — appropriateness-recognizability · learnability · operability · user-error-protection · **User-Assistance** · **Inclusivity** (usable by the widest range of people — distinct from, and broader than, a WCAG conformance level) · plus **accessibility = a concrete WCAG level** as a verifiable conformance bar
  - **Compatibility** (new branch) — **co-existence** (shares an environment without harming neighbours) + **interoperability** (exchanges and uses information across systems)
  - **Maintainability** — modularity · reusability · analysability · modifiability · **testability coverage bars** + fitness functions
  - **Flexibility** — adaptability · installability · replaceability · **Scalability** (now a sub-characteristic here, to N)
  - **Functional-suitability** — completeness · correctness · appropriateness: **correctness rates** (accuracy/recall/determinism) where value rests on processing quality
  - plus **observability** (golden signals, MTTD)
- each NFR = **a number + measurement point + enforcement category** (test/gate/lint/infra/review) — no adjectives
- tag the **architecturally-significant** ones as ASRs — each a **full 6-part quality-attribute scenario** (source · stimulus · artifact · environment · response · response-measure) keyed to a real flow/use-case
- **surface NFR conflicts** (e.g. security↔usability, consistency↔availability)

## Output
**Stable IDs** (bare type prefix, ID = the leading table column / row key): `NFR-` quality requirement · `ASR-` architecturally-significant requirement, keyed to its NFR by the same number (NFR-014 → ASR-014).
Written under `requirements/quality/`:

| File | Captures | Format |
|---|---|---|
| `nfrs.md` | one row per scenario: id NFR-NNN · attribute · stimulus · measurable response (number) · enforcement category (test/gate/lint/infra/review) · ASR? (if architecturally significant, tag ASR-NNN keyed to this NFR — same number, e.g. NFR-014 → ASR-014) | — |
| `asrs.md` | architecturally-significant requirements: ASR-NNN keyed to its NFR (same number) — the full 6-part quality-attribute scenario | — |

ADRs → `adr/ADR-QUAL-NNN.md`
Consumes: the domain model's surfaces, objects and actors — the seed grid the quality tree is walked against.

## Excludes
mechanisms — caching/replicas/queues (→ the solution)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
