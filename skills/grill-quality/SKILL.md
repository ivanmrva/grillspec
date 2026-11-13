---
name: grill-quality
description: >-
  Turn vague quality wishes into measurable targets (NFRs): a number, where it is measured and how
  it is enforced, with the architecture-shaping ones tagged as ASRs. Use when the design needs
  performance, reliability, security-level or accessibility bars it can be held to.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# grill-quality

**Load `references/grill-engine.md` first and follow it.** This skill applies that method to **Quality requirements (NFRs)** — measurable quality targets, with the architecturally-significant ones tagged.

## Depth by profile
| Profile | What the interview captures |
|---|---|
| `lite`, `standard` | the 5–10 quality targets that actually shape the design, each with a ratified number and how it is enforced. The tree below is a prompt for finding them; a branch the product does not stress gets no row. |
| `regulated` | the full tree walked as a grid against the domain's surfaces, objects and actors. Every relevant characteristic is either quantified or recorded as moot with the reason. |

## Rules
- Each NFR is a number, a measurement point and an enforcement category (test · gate · lint · infra · review). An adjective is not a requirement. Each number is the user's target to ratify, so propose one with its reason ("p95 < 200 ms at peak; typical for an interactive web app").
- A performance number names its load profile (concurrency and data volume); without it the number cannot be tested.
- The availability / RTO / RPO row also carries its `dr-tier` (backup-restore · pilot-light · warm-standby · active-active). The tier is a cost commitment the user ratifies here, so the infrastructure design realises a confirmed tier.
- Tag the architecturally significant NFRs as ASRs. Each is a six-part quality-attribute scenario: source · stimulus · artifact · environment · response · response measure. The artifact is the system or an architectural element, and the stimulus is an event, a load or a fault. A measurable instance may be bound to a domain operation or a `UC-` for test traceability.
- Surface conflicts between targets (security ↔ usability, consistency ↔ availability) and settle each in an ADR.

## The quality-attribute tree
A seed list in its current edition, open to branches the product adds.

| Branch | What to pin |
|---|---|
| Performance efficiency | response time and throughput at a stated load profile · capacity · resource use |
| Reliability | availability · RTO/RPO · SLA · faultlessness under normal use · fault tolerance · recoverability · maturity |
| Security level | verification level (ASVS) · patch SLA · scan cadence. The threat model belongs to the security requirements. |
| Safety | where a malfunction could harm people, property or the environment: operational constraints · risk identification · fail-safe · hazard warning · safe integration |
| Interaction capability | recognisability · learnability · operability · user-error protection · user assistance · inclusivity (usable by the widest range of people) · accessibility as a concrete WCAG level |
| Compatibility | co-existence (shares an environment without harming neighbours) · interoperability |
| Maintainability | modularity · reusability · analysability · modifiability · testability (coverage bars, fitness functions) |
| Flexibility | adaptability · installability · replaceability · scalability |
| Functional suitability | completeness · correctness · appropriateness, with correctness rates (accuracy, recall, determinism) where the value rests on processing quality |
| Observability | golden signals · time to detect |

## Output
**IDs:** `NFR-` quality requirement · `ASR-` architecturally-significant requirement, keyed to its NFR by the same number (NFR-014 → ASR-014).
Written under `requirements/quality/`:

| File | Captures | Format |
|---|---|---|
| `nfrs.md` | one row per requirement | table: `NFR-` id · attribute · stimulus · measurable response · `enforced-by` (test / gate / lint / infra / review) · ASR? — with `dr-tier` on availability / RTO / RPO rows |
| `asrs.md` | the six-part scenario for each ASR | `ASR-NNN` (same number as its NFR) · source · stimulus · artifact · environment · response · response measure |

ADRs → `adr/ADR-QUAL-NNN.md`
Consumes: the domain model's surfaces, objects and actors, which are what the targets are found against. Quality attributes are orthogonal to functionality, so this area does not depend on the use-cases.

## Excludes
mechanisms — caching/replicas/queues (→ the solution)

## Resources
- `references/grill-engine.md`
- Worked example: `examples.md`
