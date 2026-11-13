---
name: grill-ddd
description: >-
  Turn an idea or existing docs into a Domain-Driven Design model: subdomains, bounded contexts,
  aggregates with their invariants, commands and events, plus the ubiquitous language and actor
  roster. Use when modelling a domain, even if the user never says DDD.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo to model
---

# grill-ddd

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **Domain-Driven Design** — turning an idea or existing docs into a domain model, building the ubiquitous language and actor roster as it goes.

## Depth by profile
In scope at every profile.

| When | What the model captures |
|---|---|
| every profile | the bounded contexts and how they relate · the ubiquitous language and actor roster · per aggregate, its invariants, state table, commands and events · the policies that react to events |
| the domain has them | hotspots · value objects and entities that carry rules of their own · read models a screen or report depends on · an event flow, where a process crosses aggregates or contexts |
| the domain needs it, or `regulated` | catalogues of domain services (`SVC-`), repositories (`REPO-`) and factories (`FAC-`). In most domains a repository per aggregate is implied, and listing it tells the build nothing. |

## Method
The order matters: each step uses what the one before settled.

1. **Frame the domain.** What the product does and its subdomains, each classified Core / Supporting / Generic. The split decides build-versus-buy and where to invest, so it is the user's to ratify. Propose a classification with a one-line reason per subdomain, and recommend Core only for what truly differentiates the product.
2. **Discover event-first.** Explore the domain as a timeline of domain events (things that happened). Derive the commands that cause them and the actors and policies behind those, then cluster commands and events into aggregates. Mark the pivotal events, where responsibility or phase shifts, because context boundaries fall there. Record a hotspot (an unresolved unknown, a conflict of opinion, a terminology clash) where it surfaces.
3. **Map the bounded contexts.** Seam them at the pivotal events and draw the context map with typed, directed relationships. The system-context boundary is taken as given.
4. **Model each context tactically.** One block per aggregate, plus the entities, value objects, policies and read models the context has.

## Rules
- **Ubiquitous language.** One language per bounded context, and one meaning per term within it. Agree each term by proposing and confirming it: a term the domain already has is the user's to give, so harvest it from the input first. A label coined for a new concept is marked coined (an `inferred` term, or a `HOT-` if contested) so it can be superseded. Terms go to `glossary.md`, actors to `actors.md`.
- **Aggregates.** Each has a root, invariants, a state model, a transaction boundary, commands and events. Size it by its true invariant and its expected throughput and contention: as small as the invariant allows. It references other aggregates by identity only, and one transaction changes one aggregate, so consistency across aggregates is eventual.
- **Cross-aggregate invariants.** Each names the reactive policy that restores consistency, stated as "whenever EVT-… then CMD-…": the event that breaks the rule and the command that repairs it. A cross-aggregate rule without that policy is unenforced.
- **Commands and events.** Every command produces an event. Every event has a consumer, or states that it has none.
- **Value objects.** Model an attribute cluster with no identity as an immutable value object, equal by value. Make implicit concepts explicit (Money · DateRange · Address · typed ids) and put their validation inside them, so entities do not carry bare primitives.
- **Context relationships** are typed and directed. Upstream/downstream: Open-Host-Service (the published API the upstream exposes) · Published-Language (the shared schema the exchange speaks) · Anti-Corruption-Layer · Conformist · Customer-Supplier. Symmetric: Shared-Kernel · Partnership. No integration: Separate Ways (duplicate rather than couple) · a wall-off around a legacy system that is contained, not integrated.

## IDs
aggregate `AGG-` · command `CMD-` · event `EVT-` · value object `VO-` · entity `ENT-` · invariant `INV-` · policy/saga `POL-` · read model `RM-` · hotspot `HOT-` · domain service `SVC-` · repository `REPO-` · factory `FAC-`

- Write each element as `<ID> <Name>`, the id first and then its PascalCase name: `commands: CMD-201 ExtractAtoms · CMD-204 ReExtract`, or a table row keyed on the id. That form is what registers the element as a definition.
- Every aggregate invariant carries an `INV-` id, so an acceptance criterion can trace to the exact rule it asserts.
- Namespace contexts by disjoint numeric bands (orders `AGG-2xx`, billing `AGG-3xx`). A context prefix in front of the type breaks id resolution.

## Output
Written under `domain/ddd/`, grouped per bounded context. Within a context, each aggregate is one block with its commands, events and invariants nested under it. A flat list of all commands, then all events, then all aggregates hides which rule belongs to which aggregate.

| File | Captures | Format |
|---|---|---|
| `strategic/subdomains.md` | subdomains classified Core / Supporting / Generic, each with its reason | table |
| `strategic/context-map.md` | the bounded contexts and their typed, directed relationships | Mermaid |
| `strategic/event-flow.md` | per context, the domain events in timeline order with their triggering commands and reacting policies; pivotal events marked | per context: ordered `EVT-` ⟵ `CMD-` → policy |
| `strategic/hotspots.md` | the unresolved unknowns, conflicts of opinion and terminology clashes, and where each one bites | `HOT-NNN` · area · question · status (open / resolved) |
| `tactical/<context>/aggregates.md` | one block per aggregate: root · invariants (`INV-`) · state model · transaction boundary · commands · events · size/throughput note | a block per aggregate; the state model is a transition table |
| `tactical/<context>/entities.md` | entities: identity and lifecycle | one entry per `ENT-` |
| `tactical/<context>/value-objects.md` | value objects and the rules pushed into them | one entry per `VO-` |
| `tactical/<context>/policies.md` | policies and sagas (`POL-`); domain services (`SVC-`) where catalogued | one entry per id; a policy reads "whenever EVT-… then CMD-…" |
| `tactical/<context>/read-models.md` | read models (`RM-`); repositories (`REPO-`) and factories (`FAC-`) where catalogued | one entry per id |
| `glossary.md` | the ubiquitous language, per context | term · context · definition |
| `actors.md` | the actor roster | actor · what they do |

The state model is a transition table with the columns `from · trigger · to · guard`. Mark the initial state by writing `(initial)` in its `from` cell and a terminal state by writing `(terminal)` in its `to` cell. Every state is then reachable and either exits or is terminal, and two transitions that share a `from` and a `trigger` each carry a distinguishing guard.

ADRs → `adr/ADR-DDD-NNN.md`
Consumes: the product vision's coarse scope (which bounded contexts exist), the constraints (the bounds on the model), and the system context where it exists (the external boundary and neighbor systems the model sits inside).

## Excludes
implementation/tech · NFRs · pricing · GTM · UX visuals

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
