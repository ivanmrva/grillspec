---
name: grill-ddd
description: >-
  Turn an idea or existing docs into a complete Domain-Driven Design model — subdomains, bounded contexts, aggregates — building the ubiquitous language and actor roster as it goes. Use when modelling a domain, even if the user never says "DDD". Loads the shared grill engine.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo to model
---

# grill-ddd

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **Domain-Driven Design** — turning an idea or existing docs into a domain model, building the ubiquitous language and actor roster as it goes.

## Method
1. **Frame the domain** — what the product does, its subdomains, each classified **Core / Supporting / Generic** (drives build-vs-buy and where to invest).
2. **Discover event-first** (big-picture → process → design) — explore the domain as a **timeline of domain events** (the things that happened), then **derive the commands** that cause them and the actors/policies behind those, then **cluster commands+events into aggregates**, and use the natural seams in the flow to **find bounded-context boundaries**. Record **hotspots** (unresolved unknowns, conflicting opinions, terminology clashes) where they surface rather than papering over them, and mark **pivotal events** (the ones that shift responsibility or phase) — these are the cues for where context boundaries fall. Capture a **process-level event flow per context** (events in order with their triggering commands and reacting policies), not just the static model.
3. **Map the bounded contexts** — the contexts and their boundaries (seamed at the pivotal events); draw the **context map** with typed relationships and their direction. The system-context boundary is taken as given.
4. **Build the ubiquitous language** — per context, agree the domain terms (one meaning within the context) into `glossary.md`; capture the actors in `actors.md`.
5. **Model each context tactically** — per context, **one block per aggregate** (root, invariants, **state model: states · allowed transitions · guards**, transaction boundary, commands, events, **size/throughput note**) plus entities, **value objects** (immutable, equality-by-value — push implicit concepts like Money/DateRange/typed-Ids and their rules *into* them), policies/sagas, read models, domain services, repositories, factories.

## Rules
- **One ubiquitous language per bounded context** — domain-established terms only, one meaning within the context
- **Effective-aggregate rules** — root + invariants + **state model (states · transitions · guards)** + transaction boundary + commands + events; **right-sized by its true invariant + expected throughput/contention** (as small as the invariant allows); references other aggregates **by identity only**; **one aggregate per transaction** (cross-aggregate consistency is eventual)
- **Prefer value objects** — model any attribute-cluster with no identity as an **immutable value object** (equality by value); make implicit domain concepts explicit as VOs (Money · DateRange · Address · typed Ids) and push their validation/behaviour inside them rather than leaving bare primitives on entities
- **Every cross-aggregate invariant names the reactive policy** that restores eventual consistency — stated as **"whenever EVT-… then CMD-…"** (the event that breaks it → the command that repairs it); a cross-aggregate rule with no such policy is incomplete
- **Every command produces an event; every event has a consumer or an explicit none**
- **Typed context relationships, drawn from the full set** — upstream/downstream: **Open-Host-Service** (the published API/contract the upstream exposes) · **Published-Language** (the shared schema the exchange speaks — distinct from OHS) · **Anti-Corruption-Layer** · **Conformist** · **Customer-Supplier**; symmetric: **Shared-Kernel** · **Partnership**; and the non-integration cases: **Separate Ways** (deliberate no integration — duplicate rather than couple) · a **wall-off** relationship around a legacy/big-ball-of-mud system (contained behind a boundary, not integrated into). Each relationship carries its up/down-stream direction.
- stable IDs: aggregate `AGG-`, command `CMD-`, event `EVT-`, value object `VO-`, hotspot `HOT-`

## Output
Written under `domain/ddd/`:

Not every file is always produced; create one only when the product has that content. The DDD schema is grouped **per bounded context**, then **one block per aggregate** with its commands, events and invariants nested under it — **never a flat dump** of all commands, then all events, then all aggregates.

| File | Captures | Format |
|---|---|---|
| `strategic/subdomains.md` | subdomains classified Core / Supporting / Generic | — |
| `strategic/context-map.md` | bounded contexts + typed relationships (with direction) | Mermaid |
| `strategic/event-flow.md` | process-level event flow **per context** — domain events in timeline order with their triggering commands and reacting policies; **pivotal events** marked (the boundary/phase-shift cues) | per context: ordered EVT- ⟵ CMD- → policy; pivotal flagged |
| `strategic/hotspots.md` | hotspots — unresolved unknowns, conflicting opinions, terminology clashes surfaced during discovery, each with status (open/resolved) and where it bites | id HOT-NNN · area · question · status |
| `tactical/<context>/aggregates.md` | one block per aggregate: root · invariants (cross-aggregate ones naming "whenever EVT- then CMD-") · **state model (states · allowed transitions · guards)** · transaction boundary · commands · events · **size/throughput note (what right-sizes it)** | — |
| `tactical/<context>/entities.md` | entities — identity + lifecycle | — |
| `tactical/<context>/value-objects.md` | value objects — immutable, equality-by-value; the concepts + invariants pushed into them (Money · DateRange · typed Ids) | — |
| `tactical/<context>/policies.md` | policies / sagas, domain services | — |
| `tactical/<context>/read-models.md` | read models, repositories, factories | — |
| `glossary.md` | ubiquitous language (per-context terms) | — |
| `actors.md` | actor roster | — |

ADRs → `adr/ADR-DDD-NNN.md`

## Excludes
implementation/tech · NFRs · pricing · GTM · UX visuals

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
