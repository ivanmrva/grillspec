---
name: derive-impl-design
description: >-
  Write the short design note for a critical or genuinely complex slice, just before it is coded — the mechanism, concurrency, failure handling and the risk it contains. Use before coding a critical task: a new aggregate, a migration, auth, billing, a model seam, a one-way door.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# derive-impl-design

**Load `references/derive-engine.md` first and follow it.** This skill applies that method to the internals of one slice: a short design note, written just in time, that settles how the hard part works before any code depends on the answer.

## When a slice gets a note
A task brief asks for one with a `design` row reading `design-first — <path>`. Every `critical` task has it (a new aggregate or context, a schema or data migration, an authentication, authorization, erasure or billing path, a model seam, any one-way door), and so does a `feature` whose difficulty is real: a hard algorithm, genuine concurrency, a saga across contexts. An ordinary slice is designed while it is test-driven and gets no note; a design document for a CRUD slice only restates what the tests already say.

The note is written when the slice is about to be built, not earlier. By then the neighbouring slices exist, and their code shows where the real seams are.

## What the note takes as given
The module map, each module's `role:`, the dependency direction and the seam interfaces belong to the architecture and are already decided. The note designs behind those interfaces. If the slice cannot be built without changing an interface, that is a gap to raise against the architecture; a local override would leave the two documents disagreeing.

## What the note contains
Write only the parts the slice actually has. A migration has no concurrency section if it runs alone; a pricing algorithm has no rollout section.

| Part | Content |
|---|---|
| lead line | `implements MOD-NNN · serves T-NNN` — the modules designed and the task served, by ID (the linter checks both are named) |
| mechanism | the core algorithm or sequence in numbered steps or a short sketch: enough to see how it works, not how to type it |
| the risk and its containment | what makes the slice critical, and how the design keeps it reversible or safe: the staging of a one-way door, where an authorization check is enforced, what a failed model call falls back to |
| concurrency | where it is real: locking or optimistic versioning, shared state, idempotency and re-entrancy, cancellation, timeouts and deadlines, what stays atomic when part of the work fails |
| errors | table: error · retryable? · `designed-out`, `masked` or `propagated` · why. `designed-out` means the design removes the case (a default, an idempotent no-op); `masked` means it is absorbed at the boundary; `propagated` means the caller sees it |
| failure path | a Mermaid sequence, when the slice introduces a compensation or failure path that prose does not make clear |

A choice in the note that is costly to reverse and that a reader would not expect becomes an ADR (`adr/ADR-IMPL-NNN.md`) with the alternatives rejected; the note then refers to it.

## What the note leaves out
- The brief's content. The outcome, acceptance criteria and rules are stated once, in the brief; the note refers to a criterion by ID where the design turns on it.
- Code and heavy pseudocode. The tests and the implementation carry that detail and cannot drift from themselves.
- Modules the slice does not touch.
- A new seam for a single implementation. Design a deep module — much behaviour behind the small interface the architecture fixed, which stays the test surface — and add an abstraction when a second concrete implementation needs it.

Keep it short: a note that takes longer to read than the slice takes to review has stopped helping.

## Output
One note per slice, under `spec/10-delivery/impl-design/`, at the path the brief's `design` row names (by convention `T-NNN-<slug>.md`). It is an ordinary authored document: when building shows the design was wrong, edit it in place so it states the design as built. A later slice that changes the same mechanism edits the existing note and names it in its own `design` row, so one mechanism never has two notes that can disagree.

| File | Captures | Format |
|---|---|---|
| `T-NNN-<slug>.md` | the design note described above | the lead line, then short sections; tables for errors |
| `adr/ADR-IMPL-NNN.md` | a costly-to-reverse design choice with its alternatives | ADR |

Reads: the brief, the architecture's module map and seam interfaces for the modules it touches, and the code those modules already have.

## Resources
- `references/derive-engine.md`
- Worked example: `examples.md`
