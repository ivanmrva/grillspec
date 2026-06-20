---
name: derive-impl-design
description: >-
  Low-level design of the modules a slice touches — algorithm, error handling, concurrency — produced just-in-time for a complex slice, just before it is coded (DESIGN, not code). The architecture already fixed each module's role, dependency direction, and seam interface; this designs the internals behind it. Use for a hard slice (tricky algorithm · real concurrency · cross-context saga) before implementing it. Loads the shared derive engine.
disable-model-invocation: true
argument-hint: the slice (and the modules it touches) to design
---

# derive-impl-design

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md` first and follow it.** This skill applies that method to **per-slice module internals** — the low-level design of the modules a slice touches, produced just-in-time before coding a hard slice. It does **not** re-decide structure: the module's `role:`, dependency direction, and **seam interface are already fixed in the architecture**; this designs behind that interface.

## Method  (for the modules THIS slice touches — not every module)
1. take the module's `role:`, dependency direction, and **seam interface** as given (from the architecture)
2. design its **core algorithm / sequence-level mechanism** + **concurrency model** (async · locking · shared-state · idempotency/reentrancy · cancellation · timeout/deadline · partial-failure atomicity)
3. design its **error handling** — taxonomy + which are retryable; mark each error `designed-out | masked | propagated` with rationale (designed-out = removed via a default / idempotent no-op / masked at the boundary so it can't arise)
4. a Mermaid sequence for any tricky failure/compensation path the slice introduces

## Rules
- **per-slice & risk-gated** — produced only for a **complex** slice (a hard algorithm · real concurrency · a cross-context saga); a simple/CRUD slice is designed as it is TDD'd, with no design step
- **internals only** — the seam interface, role, and dependency direction belong to the architecture; never re-open them here (a needed interface change is a **gap raised to the architecture**, not a local override)
- **design DEEP modules** — a lot of behaviour behind the *small* interface the architecture fixed; the interface stays the test surface
- **don't introduce a seam until a second concrete implementation needs it** — exactly why this is JIT: the second consumer reveals the real seam
- DESIGN fidelity — no code, no heavy pseudocode

## Output
Written under `delivery/impl-design/` — **filled incrementally**, one file per module **as a slice touches it** (not all modules up front):

| File | Captures | Format |
|---|---|---|
| `<module>.md` | the module's internal design: algorithm (steps / short pseudocode-sketch) · concurrency model (incl. cancellation · timeout/deadline · partial-failure atomicity) · errors (taxonomy + retryable + each `designed-out\|masked\|propagated` w/ rationale) — behind the architecture's fixed seam interface | algorithm · concurrency · errors |

(+ ADRs → `adr/ADR-IMPL-NNN.md`)
*(DERIVED & regenerate-only)*
Consumes: the module's seam interface + role + dependency direction (from the architecture), and the slice it serves.

## Excludes
the module map · `role:` · dependency direction · seam interfaces · key sequences (→ the architecture — fixed before code) · actual code & heavy pseudocode · designing modules no slice touches yet

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md`
- Worked example: `examples.md`
