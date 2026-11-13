---
name: prototype
description: >-
  Build a throwaway prototype to answer one open question empirically — a runnable terminal app for state or logic, or toggleable UI variations for design. Use when running code settles it better than discussing. Loads the shared exec engine.
disable-model-invocation: true
argument-hint: an open question to prototype
---

# prototype

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill builds a throwaway spike that answers one question by running code. It is the path for an unknown that asking cannot settle and engineering merit cannot decide. The spike is outside the engine's test-first and production-code rules, because none of it ships: only the answer is kept.

## Process
1. **Frame the question and name its kind.** The kind decides the shape of the spike, so a wrong label wastes it.

   | Kind | The question | The spike |
   |---|---|---|
   | feasibility | can it be built, will it perform | a small interactive terminal app that pushes the state machine, rule or algorithm through its hard cases |
   | usability | can a user operate it, which direction is better | several clearly different variations on one route, switchable in place (a URL parameter and a floating switcher, for example) |
   | desirability | do the target users want it | a minimal artifact put in front of real target users, whose reactions are observed; your own judgment of it is not the answer |

   When several unknowns stack up, spike the riskiest first: the one that ends the idea if it turns out wrong.
2. **Build the least that answers it.** One command to run, state held in memory, the state shown after every action or variant, and a name that says it is a prototype. Tests, abstractions, persistence and polish add nothing to the answer.
3. **Widen the method when one spike cannot settle it.** A design direction that stays open after toggleable variations is better served by a structured round with users (sketch alternatives, pick, prototype, test) than by growing the spike.
4. **Record the answer, then delete the code.** Prototype code has none of the structure or tests production code needs, so it is not promoted: the real implementation is built test-first from the answer.

This is different from the kept UI prototype a UI slice builds against (`generate-ui-prototype`): that one is a maintained reference rendered from the design system; this one is disposable.

## Output
The spike lives in `prototypes/<question>/`, outside the source tree and outside `spec/`, until its answer is recorded. The answer goes where its kind of fact lives:

| Answer | Goes to |
|---|---|
| a verdict on a product bet or assumption | the discovery or product area that owns the bet |
| a UX direction | `08-ux/` |
| a load-bearing technical verdict | an ADR (`adr/ADR-PROTO-NNN.md`) |
| a decision the build needs (a state machine, a reducer shape, a schema) | the spec area that owns it, or the design note of the task that implements it |

Reads: the question, and the spec passages and code it concerns.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
