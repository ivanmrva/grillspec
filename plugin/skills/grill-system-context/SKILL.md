---
name: grill-system-context
description: >-
  Draw the system boundary: the system as one black box, its external actors and neighbor systems,
  the interfaces crossing the edge and the in/out scope line (the C4 System Context view). Use
  before the domain is modelled, when the product talks to outside systems.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo
---

# grill-system-context

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **System context & scope** — the system as one black box and everything at its boundary, drawn as the Level-1 (System Context) view.

## Depth by profile
| Profile | What the interview captures |
|---|---|
| `lite` | not a separate area: the constraints list the external systems and what crosses each boundary. |
| `standard`, `regulated` | the four files below, kept to the roster: one row per actor, one row per interface, one diagram. The qualities of an interface belong to the integration requirements. |

## Rules
- The system is one black box. Internal decomposition belongs to the domain model and the architecture.
- Every external actor and neighbor system appears on the diagram, and every diagram element is in the roster.
- Each interface records two facets and keeps them apart: the business context (what is exchanged, in domain terms) and the technical context (channel, protocol, hardware).
- The diagram uses proper Level-1 notation so it reads without a walkthrough: person, the system and external systems are visually distinct, every relationship is labelled with its intent and technology, and a legend keys the notation.
- Scope here is the system boundary (what the software does and does not do), which is distinct from the product's feature scope.
- Derive the in/out line and the roster from the product scope and the known actors. Ask only whether a neighbor system the user names is real, owned by them and in scope, because that is a fact the spec cannot carry.

## Output
**IDs:** `IF-` a boundary interface.
Written under `system-context/`:

| File | Captures | Format |
|---|---|---|
| `scope.md` | the system as a black box: name, one-line purpose, and what is in and out of the system boundary | one-line purpose · two lists (in / out) |
| `actors.md` | external actors (human roles at the boundary) and neighbor systems — the System Context roster | actor · type (human / system) · role at the boundary |
| `interfaces.md` | the inventory of boundary interfaces | table keyed on `IF-`: neighbor · direction (in / out / bi) · what-flows (business) · channel (technical) · trigger |
| `context-diagram.md` | the C4 Level-1 diagram: the system, its actors, its neighbor systems and the boundary | Mermaid |

ADRs → `adr/ADR-CTX-NNN.md`
Consumes: the human actors at the boundary (the personas marked as system users where customer discovery was run, otherwise the product vision's who-it-is-for paragraph) and the constraints (the environment and neighbor systems the boundary must respect).

## Excludes
internal decomposition — containers and components (C4 L2/L3) and the chosen architecture (→ the architecture) · the qualities of each interface — volume, latency, SLA, delivery guarantee, failure behaviour (→ the integration requirements) · the formal API and event contracts, schemas and versioning (→ the API contracts) · the product's feature scope and phasing (→ the product vision) · the internal bounded contexts and their relationships (→ the domain model, which consumes this boundary)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
