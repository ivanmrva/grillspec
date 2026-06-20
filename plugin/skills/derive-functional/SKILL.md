---
name: derive-functional
description: >-
  Project the domain model into use-cases (commands × actors × flows) and testable acceptance criteria (invariants/rules/specs/policies). Use when the domain model exists and you need use-cases plus acceptance criteria projected from it. Loads the shared derive engine.
disable-model-invocation: true
argument-hint: a recorded spec or design docs
---

# derive-functional

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md` first and follow it.** This skill applies that method to **Functional spec** — use-cases plus testable acceptance criteria, projected from the domain model.

## Method
1. per command/flow: project a **command** use-case (actor · trigger · outcome); per **user-facing read-model / read-surface**: project a **view** use-case (actor · what they see · the `RM-` it surfaces) — the query side, not only the command side
2. project its acceptance criteria from the relevant invariants/rules/specs/policies
3. missing *domain* rule → gap to the domain model; missing interaction → gap to the UX requirements; missing timing → gap to the quality requirements
4. only a true residual product-behavior decision is derive-and-asked + recorded

## Rules
- every in-scope command/flow projected to ≥1 use-case; each maps to `CMD-`/`EVT-` IDs
- **every user-facing read-model/read-surface (`RM-`) projects to ≥1 view use-case** — or is marked **N/A** as an internal projection (one only other model elements or the architecture consume); a read surface no use-case surfaces is an under-projected functional spec, not a silent pass
- **every use-case projects its happy path PLUS the alternate/exception flows entailed by its command's invariants and policies NOW** — invalid-input · permission-denied · timeout · conflict (and any other rejection the model's rules imply); these are not deferrable, they fall straight out of the projection
- every use-case has acceptance criteria traceable to a domain-model rule (or a logged gap); **each acceptance criterion is singular and verifiable** — one Given/When/Then asserting one outcome (the test oracle), never a compound clause
- this is a projection — if you find yourself *inventing* a rule, it belongs in the domain model: raise it there, don't author it here. This area carries almost no primary facts of its own
- only a **genuinely model-absent** edge (no invariant/policy in the model speaks to it yet) → record a **Deferred** gap (`at-task`), not a blocker now — but an edge the model *already* entails is projected now, not deferred

## Output
**Stable IDs** (bare type prefix, ID = the leading table column / row key): `UC-` use-case · `AC-` acceptance criterion, keyed to its use-case as `AC-<ucnum><letter>` (UC-014 → AC-014a).
Written under `functional-spec/`:

| File | Captures | Format |
|---|---|---|
| `use-cases.md` | the artifact is **use-cases** (actor · trigger · outcome + flows), **not user stories** — one block per use-case (id UC-NNN · actor · trigger · outcome) covering the **happy path and its alternate/exception flows** (invalid-input/permission-denied/timeout/conflict), with its acceptance criteria nested directly beneath — NEVER a flat list detached from their use-cases — each keyed to its parent as AC-NNN<letter> (UC-014 → AC-014a/b), one **singular, verifiable** Given/When/Then per criterion (the test oracle) · maps-to CMD-/EVT- | UC-NNN: actor · trigger · outcome · flows · AC-NNN<letter> Given/When/Then (singular) · maps-to |

ADRs → `adr/ADR-FUNC-NNN.md`
*(one file — DERIVED & regenerate-only; never hand-edited)*
Consumes: the domain model's commands/actors/process-flows (→ use-cases) and its invariants/business-rules/specifications/policies (→ acceptance criteria).

## Excludes
domain rules/invariants (→ the domain model — a missing one is a gap there) · interaction/microcopy (→ the UX requirements) · timing/resilience (→ the quality requirements) · the UI itself

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md`
- Worked example: `examples.md`
