---
name: derive-architecture
description: >-
  Derive the solution architecture from the settled spec — the load-bearing decisions, the tech stack
  and the module map with its seam contracts; above the lite profile also C4, services, quality tactics
  and key sequences. Use when the domain model and requirements exist.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# derive-architecture

**Load `references/derive-engine.md` first and follow it.** This skill applies that method to the **solution architecture**: style, decomposition, stack, the module map with its seam contracts, and the cross-cutting concerns.

The architecture is what lets independent vertical slices integrate. It is complete when an agent can implement any slice without making a further architectural decision.

## Depth by profile
How much is written follows the project's profile:

| Profile | Written |
|---|---|
| `lite` | `solution-strategy.md`, `stack.md`, `modules.md` and the ADRs |
| `standard`, `regulated` | every file in the Output table |

At `lite` the seven further solution areas (data, API contracts, security, observability, infrastructure and operations, test strategy, ML) are not written, so `solution-strategy.md` also carries the handful of decisions they would own. Each is one numbered decision, recorded only where the product has the concern: the datastore and tenancy model · the API versioning and error policy · the sign-in and key-management choice · the environments and promotion path · the service-level objectives that page · the test tiers and their bars · for an AI feature, the model choice, its fallback and the gate before promotion. Anything more detailed than a decision is left to the code and the conventions.

## What to decide
- **Solution strategy.** The three to five load-bearing decisions: the top decomposition approach · the key technology choices · how the top quality goals are met · the key organisation/team decisions.
- **Decomposition.** The style, then bounded contexts → services, then the module map. Each module (`MOD-`) records its `role:` (domain · driving-port · driven-port · adapter · application-service), its allowed dependency direction (inward only), the public interface it exposes at its seam, and `realises:` — the `AGG-`/`UC-` it exists for, or `N/A — why` for a purely technical module. The `realises:` link is what lets a changed aggregate be traced to the modules it affects.
- **Stack.** Each choice with its rationale; the latest stable, idiomatic release unless a user or constraint pins a version.
- **Quality.** Each `ASR-` → a named tactic → the point in the C4 where it is realised → the fitness function that guards it, with the trade-off recorded.
- **Key sequences.** The golden-path end-to-end trace, plus a critical-failure or compensation path for each transactional or cross-context interaction.

## Rules
- **Seams here, internals later.** A module's public interface is fixed here because it is the stable contract slices build against. Module internals (algorithm, error taxonomy, concurrency) are designed per slice, just in time, and stay out of this artifact.
- **One-way doors are ratify-points.** The primary cloud, the core datastore and the primary language/runtime reverse only at great cost and often turn on an organisation's commitment. Propose the merit pick and surface it for ratification as the engine describes.
- **Co-design the concerns that reshape the structure.** Security trust boundaries, data topology and ML data dependencies are committed here as part of the skeleton, at the level of strategy. Their finer detail (the full schema, the detailed authorization or serving design) belongs to each concern's own area.
- Every bounded context is placed in a service and module.
- Check the style and stack against the qualities the product has requirements for (reliability, security, cost, performance, operability). A significant component the team could buy gets a build-vs-buy ADR.
- A trade-off's residual risk, and any deliberate technical debt, is recorded as the consequence of the ADR that makes the call, so the mitigation lives in the design. An unclosed spec gap is not a risk entry; it closes upstream.

## Output
Written under `solution/arch/`:

| File | From | Captures | Format |
|---|---|---|---|
| `solution-strategy.md` | `lite` | the load-bearing decisions; at `lite` also the decisions of the solution areas that are not written | numbered: decision · why · alternatives rejected (ADR ref) |
| `stack.md` | `lite` | the technology stack | table: concern · choice · ADR |
| `modules.md` | `lite` | the module map: one row per module with its role, what it realises, its dependency direction and its seam interface | table keyed on `MOD-`: module · role · realises (`AGG-`/`UC-`) · direction · seam interface |
| `style.md` | `standard` | the architecture style and the decided cross-cutting concerns (authn/authz · errors · logging/trace · transactions · caching · config · idempotency · concurrency · feature flags · gateway/BFF) | table: concern · decision · ADR |
| `c4.md` | `standard` | C4 containers (L2) and typed components (L3), refining the System Context (L1) taken from the system context | Mermaid C4 + typed component list |
| `services.md` | `standard` | bounded contexts → services/deployable units, with inter-context communication and consistency | table: context · service/unit · comms mode (sync/async · choreography vs saga) · consistency · failure handling · data owner |
| `quality.md` | `standard` | each `ASR-` → mitigating tactic → its C4 location → the fitness function that guards it | table: ASR · tactic · C4 location · fitness function |
| `sequences.md` | `standard` | the key cross-module interactions: the golden path and at least one critical-failure/compensation path per transactional or cross-context interaction | Mermaid |

ADRs → `adr/ADR-ARCH-NNN.md`
Consumes: the domain model (its bounded contexts drive the service and module decomposition) · the settled requirements · the quality NFRs/ASRs · the system context's System Context (L1) · the entitlement tiers. All upstream layers are available.

## Excludes
source code · detailed schema (→ the data architecture) · API artifacts (→ the API & event contracts)

## Resources
- `references/derive-engine.md`
- Worked example: `examples.md`
