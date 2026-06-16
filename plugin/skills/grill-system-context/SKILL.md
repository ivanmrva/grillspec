---
name: grill-system-context
description: >-
  Nail the system boundary before the domain is modelled — the system as one black box, its external actors and neighbor systems, the interfaces that cross the edge, and the in/out scope line, drawn as the C4 System Context view. Loads the shared grill engine.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo
---

# grill-system-context

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **System context & scope** — the system as one black box and everything at its boundary, drawn as the Level-1 (System Context) view.

## Rules
- the system is **ONE black box** — no internal decomposition
- every external actor and neighbor system appears on the diagram; none orphaned
- each interface has a **business-context** facet (what's exchanged in domain terms) and a **technical-context** facet (channel/protocol/hardware) — both recorded, kept distinct; interface *qualities/SLAs* stay out of scope
- the **Level-1 context diagram uses proper notation** — every element typed (person vs the system vs external system, visually distinct) · every relationship labeled with its **intent + technology** (the "how") · a **legend** keying the element types and notation
- **scope is the SYSTEM boundary** (in/out of the software), distinct from the product's *feature* scope
- **decide the boundary; ask only what you can't know** — derive the in/out line + the actor/neighbor roster from the product scope and the discovered actors; **ASK only whether a neighbor system the user names is real, owned by them, and in-scope** — a neighbor's existence/ownership is a fact the spec can't carry

## Output
Written under `system-context/`:

| File | Captures | Format |
|---|---|---|
| `scope.md` | the system as a black box: name · one-line purpose · what's IN vs OUT of the system boundary (system scope, NOT the product's feature scope) | two lists in/out · one-line purpose |
| `actors.md` | external actors (human roles at the boundary) + neighbor/external systems — the C4 System Context roster | actor · type human/system · role at the boundary |
| `interfaces.md` | per neighbor: direction (in/out/bi) · **business context** — what's exchanged in domain terms · **technical context** — channel/protocol/hardware · trigger  (the INVENTORY; volumes/SLAs/failure behaviour are out of scope) | table: neighbor · direction · what-flows (business) · channel (technical) · trigger |
| `context-diagram.md` | the C4 Level-1 System Context diagram (Mermaid): the system + its actors + neighbor systems + the boundary line | Mermaid |

ADRs → `adr/ADR-CTX-NNN.md`
Consumes: the **personas / system-users** (from customer discovery — the human actors at the boundary) and the **constraints** (the environment + neighbor systems the boundary must respect).

## Excludes
internal decomposition — containers/components (C4 L2/L3) and the chosen architecture (→ the architecture) · the *qualities* of each interface — volume/latency/SLA/delivery-guarantee/failure behaviour (→ the integration requirements) · the formal API/event **contracts**, schemas, versioning (→ the API contracts) · the product's *feature* scope and phasing (→ the product vision) · the **internal** bounded contexts & their relationships (→ the domain model, which consumes this boundary)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
