---
name: prototype
description: >-
  Build a throwaway prototype to answer ONE open question empirically — a runnable terminal app for state/logic, or toggleable UI variations for design. Use when running code settles it better than discussing. Loads the shared exec core.
disable-model-invocation: true
argument-hint: an open question to prototype
---

# prototype

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill: **a throwaway spike that answers ONE question empirically**.

## Process
1. **Frame the question — name which kind it is: feasibility | usability | desirability.** A prototype is the empirical path for an unknown that asking can't settle and merit can't decide. *Feasibility* = can it be built / will it perform; *usability* = can a user operate it; *desirability* = do target users actually want it. When several unknowns stack up, **spike the riskiest assumption first** — the one that kills the idea if it's wrong. Reach for a prototype when running beats discussing.
2. **Pick the branch (the question decides the shape).** Feasibility/state → a tiny interactive terminal app that pushes the state machine / business rule through the hard cases. Usability/UI-direction → several *radically different* variations on one route, toggleable (e.g. a URL param + a floating switcher). Desirability → **test with N target users**: put a minimal artifact in front of real users and observe, don't self-judge. Getting the branch wrong wastes the prototype.
3. **Escalate when one spike isn't enough.** If a single toggleable-variations spike can't settle it, run the structured **multi-day design-sprint** shape (map → sketch → decide → prototype → test with users) rather than sprawling the throwaway.
4. **Record the answer, then delete the code** (see Output for where the answer lands by question type).

## Rules
- Throwaway from day one and clearly named as a prototype; one command to run; no persistence (state in memory); skip polish (no tests/abstractions/error-handling beyond runnable); surface the state after every action/variant.
- **The prototype is deleted — only the answer persists.** Never ship prototype code as production.
- Not a kept mockup and not production UI; production wireframes / a design system are out of scope (UX *requirements* are owned elsewhere, not visual design).

## Output
The prototype code lands in `prototypes/<question>/` (never `src/`, never `spec/`) and is **throwaway — the prototype is deleted once the answer is recorded; only the answer persists**, routed by question type:

| Answer | Goes to |
|---|---|
| a recorded verdict and/or bet-status update | discovery / the owning area |
| a UX-direction verdict | `05-req-nonfunctional/ux/` |
| a load-bearing technical verdict | an ADR (`adr/ADR-PROTO-NNN.md`) |
| a decision-encoding snippet (state machine/reducer/schema) | inlined into the `T-NNN` manifest |

Consumes: the work item it operates on, plus the spec IDs / code it references.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
