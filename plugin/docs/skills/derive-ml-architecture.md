# derive-ml-architecture — user guide

**Invoke:** `/derive-ml-architecture`  (plugin: `/grillspec:derive-ml-architecture`)

*Derivation skill — it generates an artifact from recorded input (no interview).*

## What it does
Derive the ML/AI system design from the ML requirements — model serving, the evaluation harness, the training/feedback (or prompt/retrieval) pipeline, drift & quality monitoring, guardrails, and model/prompt versioning. Use when an ML/LLM capability's requirements are settled and you need its system architecture derived.

## What it needs (input)
The **recorded source artifacts** — it derives from them and does **not** interview you for facts. Standalone, place those artifacts in the working-root folders (or hand them in); a missing fact is recorded as a gap, never invented.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:derive-ml-architecture`
- **Standalone:** copy the `derive-ml-architecture/` folder into `~/.claude/skills/`, then run `/derive-ml-architecture`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
