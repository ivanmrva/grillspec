---
name: derive-functional
description: >-
  Project the domain model into use-cases and testable Given/When/Then acceptance criteria — the acceptance layer that tasks and tests key on. Use when the domain model exists and the functional spec is missing or behind it.
disable-model-invocation: true
argument-hint: a recorded spec or design docs
---

# derive-functional

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md` first and follow it.** This skill applies that method to the **functional spec**: use-cases and their testable acceptance criteria, projected from the domain model.

The functional spec is the acceptance layer of the build. A task brief quotes the criteria it implements, and each behaviour test names the `AC-` it covers, so a criterion is the oracle a test is written against. The area carries almost no primary facts of its own: every use-case and criterion is a projection of something the domain model already states.

## Depth by profile
In scope at every profile (`lite`, `standard`, `regulated`), with the same shape. Its size follows the domain model, not the profile.

## What to project
- **Command use-cases.** One per command or flow: actor · trigger · outcome, mapped to its `CMD-`/`EVT-`.
- **View use-cases.** One per user-facing read model (`RM-`): actor · what they see · the `RM-` it surfaces. The query side is easy to miss, and a read surface with no use-case has no criteria and so no test. A read model that only other model elements or the architecture consume is marked N/A as an internal projection.
- **Flows.** The happy path plus the alternate and exception flows the command's invariants and policies already entail (invalid input, permission denied, conflict, timeout). They fall straight out of the projection, so they are written in the same pass as the happy path.
- **Acceptance criteria.** Projected from the invariants, business rules, specifications and policies that govern the use-case. Every invariant (`INV-`) is asserted by at least one criterion, or its definition notes that the model enforces it structurally (by construction, or a `DATA-` constraint); an invariant nothing asserts is an unenforced rule.

## Writing a criterion
- One Given/When/Then per criterion, with one behaviour and one observable outcome, so a single test can pass or fail it.
- A self-contained sentence. Task briefs quote the criterion text on its own, so it names its actor, precondition and outcome in words and reads correctly without the use-case block around it or a sibling criterion beside it.
- Terse: the precondition that matters, the action, the result. The rule it projects is cited after the sentence (`← INV-…`, `← POL-…`).

## Gaps
This is a projection. A rule the criteria need but the domain model does not state belongs in the domain model: record the gap against it there instead of authoring the rule here. A missing interaction detail is a gap to the UX requirements, a missing timing or resilience bound a gap to the quality requirements.

An edge the model already entails is projected in this pass. Only an edge no invariant or policy speaks to yet is recorded as a Deferred gap (`at-task`). A residual product-behaviour decision that has no owner upstream follows the engine's decide-or-ask rule and is recorded once made.

## Output
Stable IDs: `UC-` use-case · `AC-` acceptance criterion, keyed to its use-case as `AC-<ucnum><letter>` (UC-014 → AC-014a).
Written under `functional-spec/`:

| File | Captures | Format |
|---|---|---|
| `use-cases.md` | use-cases (actor · trigger · outcome · flows), not user stories; each use-case's acceptance criteria sit directly beneath it, never in a separate flat list | one block per use-case: UC-NNN · actor · trigger · outcome · maps-to `CMD-`/`EVT-` · flows, then one line per criterion: AC-NNN<letter> · flow · Given/When/Then · the rule it projects |

ADRs → `adr/ADR-FUNC-NNN.md`
Consumes: the domain model's commands, actors and process flows (→ use-cases) and its invariants, business rules, specifications and policies (→ acceptance criteria).

## Excludes
domain rules/invariants (→ the domain model) · interaction/microcopy (→ the UX requirements) · timing/resilience (→ the quality requirements) · the UI itself

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md`
- Worked example: `examples.md`
