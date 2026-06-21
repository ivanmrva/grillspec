---
name: derive-architecture
description: >-
  Derive the solution architecture — style, C4 decomposition, tech stack, contexts→services, cross-cutting concerns, the module map & seam contracts, and the key sequences — from the settled spec. Use when the requirements are settled and you need the architecture derived (not interviewed). Loads the shared derive engine.
disable-model-invocation: true
argument-hint: a recorded spec or design docs
---

# derive-architecture

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md` first and follow it.** This skill applies that method to **Solution architecture** — style, C4 decomposition, stack, contexts→services, and cross-cutting concerns.

## Method
1. apply the convergence test per fork: decide on merit · ask only the true preference/constraint forks · pick conventional taste & move on
2. **solution strategy** — the 3–5 load-bearing decisions: top decomposition approach · key technology choices · how the top quality goals are met · key org/team decisions
3. style → contexts→services → component decomposition → the **module map**: each module's `role:` (domain · driving/driven-port · adapter · application-service), its inward-only dependency direction, and **the public interface it exposes at its seam** (the stable contract independent slices integrate against)
4. stack (latest-stable, rationale each)
5. each `ASR-` → tactic → its C4 location → the fitness function guarding it
6. the **key sequences** — the golden-path end-to-end trace + a critical-failure/compensation path per transactional or cross-context interaction
7. record every default in the artifact (load-bearing ones as ADRs)

## Rules
- choose **latest-stable + idiomatic** by default — for the tech stack **and any standard/format/protocol it adopts**; a named stack or standard implies its current stable release unless a user/constraint pins one. Never bake a historical version into the design
- **decide the stack, but surface each one-way door as a ratify-point** — the lock-in choices (primary cloud · core datastore · primary language/runtime) reverse only at great cost and often turn on an org commitment; propose the merit pick, but flag it for ratification rather than silently baking it in
- every context placed; every ASR addressed by a **named tactic** realised at a specific point in the C4 (trade-off recorded)
- style/stack choices checked against the cloud **well-architected pillars** (reliability · security · cost · performance · operability · sustainability); a significant component records a **build-vs-buy** ADR
- **an agent could implement ANY part with no further architectural decision**
- the **seam contracts** (each module's public interface) are fixed here — they are what lets independent vertical slices integrate; module *internals* (algorithm, error taxonomy, concurrency) are **not** designed here — they're produced per-slice, just-in-time
- completeness verified both directions (no silent gap, no gold-plating)
- a trade-off's **residual risk** + any **deliberate technical debt** is recorded as the **consequence of the ADR** that makes the call (the mitigation lives in the design, not a log) — never a parking lot for unclosed spec gaps, which close upstream; whatever composes the areas reconciles the cross-area risk register from these

## Output
Written under `solution/arch/`:

| File | Captures | Format |
|---|---|---|
| `solution-strategy.md` | the 3–5 load-bearing decisions: top decomposition approach · key technology choices · how the top quality goals are achieved · key org/team decisions | — |
| `style.md` | the architecture style + the decided cross-cutting concerns (authn/authz · errors · logging/trace · tx · caching · config · idempotency · concurrency · feature-flags · gateway/BFF) | — |
| `c4.md` | C4 decomposition in Mermaid: containers (L2) · components (L3, typed) — refining the System Context (L1) taken from the system context | Mermaid · C4 context/container/component · typed component list |
| `stack.md` | technology stack table: concern · choice · ADR (latest-stable/idiomatic by default) | table: concern · choice · ADR |
| `services.md` | bounded contexts → services/deployable units + inter-context comms & consistency (sync/async · choreography vs saga · failure handling · data ownership) | — |
| `modules.md` | the module/component map — per module (`MOD-`): `role:` (domain · driving-port · driven-port · adapter · application-service) · allowed dependency direction (inward only) · **the public interface it exposes at its seam** (the stable contract slices build against) | table keyed on `MOD-`: module · role · direction · seam interface |
| `quality.md` | each `ASR-` → mitigating tactic → its C4 location → the **fitness function** that guards it | table: ASR · tactic · C4 location · fitness function |
| `sequences.md` | the key cross-module interactions in Mermaid — the golden-path end-to-end trace **+ ≥1 critical-failure/compensation path** per transactional or cross-context interaction | Mermaid |

ADRs → `adr/ADR-ARCH-NNN.md`
*(DERIVED & regenerate-only — never hand-edited)*
Consumes: the **domain model** (its bounded contexts → the service/module decomposition; the dependency sink) + the settled requirements + the quality NFRs/ASRs + the system context's System Context (L1) + the entitlement tiers. **Co-design the irreducible cross-cutting concerns — security trust boundaries, data topology, ML data-dependencies — in this pass**, not deferred: those are one-way doors that reshape the structure, so the architecturally-significant *strategy* for each is committed here as part of the skeleton. (Finer per-concern detail — the full schema, the detailed authz/serving design — is out of this artifact's scope.) All upstream layers are available.

## Excludes
source code · detailed schema (→ the data architecture) · API artifacts (→ the API & event contracts)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md`
- Worked example: `examples.md`
